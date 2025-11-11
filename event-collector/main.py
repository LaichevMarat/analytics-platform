from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI(title="Event Collector API")


# Модель данных для события
class UserEvent(BaseModel):
    user_id: str
    event_type: str  # page_view, add_to_cart, purchase
    page: str
    timestamp: datetime = None


# Настройка базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@postgres:5432/analytics")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Создаем таблицу
def create_tables():
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS user_events (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                page VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        conn.commit()


@app.on_event("startup")
async def startup():
    create_tables()


@app.post("/api/events")
async def collect_event(event: UserEvent):
    """Эндпоинт для сбора событий от пользователей"""
    try:
        if event.timestamp is None:
            event.timestamp = datetime.utcnow()

        with SessionLocal() as session:
            session.execute(
                text("INSERT INTO user_events (user_id, event_type, page, timestamp) VALUES (:user_id, :event_type, :page, :timestamp)"),
                {
                    "user_id": event.user_id,
                    "event_type": event.event_type,
                    "page": event.page,
                    "timestamp": event.timestamp
                }
            )
            session.commit()

        return {
            "status": "success",
            "message": "Event collected successfully",
            "event_id": event.user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error collecting event: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "event-collector"}


if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
