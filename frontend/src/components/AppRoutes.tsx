import Landing from "../views/Landing.tsx";
import Lobby from "../views/Lobby.tsx";
import Login from "../views/Login.tsx";
import Register from "../views/Register.tsx";
import "react-toastify/dist/ReactToastify.css";
import ProtectedRoute from "../routes/ProtectedRoute.tsx";
import Game from "../views/Game.tsx";
import { SocketProvider } from "../context/useSocket.tsx";
import Admin from "../views/Admin.tsx";
import AdminRoute from "../routes/AdminRoute.tsx";
import { Routes, Route } from "react-router-dom";
import SpecialLanding from "./SpecialLanding.tsx";
import { useAuth } from "../context/useAuth.tsx";
import Leaderboard from "../views/Leaderboard.tsx";

export default function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {user?.username === "kenna" ? (
        <Route path="/" element={<SpecialLanding />} />
      ) : (
        <Route path="/" element={<Landing />} />
      )}

      {/* Regular landing page still accessible */}
      <Route path="/main" element={<Landing />} />

      <Route
        path="/lobby"
        element={
          <ProtectedRoute>
            <SocketProvider>
              <Lobby />
            </SocketProvider>
          </ProtectedRoute>
        }
      />
      <Route
        path="/game"
        element={
          <ProtectedRoute>
            <SocketProvider>
              <Game />
            </SocketProvider>
          </ProtectedRoute>
        }
      />
      <Route path="/register" element={<Register />}></Route>
      <Route path="/login" element={<Login />} />
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <Admin />
          </AdminRoute>
        }
      />
      <Route path="/leaderboard" element={<Leaderboard />} />
    </Routes>
  );
}
