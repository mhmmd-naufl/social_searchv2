import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Hasil from "./Hasil";
import Detail from "./Detail";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/hasil" element={<Hasil />} />
      <Route path="/detail/:video_id" element={<Detail />} />
    </Routes>
  </BrowserRouter>
);