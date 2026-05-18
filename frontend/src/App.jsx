import React, { useState, useEffect } from 'react'

function App() {
  const [query, setQuery] = useState('')
  const [weights, setWeights] = useState({
    price: 0.4,
    delivery: 0.2,
    reputation: 0.2,
    cashback: 0.2
  })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleWeightChange = (e) => {
    const { name, value } = e.target
    const newValue = parseFloat(value) / 100
    setWeights(prev => ({
      ...prev,
      [name]: newValue
    }))
  }

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0)
  const isValidWeights = Math.abs(totalWeight - 1.0) < 0.001

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!isValidWeights) {
      setError("Los pesos deben sumar 100%")
      return
    }
    setLoading(true)
    setError(null)
    setResults([])

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          weights: weights
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error en el servidor backend');
      }

      const data = await response.json()
      // Sort results by rank before setting state
      const sortedData = data.sort((a, b) => a.rank - b.rank);
      setResults(sortedData)
    } catch (err) {
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('No se pudo conectar con el servidor. ¿Está corriendo el Backend en el puerto 8000?')
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const openInNewTab = (url) => {
    if (!url) {
      console.error("URL no disponible para este producto");
      return;
    }
    console.log("Abriendo URL:", url);
    const win = window.open(url, '_blank', 'noopener,noreferrer');
    if (win) win.focus();
  };

  return (
    <div className="min-h-screen bg-white text-gray-900 font-sans p-6 max-w-2xl mx-auto">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-light tracking-tight text-gray-800">
          Cazador de <span className="font-semibold">Ofertas</span>
        </h1>
        <p className="text-gray-500 text-sm mt-2">Ranking inteligente con TOPSIS</p>
      </header>

      <form onSubmit={handleSearch} className="space-y-6">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="¿Qué buscas hoy?"
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-400 transition-all"
            required
          />
        </div>

        <div className="bg-gray-50 p-6 rounded-xl border border-gray-100 space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-sm font-medium text-gray-700">Prioridades (Total: {(totalWeight * 100).toFixed(0)}%)</h2>
            {!isValidWeights && <span className="text-xs text-red-500">Debe sumar 100%</span>}
          </div>
          
          {[
            { id: 'price', label: 'Precio', value: weights.price },
            { id: 'delivery', label: 'Velocidad de Entrega', value: weights.delivery },
            { id: 'reputation', label: 'Reputación', value: weights.reputation },
            { id: 'cashback', label: 'Cashback / Promo', value: weights.cashback },
          ].map((slider) => (
            <div key={slider.id} className="space-y-1">
              <div className="flex justify-between text-xs text-gray-500">
                <span>{slider.label}</span>
                <span>{(slider.value * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                name={slider.id}
                min="0"
                max="100"
                step="5"
                value={slider.value * 100}
                onChange={handleWeightChange}
                className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-800"
              />
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading || !isValidWeights}
          className="w-full bg-gray-900 text-white py-3 rounded-lg font-medium hover:bg-black transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? 'Buscando...' : 'Encontrar Mejor Oferta'}
        </button>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-red-50 text-red-600 rounded-lg text-sm border border-red-100">
          {error}
        </div>
      )}

      {loading && (
        <div className="mt-12 flex flex-col items-center justify-center space-y-4">
          <div className="w-8 h-8 border-2 border-gray-200 border-t-gray-800 rounded-full animate-spin"></div>
          <p className="text-gray-400 text-sm">Escaneando tiendas en tiempo real...</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-12 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-800">Mejores Ofertas Encontradas</h2>
            <span className="text-xs text-gray-400">{results.length} resultados</span>
          </div>
          <div className="space-y-4">
            {results.map((item, index) => (
              <div
                key={index}
                className={`p-5 border rounded-xl transition-all shadow-sm hover:shadow-md ${
                  item.rank === 1 
                    ? 'border-emerald-200 bg-emerald-50/40 ring-1 ring-emerald-100' 
                    : 'border-gray-100 bg-white'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1 pr-4">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded ${
                        item.store === 'Amazon' ? 'bg-orange-100 text-orange-700' : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {item.store}
                      </span>
                      {item.rank === 1 && (
                        <span className="text-[10px] uppercase tracking-wider font-bold text-emerald-700 bg-emerald-200/50 px-1.5 py-0.5 rounded animate-pulse">
                          Opción Ganadora
                        </span>
                      )}
                    </div>
                    <h3 className="font-medium text-gray-900 leading-tight mb-1">{item.name}</h3>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-gray-900">${item.price.toLocaleString()}</p>
                    <div className="inline-block mt-1">
                       <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                         item.topsis_score > 0.7 ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'
                       }`}>
                         Score: {(item.topsis_score * 100).toFixed(1)}
                       </span>
                    </div>
                  </div>
                </div>
                
                <div className="mt-5 grid grid-cols-4 gap-2 text-center border-t border-gray-50 pt-4 items-center">
                  <div>
                    <p className="text-[9px] text-gray-400 uppercase font-semibold">Envío</p>
                    <p className="text-xs font-medium text-gray-700">{item.delivery_days === 1 ? 'Mañana' : `${item.delivery_days}d`}</p>
                  </div>
                  <div>
                    <p className="text-[9px] text-gray-400 uppercase font-semibold">Rating</p>
                    <p className="text-xs font-medium text-gray-700">{item.reputation}★</p>
                  </div>
                  <div>
                    <p className="text-[9px] text-gray-400 uppercase font-semibold">Rank</p>
                    <p className="text-xs font-bold text-gray-800">#{item.rank}</p>
                  </div>
                  <div className="flex justify-end">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] font-bold bg-gray-900 text-white px-3 py-1.5 rounded-md hover:bg-black transition-all active:scale-95 shadow-sm inline-block"
                    >
                      Ir a tienda
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
