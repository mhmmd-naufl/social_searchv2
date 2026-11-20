import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FaSearch,
  FaArrowLeft,
  FaArrowRight,
  FaExternalLinkAlt,
  FaExclamationCircle,
  FaInbox,
  FaInfoCircle,
} from "react-icons/fa";
import "./Hasil.css";

const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "1";

const summarize = (item) => {
  const comments = item.comment_analyzed || [];
  const count = (sentiment) => comments.filter((c) => c.sentiment === sentiment).length;
  const positif = count("positif");
  const negatif = count("negatif");
  const netral = count("netral");
  const total = comments.length;
  const percent = (value) => (total ? Math.round((value / total) * 100) : 0);

  let dominant = "netral";
  if (total > 0) {
    if (positif >= negatif && positif >= netral) dominant = "positif";
    else if (negatif >= positif && negatif >= netral) dominant = "negatif";
  }

  return {
    total,
    positif,
    negatif,
    netral,
    persenPositif: percent(positif),
    persenNegatif: percent(negatif),
    persenNetral: percent(netral),
    dominant,
  };
};

const Hasil = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [error, setError] = useState(null);
  const [keywordFound, setKeywordFound] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const lastKeyword = sessionStorage.getItem("lastKeyword") || "";
    setKeyword(lastKeyword);
    setError(null);
    setKeywordFound(true);

    if (!lastKeyword) {
      setLoading(false);
      return undefined;
    }

    let cancelled = false;
    let timer;

    const poll = async (jobId) => {
      try {
        const response = await fetch(`${API_URL}/search/status/${jobId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const job = await response.json();
        if (cancelled) return;

        if (job.status === "done") {
          setResults(Array.isArray(job.data) ? job.data : []);
          setKeywordFound(job.keyword_found !== false);
          setLoading(false);
        } else if (job.status === "failed") {
          setError(job.error || "Scraping gagal. Silakan coba lagi.");
          setLoading(false);
        } else {
          timer = setTimeout(() => poll(jobId), 1500);
        }
      } catch {
        if (!cancelled) {
          setError("Gagal mengambil data dari server.");
          setLoading(false);
        }
      }
    };

    const start = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${API_URL}/search?keyword=${encodeURIComponent(lastKeyword)}`,
          { method: "POST" }
        );
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (cancelled) return;

        if (data.inline) {
          setResults(Array.isArray(data.data) ? data.data : []);
          setKeywordFound(data.keyword_found !== false);
          setLoading(false);
        } else {
          await poll(data.job_id);
        }
      } catch {
        if (!cancelled) {
          setError("Gagal mengambil data dari server.");
          setLoading(false);
        }
      }
    };

    start();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [attempt]);

  const handleDetail = (item) => {
    sessionStorage.setItem("detailVideo", JSON.stringify(item));
    navigate(`/detail/${item.video_id}`);
  };

  return (
    <>
      <header className="app-header">
        <div className="app-header-inner">
          <Link to="/" className="brand">
            <span className="brand-mark" aria-hidden="true">
              <FaSearch />
            </span>
            <span>Social Search</span>
          </Link>
          <Link to="/" className="ghost-link">
            <FaArrowLeft aria-hidden="true" /> Kembali
          </Link>
        </div>
      </header>

      <main className="results-page">
        <div className="results-head">
          <span className="eyebrow">HASIL PENCARIAN</span>
          <h1>
            {keyword ? (
              <>
                Untuk <span>“{keyword}”</span>
              </>
            ) : (
              "Pencarian"
            )}
          </h1>
          <p>
            {loading
              ? "Mencari video dan menganalisis komentar…"
              : `${results.length} video ditemukan`}
          </p>
        </div>

        {DEMO_MODE && (
          <p className="demo-note">
            <FaInfoCircle aria-hidden="true" />
            Mode demo — data yang ditampilkan adalah contoh hasil scraping, bukan hasil real-time.
            Detail lengkap ada di <a href="https://github.com/mhmmd-naufl/social_searchv2/blob/main/DATA_NOTICE.md" target="_blank" rel="noopener noreferrer">DATA_NOTICE.md</a>.
          </p>
        )}

        {!loading && !error && !keywordFound && results.length > 0 && (
          <p className="search-note" role="status">
            <FaInfoCircle aria-hidden="true" />
            Keyword <strong>“{keyword}”</strong> belum ada di database. Saat ini menampilkan
            data contoh yang tersedia — coba kata kunci lain untuk hasil yang lebih spesifik.
          </p>
        )}

        {loading && (
          <div className="skeleton-list" aria-label="Memuat hasil">
            {[0, 1, 2].map((index) => (
              <div className="skeleton-card" key={index}>
                <div className="skeleton-line short" />
                <div className="skeleton-line" />
                <div className="skeleton-line medium" />
                <div className="skeleton-line medium" />
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="state-card error" role="alert">
            <span className="state-icon">
              <FaExclamationCircle />
            </span>
            <h3>Pencarian gagal</h3>
            <p>{error}</p>
            <button type="button" className="primary-button" onClick={() => setAttempt((n) => n + 1)}>
              Coba lagi
            </button>
          </div>
        )}

        {!loading && !error && results.length === 0 && (
          <div className="state-card">
            <span className="state-icon">
              <FaInbox />
            </span>
            <h3>Belum ada hasil</h3>
            <p>Coba kata kunci lain atau gunakan ejaan yang lebih umum.</p>
            <Link to="/" className="primary-button">
              Ubah kata kunci
            </Link>
          </div>
        )}

        {!loading && !error && results.length > 0 && (
          <div className="result-list">
            {results.map((item) => {
              const stats = summarize(item);
              const preview = (item.comment_analyzed || []).slice(0, 4);

              return (
                <article className={`result-card ${stats.dominant}`} key={item.video_id}>
                  <div className="card-main">
                    <div className="card-top">
                      <div className="author">
                        <span className="avatar" aria-hidden="true">
                          {(item.author || "?").slice(0, 1).toUpperCase()}
                        </span>
                        <div>
                          <strong>@{item.author || "unknown"}</strong>
                          <small>Kata kunci: {item.keyword}</small>
                        </div>
                      </div>
                      <span className={`sentiment-badge ${stats.dominant}`}>
                        {stats.dominant}
                      </span>
                    </div>

                    <p className="desc">{item.desc}</p>

                    <a
                      className="video-link"
                      href={item.video_link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Lihat video di TikTok <FaExternalLinkAlt aria-hidden="true" />
                    </a>

                    <div className="comment-preview">
                      <span className="section-label">Komentar teratas</span>
                      {preview.length > 0 ? (
                        preview.map((comment, index) => (
                          <div key={index} className="comment-line">
                            <span className={`dot ${comment.sentiment}`} aria-hidden="true" />
                            <span className="comment-text">{comment.text}</span>
                            <span className={`comment-tag ${comment.sentiment}`}>
                              {comment.sentiment}
                            </span>
                          </div>
                        ))
                      ) : (
                        <p className="muted">Belum ada komentar yang termuat.</p>
                      )}
                    </div>

                    <button type="button" className="primary-button" onClick={() => handleDetail(item)}>
                      Lihat analisis lengkap <FaArrowRight aria-hidden="true" />
                    </button>
                  </div>

                  <aside className="card-stats">
                    <span className="stats-label">Ringkasan sentimen</span>
                    <strong className="stats-total">{stats.total}</strong>
                    <span className="stats-caption">komentar dianalisis</span>

                    <div
                      className="stacked-bar"
                      role="img"
                      aria-label={`Positif ${stats.persenPositif}%, negatif ${stats.persenNegatif}%, netral ${stats.persenNetral}%`}
                    >
                      <span className="segment positif" style={{ width: `${stats.persenPositif}%` }} />
                      <span className="segment negatif" style={{ width: `${stats.persenNegatif}%` }} />
                      <span className="segment netral" style={{ width: `${stats.persenNetral}%` }} />
                    </div>

                    <ul className="stats-legend">
                      <li>
                        <span className="dot positif" aria-hidden="true" />
                        Positif <b>{stats.positif} ({stats.persenPositif}%)</b>
                      </li>
                      <li>
                        <span className="dot negatif" aria-hidden="true" />
                        Negatif <b>{stats.negatif} ({stats.persenNegatif}%)</b>
                      </li>
                      <li>
                        <span className="dot netral" aria-hidden="true" />
                        Netral <b>{stats.netral} ({stats.persenNetral}%)</b>
                      </li>
                    </ul>
                  </aside>
                </article>
              );
            })}
          </div>
        )}
      </main>
    </>
  );
};

export default Hasil;
