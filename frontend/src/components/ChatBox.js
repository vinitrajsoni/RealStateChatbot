import React, { useState } from "react";
import api from "../api";
import Message from "./Message";
import "./style.css";
import ProjectCard from "./ProjectCard";

function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!query.trim()) return;

    const newMessages = [...messages, { sender: "user", text: query }];
    setMessages(newMessages);
    setQuery("");
    setLoading(true);

    try {
      const res = await api.post("/chat", { query });
      const { summary, results } = res.data;

      setMessages([
        ...newMessages,
        { sender: "bot", text: summary, cards: results },
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { sender: "bot", text: "⚠️ Server error, please try again later." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index}>
            <Message sender={msg.sender} text={msg.text} />
            {msg.cards &&
              Array.isArray(msg.cards) &&
              msg.cards.map((card, i) => <ProjectCard key={i} data={card} />)}
          </div>
        ))}
        {loading && <p className="loading">Thinking...</p>}
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Ask something like: 3BHK in Pune under ₹1.2 Cr"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default ChatBox;
