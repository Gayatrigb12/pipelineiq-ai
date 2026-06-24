// import { useEffect, useRef, useState } from "react";
// import { askQuestion } from "../api/api";

// const ROLE = { USER: "user", AI: "ai" };

// const SUGGESTIONS = [
//   "Which deals are at risk of stalling?",
//   "Summarise all deals in the negotiation stage.",
//   "Who owns the highest-value deal?",
//   "Which industries have the most open deals?",
// ];

// export default function Chat() {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);
//   const bottomRef = useRef(null);
//   const inputRef = useRef(null);

//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages, loading]);

//   const sendMessage = async (question) => {
//     const text = (question || input).trim();
//     if (!text || loading) return;

//     setMessages((prev) => [...prev, { role: ROLE.USER, text }]);
//     setInput("");
//     setLoading(true);

//     try {
//       const res = await askQuestion(text);
//       setMessages((prev) => [
//         ...prev,
//         { role: ROLE.AI, text: res.answer },
//       ]);
//     } catch (err) {
//       setMessages((prev) => [
//         ...prev,
//         { role: ROLE.AI, text: `⚠️ ${err.message}`, error: true },
//       ]);
//     } finally {
//       setLoading(false);
//       setTimeout(() => inputRef.current?.focus(), 50);
//     }
//   };

//   const handleKeyDown = (e) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   };

//   const isEmpty = messages.length === 0;

//   return (
//     <div className="chat-page">
//       {/* Header */}
//       <header className="page-header chat-header">
//         <div>
//           <h1 className="page-title">AI Chat</h1>
//           <p className="page-subtitle">Ask anything about your deal pipeline.</p>
//         </div>
//         {messages.length > 0 && (
//           <button
//             className="btn btn--ghost btn--sm"
//             onClick={() => setMessages([])}
//           >
//             Clear chat
//           </button>
//         )}
//       </header>

//       {/* Message list */}
//       <div className="chat-messages">
//         {isEmpty && (
//           <div className="chat-empty">
//             <div className="chat-empty-icon">🤖</div>
//             <p className="chat-empty-title">PipelineIQ is ready</p>
//             <p className="chat-empty-sub">
//               Ask a question about your deals, or try one of these:
//             </p>
//             <div className="chat-suggestions">
//               {SUGGESTIONS.map((s) => (
//                 <button
//                   key={s}
//                   className="suggestion-chip"
//                   onClick={() => sendMessage(s)}
//                 >
//                   {s}
//                 </button>
//               ))}
//             </div>
//           </div>
//         )}

//         {messages.map((msg, i) => (
//           <div
//             key={i}
//             className={
//               "chat-bubble-row" +
//               (msg.role === ROLE.USER ? " chat-bubble-row--user" : "")
//             }
//           >
//             <div
//               className={
//                 "chat-avatar" +
//                 (msg.role === ROLE.USER
//                   ? " chat-avatar--user"
//                   : " chat-avatar--ai")
//               }
//             >
//               {msg.role === ROLE.USER ? "U" : "⚡"}
//             </div>
//             <div
//               className={
//                 "chat-bubble" +
//                 (msg.role === ROLE.USER
//                   ? " chat-bubble--user"
//                   : " chat-bubble--ai") +
//                 (msg.error ? " chat-bubble--error" : "")
//               }
//             >
//               {msg.text}
//             </div>
//           </div>
//         ))}

//         {loading && (
//           <div className="chat-bubble-row">
//             <div className="chat-avatar chat-avatar--ai">⚡</div>
//             <div className="chat-bubble chat-bubble--ai chat-bubble--typing">
//               <span className="typing-dot" />
//               <span className="typing-dot" />
//               <span className="typing-dot" />
//             </div>
//           </div>
//         )}

//         <div ref={bottomRef} />
//       </div>

//       {/* Input */}
//       <div className="chat-input-bar">
//         <textarea
//           ref={inputRef}
//           className="chat-input"
//           rows={1}
//           placeholder="Ask about your pipeline…"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={handleKeyDown}
//           disabled={loading}
//         />
//         <button
//           className="btn btn--primary chat-send-btn"
//           onClick={() => sendMessage()}
//           disabled={!input.trim() || loading}
//         >
//           {loading ? "…" : "Send"}
//         </button>
//       </div>
//     </div>
//   );
// }

import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api/api";

const ROLE = { USER: "user", AI: "ai" };

const SUGGESTIONS = [
  "Which deals are at risk of stalling?",
  "Summarise all deals in the negotiation stage.",
  "Who owns the highest-value deal?",
  "Which industries have the most open deals?",
];

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

 useEffect(() => {
  const saved = localStorage.getItem("pipelineiq_chat");

  if (saved) {
    try {
      const parsed = JSON.parse(saved);

      // keep only last 10
      setMessages(parsed.slice(-10));
    } catch {
      console.error("Invalid chat history");
      localStorage.removeItem("pipelineiq_chat");
    }
  }
}, []);

useEffect(() => {
  if (messages.length > 0) {
    const trimmed = messages.slice(-10);
    localStorage.setItem("pipelineiq_chat", JSON.stringify(trimmed));
  }
}, [messages]);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (question) => {
    const text = (question || input).trim();
    if (!text || loading) return;

    const userMessage = { role: ROLE.USER, text };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await askQuestion(text);

      const aiMessage = {
        role: ROLE.AI,
        text: res.answer,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: ROLE.AI,
          text: `⚠️ ${err.message}`,
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem("pipelineiq_chat");
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-page">
      {/* Header */}
      <header className="page-header chat-header">
        <div>
          <h1 className="page-title">AI Chat</h1>
          <p className="page-subtitle">
            Ask anything about your deal pipeline.
          </p>
        </div>

        {messages.length > 0 && (
          <button className="btn btn--ghost btn--sm" onClick={clearChat}>
            Clear chat
          </button>
        )}
      </header>

      {/* Messages */}
      <div className="chat-messages">
        {isEmpty && (
          <div className="chat-empty">
            <div className="chat-empty-icon">🤖</div>
            <p className="chat-empty-title">PipelineIQ is ready</p>
            <p className="chat-empty-sub">
              Ask a question about your deals, or try one of these:
            </p>

            <div className="chat-suggestions">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className="suggestion-chip"
                  onClick={() => sendMessage(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={
              "chat-bubble-row" +
              (msg.role === ROLE.USER ? " chat-bubble-row--user" : "")
            }
          >
            <div
              className={
                "chat-avatar" +
                (msg.role === ROLE.USER
                  ? " chat-avatar--user"
                  : " chat-avatar--ai")
              }
            >
              {msg.role === ROLE.USER ? "U" : "⚡"}
            </div>

            <div
              className={
                "chat-bubble" +
                (msg.role === ROLE.USER
                  ? " chat-bubble--user"
                  : " chat-bubble--ai") +
                (msg.error ? " chat-bubble--error" : "")
              }
            >
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-bubble-row">
            <div className="chat-avatar chat-avatar--ai">⚡</div>
            <div className="chat-bubble chat-bubble--ai chat-bubble--typing">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="chat-input-bar">
        <textarea
          ref={inputRef}
          className="chat-input"
          rows={1}
          placeholder="Ask about your pipeline…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />

        <button
          className="btn btn--primary chat-send-btn"
          onClick={() => sendMessage()}
          disabled={!input.trim() || loading}
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}