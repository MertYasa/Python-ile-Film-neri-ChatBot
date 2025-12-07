from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import os

router = APIRouter()

# İstek modeli (JSON body)
class RecommendRequest(BaseModel):
    genre: str
    min_year: int = 2000
    min_rating: float = 7.0

# Cevapta kullanacağımız film modeli
class Movie(BaseModel):
    title: str
    year: int
    rating: float

class RecommendResponse(BaseModel):
    recommended_movies: list[Movie]


def get_db_path() -> str:
    """
    movies.db dosyasına, dosyanın konumuna göre
    güvenli şekilde ulaş.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))      # .../backend/api
    backend_dir = os.path.dirname(current_dir)                    # .../backend
    db_path = os.path.join(backend_dir, "database", "movies.db")  # .../backend/database/movies.db
    return db_path


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
    db_path = get_db_path()

    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="movies.db veritabanı bulunamadı.")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, year, rating FROM movies 
            WHERE genre LIKE ? AND year >= ? AND rating >= ? 
            ORDER BY rating DESC
            """,
            (f"%{request.genre}%", request.min_year, request.min_rating),
        )
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Veritabanı hatası: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

    movies = [
        Movie(title=row[0], year=row[1], rating=row[2])
        for row in rows
    ]

    return RecommendResponse(recommended_movies=movies)
