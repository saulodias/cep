from fastapi import FastAPI, Query, HTTPException, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from search_cep import CEPSearcher

app = FastAPI(
    title="API de CEP Brasileiro",
    description="""
    API simples para consulta de CEPs (Códigos de Endereçamento Postal) brasileiros.
    
    Dois endpoints principais:
    * `/cep/{cep}` - Busca por número do CEP
    * `/search` - Busca geral por logradouro, cidade, bairro, etc.
    
    A busca geral utiliza full-text search com normalização para brasileiros,
    incluindo sinônimos de tipos de logradouro e normalização de números.
    """,
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substituir por origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz da API que redireciona para a documentação"""
    return FileResponse("index.html")

@app.get("/search.html")
async def search_page():
    """Serve uma página HTML simples com busca autocompletável"""
    return FileResponse("search.html")

@app.get("/cep/{cep}")
async def get_cep(cep: str):
    """
    Busca endereço pelo número do CEP
    
    Args:
        cep: Número do CEP (com ou sem formatação)
    
    Returns:
        Dados completos do endereço incluindo logradouro, bairro, cidade e estado
    """
    try:
        with CEPSearcher() as searcher:
            result = searcher.search_by_cep(cep)
            if not result:
                raise HTTPException(status_code=404, detail="CEP não encontrado")
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(
    q: str = Query(..., description="Termo de busca (logradouro, bairro, etc.)"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de resultados")
):
    """
    Busca geral de endereços com full-text search inteligente
    
    Suporta:
    - Sinônimos: "av" → "avenida", "r." → "rua", "blvd" → "boulevard"
    - Números: "28" ↔ "vinte e oito", "1ª" ↔ "primeira"
    - Variações: maiúsculas/minúsculas, acentos, abreviações
    
    Args:
        q: Termo de busca (ex: "Av. Paulista", "Rua 28", "Boulevard 1ª")
        limit: Limite de resultados (1-100)
    
    Returns:
        Lista de endereços encontrados ordenados por relevância
    """
    try:
        with CEPSearcher() as searcher:
            results = searcher.search_by_address(q, limit)
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 