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

  const welcomeMessage =
    user?.username === "kenna" ? "my love! ❤️" : user?.username;
  const chipDisplay = (
    <div className="badge bg-primary-subtle text-primary-emphasis">
      💰 {user?.chips?.toLocaleString()} Chips
    </div>
  );

  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container>
        <Navbar.Brand>
          <img
            src="/favicon.png"
            width="35"
            height="35"
            className="d-inline-block align-top"
            alt="React Bootstrap logo"
          />{" "}
          poker.soljt.ch
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />

        {/* Mobile Welcome Message */}
        <div className="d-lg-none ms-auto">
          {isLoggedIn() && (
            <div className="text-end">
              <div className="fw-semibold">Welcome, {welcomeMessage}</div>
              {chipDisplay}
            </div>
          )}
        </div>

        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            {user?.username === "kenna" ? (
              <>
                <Nav.Link
                  onClick={() => {
                    navigate("/");
                  }}
                >
                  ❤️ Special Page
                </Nav.Link>
                <Nav.Link
                  onClick={() => {
                    navigate("/main");
                  }}
                >
                  Landing
                </Nav.Link>
              </>
            ) : (
              <Nav.Link
                onClick={() => {
                  navigate("/");
                }}
              >
                Home
              </Nav.Link>
            )}

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
        {/* Desktop Welcome Message */}
        <div className="d-none d-lg-flex align-items-center ms-auto">
          {isLoggedIn() && (
            <div className="text-end me-3">
              <div className="fw-semibold">Welcome, {welcomeMessage}</div>
              {chipDisplay}
            </div>
          )}
        </div>
      </Container>
    </Navbar>
  );
}

export default NavbarComponent;
