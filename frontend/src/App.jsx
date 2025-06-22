import React, { useState, useEffect } from "react";
import { FaCalendarAlt, FaClock, FaTemperatureHigh, FaBars } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import "./Home.css";

function App() {
  const [keyword, setKeyword] = useState("");
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [temp, setTemp] = useState("...");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Update waktu dan tanggal
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const options = {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      };
      setDate(now.toLocaleDateString("id-ID", options));
      setTime(now.toLocaleTimeString("id-ID"));
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch suhu cuaca
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const city = "Banyuwangi";
        const apiKey = "REDACTED";
        const response = await fetch(
          `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`
        );
        const data = await response.json();
        const temperature = data.main.temp;
        setTemp(`${temperature.toFixed(1)}°C`);
      } catch (error) {
        console.error("Gagal mengambil suhu:", error);
        setTemp("Gagal");
      }
    };

    fetchWeather();
  }, []);

  // Ambil history dari localStorage
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("searchHistory") || "[]");
    setHistory(stored);
  }, []);

  // Fungsi pencarian
  const handleSearch = async () => {
    if (keyword.trim()) {
      setLoading(true);
      const updatedHistory = [keyword, ...history.filter((k) => k !== keyword)].slice(0, 5);
      localStorage.setItem("searchHistory", JSON.stringify(updatedHistory));
      setHistory(updatedHistory);

      // Simpan keyword ke sessionStorage agar bisa diakses di Hasil.js
      sessionStorage.setItem("lastKeyword", keyword);

      // Redirect ke halaman hasil
      navigate("/hasil");
      setLoading(false);
    }
  };

  const handleHistoryClick = (item) => {
    setKeyword(item);
    setShowHistory(false);
  };

  const toggleHistory = () => {
    setShowHistory((prev) => !prev);
  };

  return (
    <>
      <div className="main">
        <div className="top-bar">
          <div className="title">Social Search</div>
          <div className="history-container">
            <FaBars className="history-icon" onClick={toggleHistory} />
            {showHistory && (
              <div className="history-dropdown">
                {history.length === 0 ? (
                  <div className="history-item empty">Belum ada history</div>
                ) : (
                  history.map((item, idx) => (
                    <div key={idx} className="history-item" onClick={() => handleHistoryClick(item)}>
                      {item}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        <div className="search-bar">
          <div className="search-container"></div>
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
            placeholder="Cari konten TikTok"
            className="search-input"
          />
          <button onClick={handleSearch} className="search-button" disabled={loading}>
            {loading ? "Loading..." : "Cari"}
          </button>
        </div>
      </div>

      <div className="info-bar">
        <div className="info-item">
          <FaCalendarAlt className="icon" /> {date}
        </div>
        <div className="info-item">
          <FaClock className="icon" /> {time}
        </div>
        <div className="info-item">
          <FaTemperatureHigh className="icon" /> {temp}
        </div>
      </div>
    </>
  );
}

export default App;