from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import Base, engine
from .routers import notes


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes API",
    version="1.0.0",
    description=(
        "A small CRUD API for text notes with tags, keyword/tag search, "
        "and API-key authentication.Set the key in the `X-API-Key` header."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    first = exc.errors()[0] if exc.errors() else None
    if first:
        location = " -> ".join(str(p) for p in first["loc"] if p != "body")
        detail = f"{location}: {first['msg']}" if location else first["msg"]
    else:
        detail = "Invalid request."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail},
    )


@app.get("/health", tags=["meta"], summary="Health check")
def health():
    return {"status": "ok"}


app.include_router(notes.router)
