import React, { useState, useEffect, useMemo } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { Pie } from "react-chartjs-2";
import {
  Chart,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import {
  FaSearch,
  FaArrowLeft,
  FaExternalLinkAlt,
  FaCalendarAlt,
  FaCommentDots,
  FaInfoCircle,
} from "react-icons/fa";
import "./Detail.css";

const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "1";

Chart.register(ArcElement, Tooltip, Legend);

const FILTERS = [
  { value: "terbaru", label: "Semua" },
  { value: "positif", label: "Positif" },
  { value: "negatif", label: "Negatif" },
  { value: "netral", label: "Netral" },
];

function Detail() {
  const navigate = useNavigate();
  const { video_id } = useParams();

  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sortType, setSortType] = useState("terbaru");

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/video?video_id=${video_id}`)
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setVideo(Array.isArray(data.data) ? data.data[0] : data.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [video_id]);

  const comments = useMemo(
    () => (video && video.comment_analyzed ? video.comment_analyzed : []),
    [video]
  );

  const positif = comments.filter((c) => c.sentiment === "positif").length;
  const negatif = comments.filter((c) => c.sentiment === "negatif").length;
  const netral = comments.filter((c) => c.sentiment === "netral").length;
  const total = comments.length;
  const percentPos = total ? Math.round((positif / total) * 100) : 0;
  const percentNeg = total ? Math.round((negatif / total) * 100) : 0;
  const percentNet = total ? Math.round((netral / total) * 100) : 0;

  let dominant = "netral";
  if (total > 0) {
    if (positif >= negatif && positif >= netral) dominant = "positif";
    else if (negatif >= positif && negatif >= netral) dominant = "negatif";
  }

  const pieData = useMemo(
    () => ({
      labels: ["Positif", "Negatif", "Netral"],
      datasets: [
        {
          data: [positif, negatif, netral],
          backgroundColor: ["#16a34a", "#dc2626", "#64748b"],
          borderWidth: 0,
          hoverOffset: 4,
        },
      ],
    }),
    [positif, negatif, netral]
  );

  const pieOptions = useMemo(
    () => ({
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111827",
          padding: 10,
          cornerRadius: 8,
        },
      },
      cutout: "68%",
    }),
    []
  );

  const visibleComments = useMemo(() => {
    if (sortType === "terbaru") return comments;
    return comments.filter((comment) => comment.sentiment === sortType);
  }, [comments, sortType]);

  if (loading) {
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
          </div>
        </header>
        <main className="detail-page">
          <div className="skeleton-card">
            <div className="skeleton-line short" />
            <div className="skeleton-line medium" />
            <div className="skeleton-line" />
          </div>
        </main>
      </>
    );
  }

  if (!video) {
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
          </div>
        </header>
        <main className="detail-page">
          <div className="state-card">
            <h3>Data video tidak ditemukan</h3>
            <p>Video mungkin sudah dihapus atau tautannya tidak valid.</p>
            <Link to="/" className="primary-button">
              Kembali ke pencarian
            </Link>
          </div>
        </main>
      </>
    );
  }

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
          <button type="button" className="ghost-link" onClick={() => navigate(-1)}>
            <FaArrowLeft aria-hidden="true" /> Kembali ke hasil
          </button>
        </div>
      </header>

      <main className="detail-page">
        {DEMO_MODE && (
          <p className="demo-note">
            <FaInfoCircle aria-hidden="true" />
            Mode demo — komentar berikut adalah contoh hasil scraping, bukan data real-time.
          </p>
        )}

        <div className="detail-grid">
          <section className="detail-primary">
            <div className="detail-card">
              <span className="eyebrow">DETAIL VIDEO</span>
              <h1>@{video.nickname || video.author || "unknown"}</h1>
              <p className="detail-desc">{video.desc}</p>

              <div className="meta-row">
                <span>
                  <FaCalendarAlt aria-hidden="true" /> {video.tanggal_upload || "Tanggal tidak tersedia"}
                </span>
                <span>
                  <FaCommentDots aria-hidden="true" /> {total} komentar
                </span>
              </div>

              <a
                className="video-link"
                href={video.video_link}
                target="_blank"
                rel="noopener noreferrer"
              >
                Buka di TikTok <FaExternalLinkAlt aria-hidden="true" />
              </a>
            </div>

            <div className="detail-card">
              <div className="comments-head">
                <div>
                  <span className="eyebrow">KOMENTAR</span>
                  <h2>Analisis lengkap</h2>
                </div>
                <span className="comments-count">{visibleComments.length} ditampilkan</span>
              </div>

              <div className="filter-pills" role="group" aria-label="Filter sentimen komentar">
                {FILTERS.map((filter) => (
                  <button
                    type="button"
                    key={filter.value}
                    className={sortType === filter.value ? "active" : ""}
                    aria-pressed={sortType === filter.value}
                    onClick={() => setSortType(filter.value)}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>

              {visibleComments.length === 0 ? (
                <p className="muted">Tidak ada komentar pada filter ini.</p>
              ) : (
                <div className="comment-list">
                  {visibleComments.map((comment, index) => (
                    <div key={index} className={`comment-item ${comment.sentiment}`}>
                      <span className={`dot ${comment.sentiment}`} aria-hidden="true" />
                      <p>{comment.text}</p>
                      <span className={`comment-tag ${comment.sentiment}`}>
                        {comment.sentiment}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          <aside className="detail-side">
            <div className="detail-card summary-card">
              <span className="eyebrow">RINGKASAN</span>
              <h2>Sentimen audiens</h2>

              <div className="pie-wrap">
                <Pie data={pieData} options={pieOptions} />
                <div className="pie-center">
                  <strong>{total}</strong>
                  <span>komentar</span>
                </div>
              </div>

              <div className={`dominant-badge ${dominant}`}>
                Dominan: <strong>{dominant}</strong>
              </div>

              <ul className="summary-legend">
                <li>
                  <span className="dot positif" aria-hidden="true" />
                  Positif
                  <b>
                    {positif} ({percentPos}%)
                  </b>
                </li>
                <li>
                  <span className="dot negatif" aria-hidden="true" />
                  Negatif
                  <b>
                    {negatif} ({percentNeg}%)
                  </b>
                </li>
                <li>
                  <span className="dot netral" aria-hidden="true" />
                  Netral
                  <b>
                    {netral} ({percentNet}%)
                  </b>
                </li>
              </ul>
            </div>
          </aside>
        </div>
      </main>
    </>
  );
}

export default Detail;
