import React, { useState, useRef, useEffect } from "react";

function SmartAssistant() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const chatEndRef = useRef(null);

  // Otomatik scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = { sender: "user", text: message };
    setChatHistory((prev) => [...prev, userMessage]);

    const formData = new URLSearchParams();
    formData.append("user_input", message);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      const botMessage = { sender: "bot", text: data.answer };
      setChatHistory((prev) => [...prev, botMessage]);
    } catch (error) {
      setChatHistory((prev) => [
        ...prev,
        { sender: "bot", text: "Sunucuya ulaşılamadı." },
      ]);
    }

    setMessage("");
  };

  return (
    <div className="max-w-xl mx-auto bg-white p-6 rounded-xl shadow-md mt-6">
      <h1 className="text-2xl font-bold mb-4 flex items-center gap-2">
        🤖 Akıllı Asistan
      </h1>

      {/* Mesaj kutusu */}
      <div className="chat-window">
        {chatHistory.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${
              msg.sender === "user" ? "user-bubble" : "bot-bubble"
            }`}
          >
            <span className="chat-text">{msg.text}</span>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Giriş ve Gönderme */}
      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Bir mesaj yazın..."
          className="p-2 border border-gray-300 rounded-md"
        />
        <button
          type="submit"
          className="bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition"
        >
          Gönder
        </button>
      </form>
    </div>
  );
}

export default SmartAssistant;
