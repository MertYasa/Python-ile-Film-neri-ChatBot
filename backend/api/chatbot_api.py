from fastapi import APIRouter, Form
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

router = APIRouter()

def get_response(user_input: str) -> str:
    # 🎯 Film türleri
    genres = {
        "aksiyon": "Action",
        "romantik": "Romantic",
        "komedi": "Comedy",
        "bilim kurgu": "Sci-Fi",
        "korku": "Horror",
        "dram": "Drama",
        "animasyon": "Animation",
        "gerilim": "Thriller",
        "macera": "Adventure"
    }

    # 🎯 Tür geçiyorsa film öner
    for tr_tur, en_tur in genres.items():
        if tr_tur in user_input.lower():
            try:
                res = requests.post("http://127.0.0.1:8000/api/recommend", params={
                    "genre": en_tur,
                    "min_year": 2000,
                    "min_rating": 7.0
                })
                data = res.json()
                movies = data.get("recommended_movies", [])

                if not movies:
                    return f"{tr_tur.title()} türünde uygun film bulunamadı."

                film_list = "\n".join([f"🎬 {f[0]} ({f[1]}) – ⭐ {f[2]}" for f in movies[:5]])
                return f"İşte bazı {tr_tur.title()} filmleri:\n{film_list}"

            except Exception:
                return "Film öneri servisine ulaşılamadı."

    # 🎯 Tür bulunamadıysa TF-IDF chatbot
    conn = sqlite3.connect("backend/database/chatbot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chatbot_data")
    data = cursor.fetchall()
    conn.close()

    if not data:
        return "Veritabanında kayıtlı soru bulunamadı."

    questions = [row[0] for row in data]
    answers = [row[1] for row in data]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(questions + [user_input])
    similarities = cosine_similarity(vectors[-1], vectors[:-1])
    best_match = similarities.max()

    if best_match < 0.2:
        return "Ne demek istediğini anlayamadım. Daha açık yazar mısın?"

    best_idx = similarities.argmax()
    return answers[best_idx]

@router.post("/chat")
def chat(user_input: str = Form(...)):
    yanit = get_response(user_input)
    return {"answer": yanit}
