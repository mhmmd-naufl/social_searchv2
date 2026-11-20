import React, { useState, useEffect, useRef } from "react";
import {
  FaSearch,
  FaArrowRight,
  FaHistory,
  FaCalendarAlt,
  FaClock,
  FaTrash,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import "./Home.css";

function App() {
  const [keyword, setKeyword] = useState("");
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [loading, setLoading] = useState(false);
  const historyRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setDate(
        now.toLocaleDateString("id-ID", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      );
      setTime(now.toLocaleTimeString("id-ID"));
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem("searchHistory") || "[]");
      setHistory(Array.isArray(stored) ? stored : []);
    } catch {
      setHistory([]);
    }
  }, []);

  // Tutup dropdown saat klik di luar area riwayat.
  useEffect(() => {
    if (!showHistory) return undefined;
    const handleOutside = (event) => {
      if (historyRef.current && !historyRef.current.contains(event.target)) {
        setShowHistory(false);
      }
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [showHistory]);

  const runSearch = (value) => {
    const trimmed = value.trim();
    if (!trimmed) return;

    setLoading(true);
    const updatedHistory = [trimmed, ...history.filter((item) => item !== trimmed)].slice(0, 5);
    localStorage.setItem("searchHistory", JSON.stringify(updatedHistory));
    setHistory(updatedHistory);

    sessionStorage.setItem("lastKeyword", trimmed);
    setShowHistory(false);
    navigate("/hasil");
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    runSearch(keyword);
  };

  const handleHistoryClick = (item) => {
    setKeyword(item);
    runSearch(item);
  };

  const clearHistory = () => {
    localStorage.removeItem("searchHistory");
    setHistory([]);
    setShowHistory(false);
  };

  return (
    <div className="home">
      <header className="home-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <FaSearch />
          </span>
          <span>Social Search</span>
        </div>

        <div className="history-wrap" ref={historyRef}>
          <button
            type="button"
            className="icon-button"
            onClick={() => setShowHistory((open) => !open)}
            aria-label="Tampilkan riwayat pencarian"
            aria-expanded={showHistory}
          >
            <FaHistory />
          </button>

          {showHistory && (
            <div className="history-menu" role="dialog" aria-label="Riwayat pencarian">
              <div className="history-menu-head">
                <span>Pencarian terakhir</span>
                {history.length > 0 && (
                  <button type="button" className="text-button" onClick={clearHistory}>
                    <FaTrash /> Hapus
                  </button>
                )}
              </div>
              {history.length === 0 ? (
                <p className="history-empty">Belum ada riwayat.</p>
              ) : (
                <ul className="history-list">
                  {history.map((item) => (
                    <li key={item}>
                      <button type="button" onClick={() => handleHistoryClick(item)}>
                        <FaHistory aria-hidden="true" />
                        <span>{item}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </header>

      <main className="hero">
        <span className="eyebrow">ANALISIS SENTIMEN KOMENTAR TIKTOK</span>
        <h1>
          Pahami audiens <span>dari setiap komentar.</span>
        </h1>
        <p className="hero-subtitle">
          Cari kata kunci, lalu lihat ringkasan sentimen video TikTok dalam satu halaman.
        </p>

        <form className="search-form" onSubmit={handleSubmit}>
          <FaSearch className="search-icon" aria-hidden="true" />
          <input
            type="text"
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="Contoh: banyuwangi, tetangga, kominfo"
            aria-label="Kata kunci pencarian"
            autoComplete="off"
          />
          <button type="submit" disabled={!keyword.trim() || loading}>
            {loading ? "Mencari…" : "Cari"}
            {!loading && <FaArrowRight aria-hidden="true" />}
          </button>
        </form>

        {history.length > 0 && (
          <div className="recent-searches">
            <span className="recent-label">Pencarian populer Anda</span>
            <div className="recent-chips">
              {history.slice(0, 4).map((item) => (
                <button type="button" key={item} onClick={() => handleHistoryClick(item)}>
                  {item}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="home-footer">
        <span>
          <FaCalendarAlt aria-hidden="true" /> {date}
        </span>
        <span className="footer-dot" aria-hidden="true">
          •
        </span>
        <span>
          <FaClock aria-hidden="true" /> {time}
        </span>
      </footer>
    </div>
  );
}

export default App;
