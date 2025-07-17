from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from typing import List, Optional, Dict, Any
from datetime import date
import uvicorn
from fastapi.responses import JSONResponse


from Entities.Event import Event, EventTypeEnum, PricingTypeEnum, EventView, EventRegistration # Import new models
from database import get_session, create_db_and_tables
from Controllers.EventController import EventController

# Configuração da aplicação
app = FastAPI(
    title="DARC Events API",
    description="API para gerenciamento de eventos do DARC",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de inicialização
@app.on_event("startup")
async def startup_event():
    """Cria as tabelas do banco de dados na inicialização"""
    create_db_and_tables()
    print("✅ Aplicação iniciada com sucesso!")

# Rotas da API
@app.get("/", tags=["Health"])
async def root():
    """Endpoint de saúde da API"""
    return {
        "message": "DarcFastAPI rodando!",
        "version": "v1.0",
    }

# Endpoints de eventos
@app.get("/events", tags=["Events"])
async def get_events_list(
    search: Optional[str] = Query(
        None, description="String usada para fazer uma busca na lista de eventos por nome, sumário ou descrição."
    ),
    page: int = Query(
        1, ge=1, description="Número da página na paginação da lista de eventos."
    ),
    page_size: int = Query(
        10, ge=1, le=100, description="Número de itens por página."
    ),
    filter_type: Optional[EventTypeEnum] = Query(
        None, description="String usada para filtrar a lista de eventos por tipo do evento, podendo ter os valores: online, in-person, hybrid."
    ), 
    filter_pricing: Optional[PricingTypeEnum] = Query(
        None, description="String usada para filtrar a lista de eventos por tipo de precificação, podendo ter os valores: free, paid."
    ),
    filter_interval_start: Optional[date] = Query(
        None, description="Data de início do intervalo para filtrar eventos (formato YYYY-MM-DD)."
    ),
    filter_interval_end: Optional[date] = Query(
        None, description="Data de término do intervalo para filtrar eventos (formato YYYY-MM-DD)."
    ),
    sort: Optional[str] = Query(
        None, description="String usada para ordenar a lista de eventos, podendo ter os valores: relevance, date, popularity."
    ),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Retorna a lista de eventos com opções de busca, filtros, ordenação e paginação.
    """
    controller = EventController(session)
    response = controller.list_events(
        search=search,
        page=page,
        page_size=page_size,
        filter_type=filter_type,
        filter_pricing=filter_pricing,
        filter_interval_start=filter_interval_start,
        filter_interval_end=filter_interval_end,
        sort=sort
    )
    return response

# Tratamento de erros
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Tratamento padronizado de erros HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Tratamento de erros gerais"""
    print(f"❌ Erro não tratado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "pagination": None,
            "error": {
                "code": "SERVER_ERROR",
                "message": "Erro interno do servidor",
                "details": []
            }
        }
    )

# Execução da aplicação
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )