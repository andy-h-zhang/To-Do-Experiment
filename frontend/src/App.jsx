import { useEffect, useState } from "react";

const api = (path, options = {}) =>
  fetch(path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

export default function App() {
  const [items, setItems] = useState([]);
  const [text, setText] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setError("");
    const res = await api("/api/todos");
    if (!res.ok) {
      setError("Could not load todos. Is the Flask server running?");
      return;
    }
    setItems(await res.json());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    const t = text.trim();
    if (!t) return;
    setError("");
    const res = await api("/api/todos", {
      method: "POST",
      body: JSON.stringify({ text: t }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.error || "Could not add todo.");
      return;
    }
    setText("");
    load();
  }

  async function toggle(id) {
    await api(`/api/todos/${id}`, { method: "PATCH" });
    load();
  }

  async function remove(id) {
    await api(`/api/todos/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <>
      <h1>Todo</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="New task…"
          aria-label="New task"
        />
        <button type="submit">Add</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
      {items.length === 0 && !error ? (
        <p className="muted">No tasks yet.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id}>
              <input
                type="checkbox"
                checked={item.done}
                onChange={() => toggle(item.id)}
                aria-label={`Done: ${item.text}`}
              />
              <span className={item.done ? "done" : ""}>{item.text}</span>
              <button
                type="button"
                className="secondary"
                onClick={() => remove(item.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
