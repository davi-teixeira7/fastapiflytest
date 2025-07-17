from typing import List, Dict, Any, Tuple, Optional
from sqlmodel import Session, select, or_, and_, func
from datetime import datetime, date
import uuid
from Entities.Event import Event, EventView, EventRegistration 

class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_events(self) -> List[Event]:
        try:
            statement = select(Event).order_by(Event.start_date.desc())
            events = self.session.exec(statement).all()
            return events
        except Exception as e:
            print(f"Error fetching all events: {e}")
            return []

    def get_filtered_events(
        self,
        filters: Dict[str, Any],
        page: int,
        page_size: int,
        sort_by: Optional[str] = None
    ) -> List[Event]:
        try:
            query = select(Event)
            conditions = []
            
            if 'event_type' in filters:
                conditions.append(Event.event_type == filters['event_type'])
            if 'pricing_type' in filters:
                conditions.append(Event.pricing_type == filters['pricing_type'])
            if 'location_uf' in filters:
                conditions.append(Event.location_uf.ilike(f"%{filters['location_uf']}%"))
            if 'category' in filters:
                conditions.append(Event.category.ilike(f"%{filters['category']}%"))
            
            if 'start_date_interval' in filters and 'end_date_interval' in filters:
                start_interval = filters['start_date_interval']
                end_interval = filters['end_date_interval']
                
                conditions.append(and_(Event.start_date >= start_interval, Event.start_date <= end_interval))
            
            if 'search_query' in filters and filters['search_query']:
                search_text = f"%{filters['search_query']}%"
                search_conditions = or_(
                    Event.name.ilike(search_text),
                    Event.summary.ilike(search_text),
                    Event.description.ilike(search_text)
                )
                conditions.append(search_conditions)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            if sort_by == 'date':
                query = query.order_by(Event.start_date.desc())
            elif sort_by == 'relevance' and 'search_query' in filters:
                search_term = filters['search_query']
                query = query.order_by(
                    func.lower(Event.name).contains(search_term.lower()).desc(),
                    func.lower(Event.summary).contains(search_term.lower()).desc(),
                    func.lower(Event.description).contains(search_term.lower()).desc()
                )
            elif sort_by == 'popularity':
                WEIGHT_REGISTRATION = 2
                query = (
                    query
                    .outerjoin(EventView, Event.id == EventView.event_id)
                    .outerjoin(EventRegistration, Event.id == EventRegistration.event_id)
                    .group_by(Event.id) 
                    .order_by(
                        (func.count(EventView.id) + (func.count(EventRegistration.id) * WEIGHT_REGISTRATION)).desc()
                    )
                )
            else: 
                query = query.order_by(Event.start_date.desc())
            
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            events = self.session.exec(query).all()
            return events
            
        except Exception as e:
            print(f"Error fetching filtered events: {e}")
            return []

    def count_filtered_events(self, filters: Dict[str, Any]) -> int:
        try:
            query = select(func.count(Event.id))
            conditions = []
            
            if 'event_type' in filters:
                conditions.append(Event.event_type == filters['event_type'])
            if 'pricing_type' in filters:
                conditions.append(Event.pricing_type == filters['pricing_type'])
            if 'location_uf' in filters:
                conditions.append(Event.location_uf.ilike(f"%{filters['location_uf']}%"))
            if 'category' in filters:
                conditions.append(Event.category.ilike(f"%{filters['category']}%"))
            
            if 'start_date_interval' in filters and 'end_date_interval' in filters:
                start_interval = filters['start_date_interval']
                end_interval = filters['end_date_interval']
                conditions.append(and_(Event.start_date >= start_interval, Event.start_date <= end_interval))

            if 'search_query' in filters and filters['search_query']:
                search_text = f"%{filters['search_query']}%"
                search_conditions = or_(
                    Event.name.ilike(search_text),
                    Event.summary.ilike(search_text),
                    Event.description.ilike(search_text)
                )
                conditions.append(search_conditions)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            count = self.session.exec(query).one()
            return count
        except Exception as e:
            print(f"Error counting filtered events: {e}")
            return 0