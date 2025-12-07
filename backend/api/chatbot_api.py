from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from difflib import SequenceMatcher  # fuzzy benzerlik için

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


# --- Path helper'lar ---

def get_base_dirs():
    current_dir = os.path.dirname(os.path.abspath(__file__))      # .../backend/api
    backend_dir = os.path.dirname(current_dir)                    # .../backend
    db_dir = os.path.join(backend_dir, "database")                # .../backend/database
    return backend_dir, db_dir


def get_chatbot_db_path() -> str:
    _, db_dir = get_base_dirs()
    return os.path.join(db_dir, "chatbot_data.db")


def get_movies_db_path() -> str:
    _, db_dir = get_base_dirs()
    return os.path.join(db_dir, "movies.db")


# ---------- FILM ÖNERİ KISMI ----------

def detect_genre_from_message(message: str) -> str | None:
    text = message.lower()

    if "aksiyon" in text:
        return "Action"
    if "bilim kurgu" in text or "sci-fi" in text or "science fiction" in text:
        return "Sci-Fi"
    if "drama" in text:
        return "Drama"
    if "komedi" in text:
        return "Comedy"
    if "korku" in text:
        return "Horror"
    if "romantik" in text:
        return "Romance"

    return None


def build_movie_recommendation_text(genre_en: str) -> str | None:
    db_path = get_movies_db_path()
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="movies.db veritabanı bulunamadı.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, year, rating 
        FROM movies
        WHERE LOWER(genre) LIKE LOWER(?)
        ORDER BY rating DESC
        LIMIT 5
        """,
        (f"%{genre_en}%",),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    formatted = [f"{title} ({year}, {rating})" for (title, year, rating) in rows]

    genre_tr_map = {
        "Action": "aksiyon",
        "Sci-Fi": "bilim kurgu",
        "Drama": "drama",
        "Comedy": "komedi",
        "Horror": "korku",
        "Romance": "romantik",
    }
    genre_tr = genre_tr_map.get(genre_en, genre_en)

    return f"İşte sana bazı {genre_tr} film önerileri: " + ", ".join(formatted)


# ---------- CHATBOT + FUZZY EŞLEŞME ----------

def find_best_chatbot_answer(user_message: str, threshold: float = 0.6) -> str | None:
    """
    chatbot_data.db içindeki tüm sorulara bakıp
    kullanıcı mesajına en benzeyenini bulur.
    'threshold' benzerlik eşiğidir (0–1 arası).
    """
    db_path = get_chatbot_db_path()
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="chatbot_data.db bulunamadı.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chatbot_data")
    rows = cursor.fetchall()
    conn.close()

    user_lower = user_message.lower()
    best_ratio = 0.0
    best_answer = None

    for question, answer in rows:
        q_lower = (question or "").lower()
        ratio = SequenceMatcher(None, user_lower, q_lower).ratio()

        # İstersen burada basit bir keyword bonusu da eklenebilir
        if ratio > best_ratio:
            best_ratio = ratio
            best_answer = answer

    if best_ratio >= threshold:
        return best_answer

    return None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    user_message = request.message.strip()
    lower_msg = user_message.lower()

    # 1) Film isteği mi?
    is_movie_request = ("film" in lower_msg or "movie" in lower_msg) and (
        "öner" in lower_msg or "oner" in lower_msg or "recommend" in lower_msg
    )

    if is_movie_request:
        genre = detect_genre_from_message(user_message)
        if genre:
            movie_text = build_movie_recommendation_text(genre)
            if movie_text:
                return ChatResponse(answer=movie_text)
            else:
                return ChatResponse(
                    answer="Bu türde kayıtlı film bulamadım, farklı bir tür söylemek ister misin?"
                )
        else:
            return ChatResponse(
                answer="Tabii, hangi türde film istersin? (örneğin: aksiyon, bilim kurgu, komedi...)"
            )

    # 2) Normal sohbet: önce fuzzy eşleşme dene
    fuzzy_answer = find_best_chatbot_answer(user_message, threshold=0.6)
    if fuzzy_answer:
        return ChatResponse(answer=fuzzy_answer)

    # 3) Hâlâ yoksa fallback cevap
    return ChatResponse(
        answer="Bunu tam anlayamadım, başka bir şekilde sorabilir misin?"
    )
