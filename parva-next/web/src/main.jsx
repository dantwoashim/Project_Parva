import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import Audit from "./pages/Audit.jsx";
import Data from "./pages/Data.jsx";
import Review from "./pages/Review.jsx";
import Convert from "./pages/Convert.jsx";
import { FestivalDetail, FestivalList } from "./pages/Festivals.jsx";
import Holidays from "./pages/Holidays.jsx";
import Month from "./pages/Month.jsx";
import Today from "./pages/Today.jsx";
import "./styles.css";
import { Shell } from "./ui.jsx";

function NotFound() {
  return <><h1>Not found</h1><p><Link to="/">Back to today</Link></p></>;
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Shell>
        <Routes>
          <Route path="/" element={<Today />} />
          <Route path="/convert" element={<Convert />} />
          <Route path="/calendar" element={<Month />} />
          <Route path="/calendar/:year/:month" element={<Month />} />
          <Route path="/holidays" element={<Holidays />} />
          <Route path="/holidays/:year" element={<Holidays />} />
          <Route path="/festivals" element={<FestivalList />} />
          <Route path="/festivals/:id" element={<FestivalDetail />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="/review" element={<Review />} />
          <Route path="/data" element={<Data />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Shell>
    </BrowserRouter>
  </StrictMode>,
);
