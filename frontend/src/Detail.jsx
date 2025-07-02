import React, { useState, useEffect, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Pie } from "react-chartjs-2";
import { Chart, ArcElement, Tooltip, Legend } from "chart.js";
import "./Detail.css";

Chart.register(ArcElement, Tooltip, Legend);

function Detail() {
  const navigate = useNavigate();
  const { video_id } = useParams();

  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sortType, setSortType] = useState("terbaru");

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/video?video_id=${video_id}`)
      .then((res) => res.json())
      .then((data) => {
        setVideo(Array.isArray(data.data) ? data.data[0] : data.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [video_id]);

  // Memoize comments agar tidak trigger warning eslint
  const comments = useMemo(
    () => (video && video.comment_analyzed ? video.comment_analyzed : []),
    [video]
  );

  const positif = comments.filter((c) => c.sentiment === "positif").length;
  const negatif = comments.filter((c) => c.sentiment === "negatif").length;
  const netral = comments.filter((c) => c.sentiment === "netral").length;
  const total = comments.length;
  const percentPos = total ? ((positif / total) * 100).toFixed(0) : 0;
  const percentNeg = total ? ((negatif / total) * 100).toFixed(0) : 0;
  const percentNet = total ? ((netral / total) * 100).toFixed(0) : 0;

  const pieData = useMemo(
    () => ({
      labels: ["Positif", "Negatif", "Netral"],
      datasets: [
        {
          data: [positif, negatif, netral],
          backgroundColor: ["#4caf50", "#f44336", "#888"],
          borderWidth: 1,
        },
      ],
    }),
    [positif, negatif, netral]
  );

  const sortedComments = useMemo(() => {
    if (sortType === "terbaru") {
      return [...comments].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    } else if (sortType === "positif") {
      return [...comments].filter((c) => c.sentiment === "positif");
    } else if (sortType === "negatif") {
      return [...comments].filter((c) => c.sentiment === "negatif");
    } else if (sortType === "netral") {
      return [...comments].filter((c) => c.sentiment === "netral");
    }
    return comments;
  }, [comments, sortType]);

  if (loading) {
    return <div className="loading">Memuat detail video...</div>;
  }
  if (!video) {
    return <div className="error">Data video tidak ditemukan.</div>;
  }

  return (
    <>
      <header className="site-header">
        <h1 className="site-title">Social Search🔍</h1>
      </header>

      <div className="detail-container">
        <div className="content">
          <div className="header">
            <button className="back-btn" onClick={() => navigate(-1)}>←</button>
            <h2 className="nickname">{video.nickname || video.author}</h2>
          </div>

          <p className="desc">{video.desc}</p>
          <p><strong>Tanggal Upload:</strong> {video.tanggal_upload || "-"}</p>
          <p><strong>Link Video:</strong> <a href={video.video_link} target="_blank" rel="noopener noreferrer">{video.video_link}</a></p>
          <p><strong>Total Komentar:</strong> {total}</p>

          <div className="sentiment-summary">
            <p><strong>Ringkasan Sentimen:</strong></p>
            <ul>
              <li>Positif: {positif} ({percentPos}%)</li>
              <li>Negatif: {negatif} ({percentNeg}%)</li>
              <li>Netral: {netral} ({percentNet}%)</li>
            </ul>
          </div>

          <div className="pie-chart-box">
            <Pie data={pieData} options={{ maintainAspectRatio: false }} />
          </div>

          <div className="sort-options">
            <label htmlFor="sort">Urutkan Komentar: </label>
            <select id="sort" value={sortType} onChange={(e) => setSortType(e.target.value)}>
              <option value="terbaru">Semua Komentar</option>
              <option value="positif">Sentimen Positif</option>
              <option value="negatif">Sentimen Negatif</option>
              <option value="netral">Sentimen Netral</option>
            </select>
          </div>

          <h3>Komentar Lengkap</h3>
          <div className="comment-box">
            {sortedComments.length === 0 ? (
              <div className="comment-item netral" style={{ color: "#888" }}>
                komentar kosong / komentar tidak termuat
              </div>
            ) : (
              sortedComments.map((c, i) => (
                <div key={i} className={`comment-item ${c.sentiment}`}>
                  <span className={`sentiment-label ${c.sentiment}`}>
                    {c.sentiment.toUpperCase()}
                  </span>
                  <p>{c.text}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <footer className="site-footer">
        <p>© 2025 Social Search</p>
      </footer>
    </>
  );
}

export default Detail;