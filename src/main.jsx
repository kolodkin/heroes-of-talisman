import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import "./i18n";
import HomePage from "./components/HomePage.jsx";
import GameHandler from "./components/GamePlay/GameHandler.jsx";
import DiceView from "./components/DiceView.jsx";
import NotFound from "./components/NotFound.jsx";
import { ToastContainer } from "react-toastify";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dice" element={<DiceView />} />
        <Route path="games/:gamename/:username" element={<GameHandler />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
    <ToastContainer rtl />
  </StrictMode>,
);
