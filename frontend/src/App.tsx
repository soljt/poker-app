import { BrowserRouter as Router } from "react-router-dom";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import NavbarComponent from "./components/Navbar.tsx";
import { UserProvider } from "./context/useAuth.tsx";

import "./App.css";
import BackgroundDecider from "./components/BackgroundDecider.tsx";
import AppRoutes from "./components/AppRoutes.tsx";

export default function App() {
  return (
    <Router>
      {/*Navbar, Outlet(?)*/}
      <UserProvider>
        <BackgroundDecider>
          <NavbarComponent />
          <ToastContainer />
          <AppRoutes />
        </BackgroundDecider>
      </UserProvider>
    </Router>
  );
}
