# P4.3 - Aplicación: Producto

## Plataforma y Tecnologías Utilizadas

Nuestro proyecto del Cazador de Ofertas está construido sobre una arquitectura moderna basada en la separación del cliente y el servidor (Frontend y Backend), utilizando las siguientes herramientas:

### Frontend
- React.js
- Tailwind CSS

### Backend
- Python 3.
- FastAPI (para un rápido despliegue y ejecución de APIs) 
- Uvicorn 
- Procesamiento Numérico: Pandas y NumPy (para la manipulación y análisis de datos obtenidos)
- Scraping: Procesos de recolección de información que se ejecutan en paralelo contra tiendas populares como Amazon o MercadoLibre.

---

## Requerimientos de Ejecución

Para poner en marcha de manera local tanto el ambiente de desarrollo como los servicios backend, se necesita el siguiente entorno:

### Requisitos de Software
- **Node.js** (v16.x o superior) junto con su gestor de paquetes **npm** (o **yarn** / **pnpm**) para levantar el servidor de desarrollo del Frontend.
- **Python** (v3.8 o superior) junto con **pip** para el entorno del Backend.
- Se recomienda fuertemente el uso de un entorno virtual (`venv` o `conda`) para la instalación de dependencias listadas en el `requirements.txt`.
- Navegador Web moderno (Google Chrome, Mozilla Firefox, Safari o Brave).

### Requisitos de Hardware
- **Procesador:** CPU Dual-Core o superior
- **Memoria RAM:** Mínimo 4 GB (Recomendado 8 GB)
- **Almacenamiento:** Alrededor de 1 GB de espacio libre para alojar las carpetas generadas de dependencias (`node_modules` y `venv`).
- **Conectividad:** Conexión a Internet activa y estable, obligatoria para que el backend pueda acceder y minar los datos de las tiendas online.

---

## Algoritmo Elegido: TOPSIS

Para el proceso de ranking y toma de decisiones, el proyecto hace uso del algoritmo **TOPSIS** (*Technique for Order of Preference by Similarity to Ideal Solution*).

El algoritmo es un método de toma de decisiones multicriterio que clasifica las diferentes alternativas buscando la distancia más corta hacia la "solución ideal positiva" y la más lejana respecto a la "solución ideal negativa". En el proyecto, el algoritmo evalúa:
1. **Precio** (Buscando siempre minimizar).
2. **Velocidad de Entrega / Días** (Buscando siempre minimizar).
3. **Reputación del Vendedor / Rating** (Buscando maximizar).
4. **Cashback / Promociones** (Buscando maximizar).

### Conclusión y Proceso de Puesta en Marcha del Algoritmo

La elección del algoritmo TOPSIS es acertada para un sistema como nuestro Cazador de Ofertas, ya que un usuario difícilmente basa su decisión de compra únicamente en el precio absoluto; elementos como la confianza en el vendedor o la urgencia del envío son determinantes.

**Proceso de Puesta en Marcha:**
El proceso de integración e inicio se desarrolló de forma limpia aislando la lógica matemática en el archivo `backend/topsis.py`. 
1. **Recolección:** La aplicación recibe la solicitud del usuario desde el Frontend y extrae los productos en paralelo.
2. **Preparación y Normalización:** Se estructuran los datos crudos en un DataFrame de Pandas. Los pesos, controlados dinámicamente desde el React (`App.jsx`), son recibidos por la API y son normalizados para que su sumatoria represente correctamente los impactos.
3. **Cálculo de Distancias y Ranking:** El script calcula las soluciones ideales (las mejores y peores características encontradas en las tiendas) y mide mediante distancias euclidianas el desempeño de cada producto.
