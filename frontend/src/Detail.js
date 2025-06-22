import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Detail.css";

function Detail() {
  const navigate = useNavigate();

  const video = {
    video_id: "vid_dummy",
    nickname: "@suara_rakyat",
    url: "https://www.tiktok.com/@user_dummy/video/99999",
    desc: "RUU TNI: Bahaya bagi Demokrasi? atau ternyata baik untuk demokrasi? berikan komentarmu #ruutni #ruupolri #demokrasi",
    tanggal_upload: "2025-05-27",
    jumlah_comment: 20,
    sentiment_positive: 3,
    sentiment_negative: 17,
    comments: [
      { text: "RUU ini sangat berbahaya untuk demokrasi.", sentiment: "negatif", timestamp: 1 },
      { text: "Kenapa pemerintah terus memaksakan RUU ini? Sangat merugikan rakyat.", sentiment: "negatif", timestamp: 2 },
      { text: "Saya setuju TNI harus profesional, tapi RUU ini terlalu berlebihan.", sentiment: "negatif", timestamp: 3 },
      { text: "Ini bukan solusi yang tepat, malah bisa menimbulkan konflik.", sentiment: "negatif", timestamp: 4 },
      { text: "Konten sangat informatif, terima kasih sudah membahas isu penting ini.", sentiment: "positif", timestamp: 5 },
      { text: "Pemerintah harus dengarkan suara rakyat, bukan hanya TNI.", sentiment: "negatif", timestamp: 6 },
      { text: "RUU TNI ini membatasi kebebasan sipil.", sentiment: "negatif", timestamp: 7 },
      { text: "Video ini membuka mata saya tentang bahaya RUU.", sentiment: "positif", timestamp: 8 },
      { text: "Saya takut kalau RUU ini disahkan, masa depan Indonesia jadi suram.", sentiment: "negatif", timestamp: 9 },
      { text: "Tolong sebarkan info ini ke lebih banyak orang!", sentiment: "positif", timestamp: 10 },
      { text: "Banyak orang yang belum paham bahayanya RUU ini.", sentiment: "negatif", timestamp: 11 },
      { text: "Ini justru akan memperkuat militerisasi di Indonesia.", sentiment: "negatif", timestamp: 12 },
      { text: "Saya dukung TNI tapi tolak RUU ini.", sentiment: "negatif", timestamp: 13 },
      { text: "Semoga pemerintah bisa pertimbangkan aspirasi rakyat.", sentiment: "positif", timestamp: 14 },
      { text: "Konten kurang lengkap, perlu data lebih banyak.", sentiment: "negatif", timestamp: 15 },
      { text: "Kita harus kritis terhadap kebijakan seperti ini.", sentiment: "negatif", timestamp: 16 },
      { text: "RUU ini melemahkan posisi sipil di pemerintahan.", sentiment: "negatif", timestamp: 17 },
      { text: "Video bagus, tapi saya tetap skeptis dengan RUU ini.", sentiment: "negatif", timestamp: 18 },
      { text: "RUU TNI harus dibatalkan demi keadilan.", sentiment: "negatif", timestamp: 19 },
      { text: "Terima kasih sudah berbagi perspektif yang berbeda.", sentiment: "positif", timestamp: 20 },
    ],
  };

  const [sortType, setSortType] = useState("terbaru");

  const sortedComments = [...video.comments].sort((a, b) => {
    if (sortType === "terbaru") {
      return b.timestamp - a.timestamp; // descending
    } else if (sortType === "positif") {
      return a.sentiment === "positif" ? -1 : 1;
    } else if (sortType === "negatif") {
      return a.sentiment === "negatif" ? -1 : 1;
    }
    return 0;
  });

  const percentPos = ((video.sentiment_positive / video.jumlah_comment) * 100).toFixed(0);
  const percentNeg = ((video.sentiment_negative / video.jumlah_comment) * 100).toFixed(0);

  return (
    <>
      <header className="site-header">
        <h1 className="site-title">Social Search🔍</h1>
      </header>

      <div className="detail-container">
        <div className="content">
          <div className="header">
            <button className="back-btn" onClick={() => navigate(-1)}>←</button>
            <h2 className="nickname">{video.nickname}</h2>
          </div>

          <p className="desc">{video.desc}</p>
          <p><strong>Tanggal Upload:</strong> {video.tanggal_upload}</p>
          <p><strong>Total Komentar:</strong> {video.jumlah_comment}</p>

          <div className="sentiment-summary">
            <p><strong>Ringkasan Sentimen:</strong></p>
            <ul>
              <li>Positif: {video.sentiment_positive} ({percentPos}%)</li>
              <li>Negatif: {video.sentiment_negative} ({percentNeg}%)</li>
            </ul>
          </div>

          <div className="sort-options">
            <label htmlFor="sort">Urutkan Komentar: </label>
            <select id="sort" value={sortType} onChange={(e) => setSortType(e.target.value)}>
              <option value="terbaru">Terbaru</option>
              <option value="positif">Sentimen Positif</option>
              <option value="negatif">Sentimen Negatif</option>
            </select>
          </div>

          <h3>Komentar Lengkap</h3>
          <div className="comment-box">
            {sortedComments.map((c, i) => (
              <div key={i} className={`comment-item ${c.sentiment}`}>
                <span className={`sentiment-label ${c.sentiment}`}>
                  {c.sentiment.toUpperCase()}
                </span>
                <p>{c.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <footer className="site-footer">
        <p>© 2025 Sosial Search</p>
      </footer>
    </>
  );
}

export default Detail;
