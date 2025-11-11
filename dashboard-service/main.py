from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import aiohttp
import os

app = FastAPI(title="Dashboard Service")
templates = Jinja2Templates(directory="templates")

ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8001")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/data/summary")
async def get_summary_data():
    """Получаем данные из analytics service"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ANALYTICS_SERVICE_URL}/api/analytics/summary") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": "Failed to fetch data from analytics service"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}


@app.get("/api/data/events-by-type")
async def get_events_by_type():
    """Получаем данные о событиях по типам"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ANALYTICS_SERVICE_URL}/api/analytics/events-by-type") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": "Failed to fetch events data"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dashboard-service"}
