from fastapi import APIRouter, Query
import sqlite3
import os

router = APIRouter()

@router.post("/recommend")
def recommend(
    genre: str = Query(...),
    min_year: int = Query(2000),
    min_rating: float = Query(7.0)
):
    db_path = os.path.join("backend", "database", "movies.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, year, rating FROM movies 
        WHERE genre LIKE ? AND year >= ? AND rating >= ? 
        ORDER BY rating DESC
    """, (f"%{genre}%", min_year, min_rating))
    movies = cursor.fetchall()
    conn.close()

    return {"recommended_movies": movies}
