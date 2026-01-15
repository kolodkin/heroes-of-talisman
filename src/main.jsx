import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import "./i18n";

if (import.meta.env.VITE_E2E === "true") {
  import("./e2e_patches.css");
}
import HomePage from "./components/HomePage.jsx";
import GameHandler from "./components/GamePlay/GameHandler.jsx";
import DiceView from "./components/DiceView.jsx";
import Presets from "./components/Presets.jsx";
import IconGallery from "./components/IconGallery.jsx";
import NotFound from "./components/NotFound.jsx";
import { ToastContainer } from "react-toastify";

const isDev = import.meta.env.DEV;

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        {isDev && <Route path="/dice" element={<DiceView />} />}
        {isDev && <Route path="/presets" element={<Presets />} />}
        {isDev && <Route path="/icons" element={<IconGallery />} />}
        <Route path="games/:gamename/:username" element={<GameHandler />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
    <ToastContainer rtl />
  </StrictMode>,
);
