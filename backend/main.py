from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from scrapers import scrape_all
from topsis import topsis
import pandas as pd
import asyncio

app = FastAPI(title="Cazador de Ofertas API")

# Permisos CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pesos del usuario
class SearchWeights(BaseModel):
    price: float = Field(..., ge=0, le=1)
    delivery: float = Field(..., ge=0, le=1)
    reputation: float = Field(..., ge=0, le=1)
    cashback: float = Field(..., ge=0, le=1)

class SearchQuery(BaseModel):
    query: str
    weights: SearchWeights

@app.get("/")
async def root():
    return {"message": "Cazador de Ofertas API is running"}

@app.post("/search")
async def search_products(search: SearchQuery):
    # Scraping en paralelo
    products = await scrape_all(search.query)
    
    # Validar productos encontrados
    if not products or len(products) == 0:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron resultados para '{search.query}' en ninguna tienda. Intenta con un término más general."
        )
    
    print(f"Total de productos encontrados para ranking: {len(products)}")
    
    # Preparar datos TOPSIS
    df = pd.DataFrame(products)
    topsis_input = df[['price', 'delivery_days', 'reputation', 'cashback', 'relevance']]
    
    weights = [
        search.weights.price,
        search.weights.delivery,
        search.weights.reputation,
        search.weights.cashback,
        1.0
    ]
    
    # Normalizar pesos
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
        
    impacts = ['-', '-', '+', '+', '+']
    
    # Aplicar TOPSIS
    try:
        ranked_results = topsis(topsis_input, weights, impacts)
        # Combinar y retornar
        final_results = pd.concat([df[['store', 'name', 'url']], ranked_results], axis=1)
        return final_results.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing TOPSIS: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
