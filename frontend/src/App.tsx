import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Landing from "./views/Landing.tsx";
import Lobby from "./views/Lobby.tsx";
import Login from "./views/Login.tsx";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import BasicExample from "./components/Navbar.tsx";
import { UserProvider } from "./context/useAuth.tsx";

export default function App() {
  return (
    <Router>
      {/*Navbar, Outlet(?)*/}

      <BasicExample />
      <ToastContainer />
      <UserProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/lobby" element={<Lobby />} />

          <Route path="login" element={<Login />} />
        </Routes>
      </UserProvider>
    </Router>
  );
}
