from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from scrapers import scrape_all
from topsis import topsis
import pandas as pd
import asyncio

app = FastAPI(title="Cazador de Ofertas API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. You can restrict to ["http://localhost:5173"] later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # Fetch REAL data concurrently from all stores
    products = await scrape_all(search.query)
    
    # Check if we have at least one product from ANY store
    if not products or len(products) == 0:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron resultados para '{search.query}' en ninguna tienda. Intenta con un término más general."
        )
    
    # If we have products, proceed to TOPSIS ranking
    print(f"Total de productos encontrados para ranking: {len(products)}")
    
    # Prepare data for TOPSIS
    df = pd.DataFrame(products)
    # Criteria: Price (min), Delivery Days (min), Reputation (max), Cashback (max), Relevance (max)
    topsis_input = df[['price', 'delivery_days', 'reputation', 'cashback', 'relevance']]
    
    weights = [
        search.weights.price,
        search.weights.delivery,
        search.weights.reputation,
        search.weights.cashback,
        1.0 # Add a fixed high weight for relevance or make it dynamic
    ]
    
    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
        
    impacts = ['-', '-', '+', '+', '+']
    
    try:
        ranked_results = topsis(topsis_input, weights, impacts)
        # Merge back with store info
        final_results = pd.concat([df[['store', 'name', 'url']], ranked_results], axis=1)
        return final_results.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing TOPSIS: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
