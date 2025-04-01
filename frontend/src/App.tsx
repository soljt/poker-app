import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Landing from "./views/Landing.tsx";
import Lobby from "./views/Lobby.tsx";
import Login from "./views/Login.tsx";
import Register from "./views/Register.tsx";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import NavbarComponent from "./components/Navbar.tsx";
import { UserProvider } from "./context/useAuth.tsx";
import ProtectedRoute from "./routes/ProtectedRoute.tsx";

export default function App() {
  return (
    <Router>
      {/*Navbar, Outlet(?)*/}
      <UserProvider>
        <NavbarComponent />
        <ToastContainer />

        <Routes>
          <Route path="/" element={<Landing />} />
          <Route
            path="/lobby"
            element={
              <ProtectedRoute>
                <Lobby />
              </ProtectedRoute>
            }
          />
          <Route path="/register" element={<Register />}></Route>
          <Route path="/login" element={<Login />} />
        </Routes>
      </UserProvider>
    </Router>
  );
}
