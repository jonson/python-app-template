import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.repository.widget import WidgetRepository
from app.service.widget import create_widget


from ..deps import uow
from ...uow import UnitOfWork

router = APIRouter()


class WidgetCreate(BaseModel):
    name: str


@router.get("/")
async def _index(request: Request, uow: UnitOfWork = Depends(uow)):
    return "Hello World"


@router.get("/widgets/{id}")
async def _get_widget(id: uuid.UUID, uow: UnitOfWork = Depends(uow)):
    widget = await uow[WidgetRepository].get_by_id(id)
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@router.post("/widgets")
async def _create_widget(widget_data: WidgetCreate, uow: UnitOfWork = Depends(uow)):
    widget = await create_widget(uow, widget_data.name)
    return widget
