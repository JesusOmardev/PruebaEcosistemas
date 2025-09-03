from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core import config
from .core.errors import validation_exception_handler
from .api.v1.tasks import router as tasks_router
from .db.mongodb import connect, disconnect


app = FastAPI(title=config.APP_NAME)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


app.include_router(tasks_router, prefix=config.API_PREFIX)


@app.on_event("startup")
async def on_startup():
    await connect()


@app.on_event("shutdown")
async def on_shutdown():
    await disconnect()


# Handlers
from fastapi.exceptions import RequestValidationError
app.add_exception_handler(RequestValidationError, validation_exception_handler)