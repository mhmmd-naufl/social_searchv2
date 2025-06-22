import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./Hasil.css";

const Hasil = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    const lastKeyword = sessionStorage.getItem("lastKeyword") || "";
    setKeyword(lastKeyword);

    if (lastKeyword) {
      setLoading(true);
      fetch(`http://localhost:8000/search?keyword=${encodeURIComponent(lastKeyword)}`)
        .then((res) => res.json())
        .then((data) => {
          setResults(Array.isArray(data.data) ? data.data : []);
          setLoading(false);
        })
        .catch(() => {
          setError("Gagal mengambil data dari server.");
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  return (
    <>
      <header className="site-header">
        <h1 className="site-title">Social Search🔍</h1>
        <Link to="/" className="back-link">← Kembali ke Pencarian</Link>
      </header>

      <div className="container">
        {loading && <p className="loading">Sedang mencari data...</p>}
        {error && <p className="error">{error}</p>}

        {!loading && results.length === 0 && (
          <p className="no-result">Tidak ada hasil untuk "{keyword}".</p>
        )}

        <div className="result-list">
          {results.map((item) => {
            // Hitung statistik sentimen
            const total = item.comment_analyzed ? item.comment_analyzed.length : 0;
            const positif = item.comment_analyzed
              ? item.comment_analyzed.filter((c) => c.sentiment === "positif").length
              : 0;
            const negatif = item.comment_analyzed
              ? item.comment_analyzed.filter((c) => c.sentiment === "negatif").length
              : 0;
            const netral = item.comment_analyzed
              ? item.comment_analyzed.filter((c) => c.sentiment === "netral").length
              : 0;
            const persenPositif = total ? Math.round((positif / total) * 100) : 0;
            const persenNegatif = total ? Math.round((negatif / total) * 100) : 0;
            const persenNetral = total ? Math.round((netral / total) * 100) : 0;

            // Tentukan sentimen utama untuk border warna
            let mainSentiment = "netral";
            if (total === 0) {
              mainSentiment = "netral";
            } else if (positif >= negatif && positif >= netral) {
              mainSentiment = "positif";
            } else if (negatif >= positif && negatif >= netral) {
              mainSentiment = "negatif";
            } else if (netral >= positif && netral >= negatif) {
            mainSentiment = "netral";
            }

            return (
              <div
                className={`result-card ${mainSentiment}`}
                key={item.video_id}
              >
                <div className="card-content">
                  <div className="card-left">
                    <p className="desc"><strong>{item.desc}</strong></p>
                    <p>
                      <b>Author:</b> @{item.author}
                    </p>
                    <a href={item.video_link} target="_blank" rel="noopener noreferrer" className="video-url">
                      {item.video_link}
                    </a>
                    <p>
                      <b>Keyword:</b> {item.keyword}
                    </p>
                    <p className="komentar-label">💬 Komentar & Sentimen</p>
                    <ul className="comment-list">
                      {item.comment_analyzed &&
                        item.comment_analyzed.map((comment, idx) => (
                          <li key={idx} className={`comment-item ${comment.sentiment}`}>
                            "{comment.text}"{" "}
                            <span
                              style={{
                                color:
                                  comment.sentiment === "positif"
                                    ? "green"
                                    : comment.sentiment === "negatif"
                                    ? "red"
                                    : "gray",
                                fontWeight: "bold",
                              }}
                            >
                              ({comment.sentiment})
                            </span>
                          </li>
                        ))}
                    </ul>
                  </div>
                  <div className="card-right">
                    <h2 className="sentimen-title">{mainSentiment.toUpperCase()}</h2>
                    <p className="sentimen-detail">
                      Positif : {persenPositif}% ({positif})<br />
                      Negatif : {persenNegatif}% ({negatif})<br />
                      Netral : {persenNetral}% ({netral})
                    </p>
                    <p className="sentimen-count">
                      Total komentar: {total}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <footer className="site-footer">
        <p>© 2025 Social Search</p>
      </footer>
    </>
  );
};

export default Hasil;