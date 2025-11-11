from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from datetime import datetime
import os

app = FastAPI(title="Analytics Service")

# CORS для dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@postgres:5432/analytics")
engine = create_engine(DATABASE_URL)


@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Основные метрики аналитики"""
    try:
        with engine.connect() as conn:
            # Общее количество событий
            total_events = conn.execute(text("SELECT COUNT(*) FROM user_events")).scalar()

            # Уникальные пользователи
            unique_users = conn.execute(text("SELECT COUNT(DISTINCT user_id) FROM user_events")).scalar()

            # Самая популярная страница
            popular_page_result = conn.execute(
                text("SELECT page, COUNT(*) as count FROM user_events GROUP BY page ORDER BY count DESC LIMIT 1")
            ).first()

            return {
                "total_events": total_events or 0,
                "unique_users": unique_users or 0,
                "popular_page": popular_page_result[0] if popular_page_result else "No data",
                "popular_page_views": popular_page_result[1] if popular_page_result else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching analytics: {str(e)}"
        )


@app.get("/api/analytics/events-by-type")
async def get_events_by_type():
    """События по типам"""
    try:
        with engine.connect() as conn:
            events_by_type_result = conn.execute(
                text("SELECT event_type, COUNT(*) as count FROM user_events GROUP BY event_type")
            ).fetchall()

            return {
                "events_by_type": [
                    {"event_type": row[0], "count": row[1]}
                    for row in events_by_type_result
                ]
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching events by type: {str(e)}"
        )


@app.get("/api/analytics/recent-events")
async def get_recent_events(limit: int = 10):
    """Последние события"""
    try:
        with engine.connect() as conn:
            recent_events = conn.execute(
                text("SELECT user_id, event_type, page, timestamp FROM user_events ORDER BY timestamp DESC LIMIT :limit"),
                {"limit": limit}
            ).fetchall()

            return {
                "recent_events": [
                    {
                        "user_id": row[0],
                        "event_type": row[1],
                        "page": row[2],
                        "timestamp": row[3].isoformat() if row[3] else None
                    }
                    for row in recent_events
                ]
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching recent events: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
