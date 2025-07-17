from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import enum
import uuid

class EventTypeEnum(str, enum.Enum):
    presencial = "presencial"
    online = "online"
    hibrido = "hibrido"  


class PricingTypeEnum(str, enum.Enum):
    gratis = "gratis"
    pago = "pago"  

class Event(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    summary: Optional[str] = None
    description: str = Field(nullable=False)
    start_date: datetime = Field(nullable=False)
    end_date: Optional[datetime] = None
    photo_url: Optional[str] = None
    location_city: str = Field(nullable=False)
    location_uf: str = Field(nullable=False)
    event_type: EventTypeEnum = Field(sa_column_kwargs={"nullable": False})
    pricing_type: PricingTypeEnum = Field(sa_column_kwargs={"nullable": False})
    category: str = Field(nullable=False)

    views: List["EventView"] = Relationship(back_populates="event")
    registrations: List["EventRegistration"] = Relationship(back_populates="event")

class EventView(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False)
    view_timestamp: datetime = Field(nullable=False)

    event: Event = Relationship(back_populates="views")

class EventRegistration(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False)
    registration_timestamp: datetime = Field(nullable=False)
    status: str = Field(nullable=False)
    payment_id: Optional[uuid.UUID] = None

    event: Event = Relationship(back_populates="registrations")