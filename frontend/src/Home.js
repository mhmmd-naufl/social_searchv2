import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaCalendarAlt, FaClock, FaTemperatureHigh, FaBars } from "react-icons/fa";
import "./Home.css";

function Home() {
  const [keyword, setKeyword] = useState("");
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [temp, setTemp] = useState("...");

  const navigate = useNavigate();

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

  useEffect(() => {
  const fetchWeather = async () => {
  try {
    const city = "Banyuwangi";
    const apiKey = "39699f61db3b4088483dff28ef6f48ab";
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

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("searchHistory") || "[]");
    setHistory(stored);
  }, []);

  const handleSearch = () => {
    if (keyword.trim()) {
      const updatedHistory = [keyword, ...history.filter((k) => k !== keyword)].slice(0, 5);
      localStorage.setItem("searchHistory", JSON.stringify(updatedHistory));
      setHistory(updatedHistory);
     navigate(`/hasil?keyword=${encodeURIComponent(keyword)}`);

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
          <div className="title">Social Search🔍</div>

          {/* Wrap FaBars dan Dropdown dalam container */}
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
          <button onClick={handleSearch} className="search-button">
            Cari
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

export default Home;