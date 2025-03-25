import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Landing from "./views/Landing.tsx";
import Lobby from "./views/Lobby.tsx";
import Login from "./views/Login.tsx";
import { ToastContainer } from "react-toastify";

export default function App() {
  return (
    <Router>
      {/*Navbar, Outlet(?)*/}
      <ToastContainer />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/lobby" element={<Lobby />} />
        <Route path="login" element={<Login />} />
      </Routes>
    </Router>
  );
}
