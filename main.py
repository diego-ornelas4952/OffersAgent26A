import asyncio
from src.agents.shopping_agent import ShoppingAgentService

async def main():
    service = ShoppingAgentService()
    
    print("--- Cazador de Ofertas AI ---")
    print("1. Añadir misión de monitoreo")
    print("2. Ejecutar monitoreo ahora")
    print("3. Iniciar bucle de monitoreo (cada hora)")
    
    choice = "2" # Simulación para esta demo
    
    if choice == "1":
        product = input("Nombre del producto: ")
        price = float(input("Precio objetivo: "))
        service.add_mission(product, price)
    elif choice == "2":
        # Asegurarnos de tener al menos una misión
        if not service.missions:
            service.add_mission("NVIDIA RTX 4060", 8000.0)
            service.add_mission("Sony WH-1000XM5", 5000.0)
        
        for m_id in service.missions:
            await service.check_mission(m_id)
    elif choice == "3":
        await service.run_monitoring_loop()

if __name__ == "__main__":
    asyncio.run(main())
