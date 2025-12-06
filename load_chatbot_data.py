import csv
import sqlite3

conn = sqlite3.connect("backend/database/chatbot_data.db")
cursor = conn.cursor()

with open("data/chatbot_data.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # başlığı atla
    for row in reader:
        question, answer = row
        cursor.execute("INSERT INTO chatbot_data (question, answer) VALUES (?, ?)", (question, answer))

conn.commit()
conn.close()
print("✅ Chatbot verileri başarıyla yüklendi.")
