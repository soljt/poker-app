import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
// import NavDropdown from "react-bootstrap/NavDropdown";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { ConnectionState } from "./ConnectionState";

function NavbarComponent() {
  const navigate = useNavigate();
  const { isLoggedIn, user, logout, socket } = useAuth();
  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container>
        <Navbar.Brand>Sol-Poker.ch</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />

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
        <div className="d-flex align-items-center ms-auto gap-3">
          {isLoggedIn() && <h4 className="mb-0">Welcome, {user?.username}</h4>}
          <ConnectionState socket={socket} />
        </div>
      </Container>
    </Navbar>
  );
}

export default NavbarComponent;
