from datetime import date
from typing import List, Optional, Dict, Any
from fastapi import Query, Depends, HTTPException, status
from sqlmodel import Session
from Services.EventService import EventService
from Repositories.EventRepository import EventRepository
from Entities.Event import Event, EventTypeEnum, PricingTypeEnum
from database import get_session

class EventController:
    def __init__(self, session: Session = Depends(get_session)):
        self.repository = EventRepository(session)
        self.service = EventService(self.repository)
    
    def list_events(
        self,
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
            None, description="String usada para filtrar a lista de eventos por tipo do evento."
        ), 
        filter_pricing: Optional[PricingTypeEnum] = Query(
            None, description="String usada para filtrar a lista de eventos por tipo de precificação."
        ),
        filter_interval_start: Optional[date] = Query(
            None, description="Data de início do intervalo para filtrar eventos (formato YYYY-MM-DD)."
        ),
        filter_interval_end: Optional[date] = Query(
            None, description="Data de término do intervalo para filtrar eventos (formato YYYY-MM-DD)."
        ),
        sort: Optional[str] = Query(
            None, description="String usada para ordenar a lista de eventos ('relevance', 'date' ou 'popularity')."
        )
    ) -> Dict[str, Any]:
        
        try:
            filters = {}
            if filter_type:
                filters["event_type"] = filter_type
            if filter_pricing:
                filters["pricing_type"] = filter_pricing
            if search:
                filters["search_query"] = search.strip()
            
            if filter_interval_start and filter_interval_end:
                if filter_interval_start > filter_interval_end:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "data": None,
                            "pagination": None,
                            "error": {
                                "code": "INVALID_QUERY_PARAMS",
                                "message": "A data de início do intervalo não pode ser maior que a data de término.",
                                "details": [
                                    {"field": "filter-interval-start", "message": "Data inválida"},
                                    {"field": "filter-interval-end", "message": "Data inválida"}
                                ]
                            }
                        }
                    )
                filters["start_date_interval"] = filter_interval_start.strftime('%Y-%m-%d')
                filters["end_date_interval"] = filter_interval_end.strftime('%Y-%m-%d')
            elif filter_interval_start or filter_interval_end:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "data": None,
                        "pagination": None,
                        "error": {
                            "code": "INVALID_QUERY_PARAMS",
                            "message": "Para usar o filtro por intervalo de data, 'filter-interval-start' e 'filter-interval-end' devem ser fornecidos juntos.",
                            "details": []
                        }
                    }
                )

            if sort and sort not in ["relevance", "date", "popularity"]:
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "data": None,
                        "pagination": None,
                        "error": {
                            "code": "INVALID_QUERY_PARAMS",
                            "message": "O parâmetro 'sort' deve ser 'relevance', 'date' ou 'popularity'.",
                            "details": [
                                {"field": "sort", "message": "Valor inválido"}
                            ]
                        }
                    }
                )

            result = self.service.get_events(filters, page, page_size, sort)

            if result["error"]:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"])
            
            return result
            
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail={
                    "data": None,
                    "pagination": None,
                    "error": {
                        "code": "SERVER_ERROR",
                        "message": f"Erro interno do servidor: {str(e)}"
                    }
                }
            )