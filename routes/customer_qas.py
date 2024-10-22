from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session

from database.connection import get_session
from models.events import Event, EventUpdate

event_router = APIRouter(
    tags=["CustomerQA"],
)

@event_router.get("/", response_model=List[Event])
async def get_events(session: Session = Depends(get_session)) -> List[Event]:
    statement = select(Event)
    events = session.exec(statement).all()
    return events


@event_router.get("/{id}", response_model=Event)
async def get_event(id: int, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found",
    )


@event_router.post("/", response_model=Event)
async def create_event(new_event: Event, session=Depends(get_session)) -> Event:
    session.add(new_event)
    session.commit()
    session.refresh(new_event)

    return new_event


@event_router.delete("/{id}")
async def delete_event(id: int, session: Session = Depends(get_session)) -> dict:
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
        return {
            'message': 'Event deleted',
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found",
    )


@event_router.delete("/")
async def delete_all_events() -> dict:
    events.clear()
    return {
        'message': 'All event deleted',
    }


@event_router.put("/{id}")
async def update_event(id: int, update_event: EventUpdate, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        event_data = update_event.model_dump(exclude_unset=True)
        for key, value in event_data.items():
            setattr(event, key, value)
        session.add(event)
        session.commit()
        session.refresh(event)

        return event
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found",
    )
