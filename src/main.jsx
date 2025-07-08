import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import HomePage from './components/HomePage.jsx';
import Game from './components/Game.jsx';
import { ToastContainer } from 'react-toastify';

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="games/:gamename/:username" element={<Game />} />
            </Routes>
        </BrowserRouter>
        <ToastContainer rtl />
    </StrictMode>,
);
