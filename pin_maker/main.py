from fastapi import FastAPI
from pin_maker.api.routes import routes

app = FastAPI(debug=True)

app.include_router(routes)
