from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core import config
from .core.errors import validation_exception_handler
from .api.v1.tasks import router as tasks_router
from .db.mongodb import connect, disconnect, ensure_indexes


app = FastAPI(title=config.APP_NAME)

# --- CORS DEV ---
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router, prefix=config.API_PREFIX)


@app.on_event("startup")
async def on_startup():
    await connect()
    await ensure_indexes()

@app.on_event("shutdown")
async def on_shutdown():
    await disconnect()


# Handlers
from fastapi.exceptions import RequestValidationError
app.add_exception_handler(RequestValidationError, validation_exception_handler)