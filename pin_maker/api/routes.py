from fastapi import APIRouter
from pin_maker.api.local_routes import api

routes = APIRouter()

routes.include_router(api.router, prefix='/api')
