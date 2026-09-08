import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.session import Base, engine
from app.api import (
    auth_router, upload_router, dashboard_router, products_router,
    customers_router, regions_router, forecast_router, anomalies_router,
    ai_router, recommendations_router,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sales-analytics")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")
    if not settings.ai_configured:
        logger.warning("LLM_API_KEY is not set -- AI Analyst will use data-grounded template answers "
                        "instead of LLM-generated explanations.")
    yield


app = FastAPI(
    title="AI-Powered Sales Analytics & Forecasting Platform",
    description="Analytics, ML forecasting, anomaly detection, and an AI Sales Analyst over your sales data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Never leak raw stack traces to the client
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})


@app.get("/health")
def health():
    return {"status": "ok", "ai_configured": settings.ai_configured}


app.include_router(auth_router.router)
app.include_router(upload_router.router)
app.include_router(dashboard_router.router)
app.include_router(products_router.router)
app.include_router(customers_router.router)
app.include_router(regions_router.router)
app.include_router(forecast_router.router)
app.include_router(anomalies_router.router)
app.include_router(ai_router.router)
app.include_router(recommendations_router.router)
