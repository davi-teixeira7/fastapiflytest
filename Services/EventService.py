from typing import List, Optional, Dict, Any
from Repositories.EventRepository import EventRepository
from Entities.Event import Event, EventTypeEnum, PricingTypeEnum
import math
from datetime import date, datetime

class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    def get_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            if filters is None:
                filters = {}

            validated_filters = self._validate_filters(filters)
            
            total_items = self.repository.count_filtered_events(validated_filters)
            
            events = self.repository.get_filtered_events(validated_filters, page, page_size, sort_by)

            total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
            
            pagination = {
                "currentPage": page,
                "totalPages": total_pages,
                "previousPage": page - 1 if page > 1 else None,
                "nextPage": page + 1 if page < total_pages else None,
                "totalItems": total_items,
            }

            return {
                "data": events,
                "pagination": pagination,
                "error": None
            }

        except Exception as e:
            print(f"Error in service when fetching events: {e}")
            return {
                "data": None,
                "pagination": None,
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Internal server error: {str(e)}"
                }
            }
            
    def get_events_by_type(self, event_type: EventTypeEnum, page: int = 1, page_size: int = 10, sort_by: Optional[str] = None) -> Dict[str, Any]:
        return self.get_events(filters={"event_type": event_type}, page=page, page_size=page_size, sort_by=sort_by)
        
    def get_events_by_pricing(self, pricing_type: PricingTypeEnum, page: int = 1, page_size: int = 10, sort_by: Optional[str] = None) -> Dict[str, Any]:
        return self.get_events(filters={"pricing_type": pricing_type}, page=page, page_size=page_size, sort_by=sort_by)

    def search_events(self, query: str, page: int = 1, page_size: int = 10, sort_by: Optional[str] = None) -> Dict[str, Any]:
        if not query or not query.strip():
            return {
                "data": [],
                "pagination": {
                    "currentPage": 1, "totalPages": 0, "previousPage": None, "nextPage": None, "totalItems": 0
                },
                "error": None
            }
        return self.get_events(filters={"search_query": query.strip()}, page=page, page_size=page_size, sort_by=sort_by)

    def _validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        validated = {}
        
        if 'event_type' in filters:
            if isinstance(filters['event_type'], EventTypeEnum):
                validated['event_type'] = filters['event_type']
            elif isinstance(filters['event_type'], str):
                try:
                    validated['event_type'] = EventTypeEnum(filters['event_type'])
                except ValueError:
                    pass 
                
        if 'pricing_type' in filters:
            if isinstance(filters['pricing_type'], PricingTypeEnum):
                validated['pricing_type'] = filters['pricing_type']
            elif isinstance(filters['pricing_type'], str):
                try:
                    validated['pricing_type'] = PricingTypeEnum(filters['pricing_type'])
                except ValueError:
                    pass 
                
        if 'search_query' in filters:
            query = filters['search_query']
            if isinstance(query, str) and query.strip():
                validated['search_query'] = query.strip()

        if 'start_date_interval' in filters and 'end_date_interval' in filters:
            start_date_str = filters['start_date_interval']
            end_date_str = filters['end_date_interval']
            try:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
                validated['start_date_interval'] = start_date_obj
                validated['end_date_interval'] = end_date_obj
            except ValueError:
                pass 
                
        return validated