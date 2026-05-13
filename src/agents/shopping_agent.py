import os
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any
from browser_use import Agent
from browser_use.llm import ChatGoogle
from pydantic import BaseModel

class ProductMission(BaseModel):
    id: str
    product_name: str
    target_price: float
    sites: list[str] = ["Amazon.com.mx"]
    last_check: Optional[datetime] = None
    last_price: Optional[float] = None
    status: str = "active"

class ProductData(BaseModel):
    price: float
    name: str
    coupon: Optional[str] = None
    seller_rating: Optional[str] = None

class ShoppingAgentService:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogle(model=model_name, temperature=0.0)
        self.missions_file = "missions.json"
        self.missions = self._load_missions()

    def _load_missions(self) -> Dict[str, ProductMission]:
        if os.path.exists(self.missions_file):
            with open(self.missions_file, 'r') as f:
                data = json.load(f)
                # Convertir fechas de string a datetime
                for k, v in data.items():
                    if v.get('last_check'):
                        v['last_check'] = datetime.fromisoformat(v['last_check'])
                return {k: ProductMission(**v) for k, v in data.items()}
        return {}

    def _save_missions(self):
        with open(self.missions_file, 'w') as f:
            json.dump({k: v.model_dump(mode='json') for k, v in self.missions.items()}, f, indent=4)

    def add_mission(self, product_name: str, target_price: float):
        mission_id = str(len(self.missions) + 1)
        mission = ProductMission(id=mission_id, product_name=product_name, target_price=target_price)
        self.missions[mission_id] = mission
        self._save_missions()
        return mission_id

    async def check_mission(self, mission_id: str):
        mission = self.missions.get(mission_id)
        if not mission:
            return None

        print(f"[*] Ejecutando misión {mission_id}: {mission.product_name} (Objetivo: ${mission.target_price})")
        
        # Optimizar la tarea para ir directo a los resultados y ahorrar pasos/tokens
        search_url = f"https://www.amazon.com.mx/s?k={mission.product_name.replace(' ', '+')}"
        task = (
            f"1. Navega a {search_url}\n"
            "2. Identifica el primer producto que NO sea patrocinado (sponsored).\n"
            "3. HAZ CLIC en ese producto para ver sus detalles.\n"
            "4. Extrae el NOMBRE y el PRECIO TOTAL (sin mensualidades).\n"
            "5. Devuelve un objeto JSON con las llaves exactas: 'price' (solo el número) y 'name' (texto)."
        )

        # Usar un modelo lite si está disponible para ahorrar cuota, o mantenerse en flash
        agent = Agent(
            task=task, 
            llm=self.llm,
            result_type=ProductData
        )
        
        try:
            history = await agent.run()
            
            # Buscar el resultado en el historial de forma flexible
            data = None
            
            # 1. Intentar con final_result
            final_result = history.final_result()
            print(f"DEBUG: Final result content: {final_result}")
            
            # 2. Buscar en todo el historial si final_result no es JSON válido
            all_contents = [final_result] if final_result else []
            for h in history.history:
                for action_result in h.result:
                    if action_result.extracted_content:
                        all_contents.append(action_result.extracted_content)
            
            for content in reversed(all_contents):
                if not content or not isinstance(content, str):
                    continue
                
                # Intentar encontrar un bloque JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        # Limpiar el JSON de posibles bloques markdown
                        json_str = json_match.group().strip()
                        potential_data = json.loads(json_str)
                        # Mapear llaves si el LLM usó nombres distintos
                        if 'nombre_producto' in potential_data:
                            potential_data['name'] = potential_data.pop('nombre_producto')
                        if 'precio_total' in potential_data:
                            potential_data['price'] = float(str(potential_data.pop('precio_total')).replace(',', ''))
                        
                        data = ProductData(**potential_data)
                        break
                    except Exception as e:
                        print(f"DEBUG: Intento de parseo fallido: {e}")
                        continue
            
            if data:
                final_price = data.price
                mission.last_price = final_price
                mission.last_check = datetime.now()
                self._save_missions()
                
                print(f"[i] Producto encontrado: {data.name}")
                if final_price <= mission.target_price:
                    print(f"[!!!] ¡OFERTA ENCONTRADA! {mission.product_name} está a ${final_price}")
                    return True
                else:
                    print(f"[i] El precio actual es ${final_price}. Aún por encima del objetivo.")
            else:
                print("[!] No se pudo extraer información estructurada del historial del agente.")
        except Exception as e:
            print(f"[!] Error durante la ejecución del agente: {e}")
        
        return False

    async def run_monitoring_loop(self, interval_seconds: int = 3600):
        print(f"[*] Iniciando bucle de monitoreo cada {interval_seconds} segundos...")
        while True:
            for m_id in list(self.missions.keys()):
                await self.check_mission(m_id)
                # Pequeña pausa entre misiones para no saturar
                await asyncio.sleep(5)
            await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    async def test():
        service = ShoppingAgentService()
        # Ejemplo: Buscar una RTX 4060 por menos de 8000 MXN
        m_id = service.add_mission("NVIDIA RTX 4060", 8000.0)
        await service.check_mission(m_id)

    asyncio.run(test())
