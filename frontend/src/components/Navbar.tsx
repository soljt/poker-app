import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
// import NavDropdown from "react-bootstrap/NavDropdown";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { Roles } from "../types";

function NavbarComponent() {
  const navigate = useNavigate();
  const { isLoggedIn, user, logout } = useAuth();
  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container>
        <Navbar.Brand>Sol-Poker.ch</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />

        <div className="d-lg-none ms-auto">
          {isLoggedIn() && (
            <span className="fw-semibold">Welcome, {user?.username}</span>
          )}
        </div>

        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link
              onClick={() => {
                navigate("/");
              }}
            >
              Home
            </Nav.Link>
            <Nav.Link
              onClick={() => {
                navigate("/lobby");
              }}
            >
              Lobby
            </Nav.Link>
            {user?.role == Roles.admin && (
              <Nav.Link
                onClick={() => {
                  navigate("/admin");
                }}
              >
                Admin
              </Nav.Link>
            )}
            {isLoggedIn() ? (
              <Nav.Link onClick={logout}>Logout</Nav.Link>
            ) : (
              <Nav.Link
                onClick={() => {
                  navigate("/login");
                }}
              >
                Login
              </Nav.Link>
            )}
          </Nav>
        </Navbar.Collapse>
        <div className="d-none d-lg-block ms-auto">
          {isLoggedIn() && (
            <div className="d-none d-lg-flex align-items-center ms-auto">
              <div className="text-end me-3">
                <div className="fw-semibold">Welcome, {user?.username}</div>
                <div className="badge bg-primary-subtle text-primary-emphasis">
                  💰 {user?.chips.toLocaleString()} Chips
                </div>
              </div>
            </div>
          )}
        </div>
      </Container>
    </Navbar>
  );
}

export default NavbarComponent;
