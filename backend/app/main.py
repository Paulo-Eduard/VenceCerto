"""API de demonstração do VenceCerto (sem banco, sem autenticação).

Rodar: uvicorn app.main:app --reload   ->  http://localhost:8000  (docs em /docs)
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from app.domain.insights import InsufficientHistoryError
from app.domain.pvps import InsufficientStockError
from app.services import demo

app = FastAPI(title="VenceCerto (demonstração)", version="0.1.0")
WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@app.exception_handler(InsufficientStockError)
async def _stock_error(_: Request, exc: InsufficientStockError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InsufficientHistoryError)
@app.exception_handler(ValueError)
async def _value_error(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/lots/classify")
def classify(data: demo.ClassifyIn) -> dict:
    return demo.classify(data)


@app.post("/api/v1/stock/pvps")
def pvps(data: demo.PvpsIn) -> dict:
    return demo.pvps(data)


@app.post("/api/v1/promotions/recommend")
def promotion(data: demo.PromoIn) -> dict:
    return demo.promotion(data)


@app.post("/api/v1/insights/reorder")
def reorder(data: demo.ReorderIn) -> dict:
    return demo.reorder(data)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")
