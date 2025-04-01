import { useState, useEffect, FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { toast } from "react-toastify";
import { handleError } from "../helpers/ErrorHandler";

export default function Login() {
  const navigate = useNavigate();
  const { isLoggedIn, loginUser } = useAuth();
  const location = useLocation();

  useEffect(() => {
    try {
      if (isLoggedIn()) {
        const redirectPath = location.state?.from?.pathname || "/";
        navigate(redirectPath);
      }
    } catch {
      toast.warning("Something bad");
    }
  }, [isLoggedIn, location.state?.from?.pathname, navigate]);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!username) return alert("Enter a username");
    try {
      loginUser(username, password);
    } catch (error: unknown) {
      handleError(error);
    }
  };

  return (
    <div className="container" style={{ marginTop: "10vh" }}>
      <form onSubmit={handleLogin}>
        <h2>Login to your account</h2>
        <div className="mb-3">
          <label htmlFor="username" className="form-label">
            Username :
          </label>
          <input
            onChange={(e) => {
              setUsername(e.target.value);
            }}
            type="username"
            className="form-control"
            id="username"
            autoComplete="username"
          />
        </div>
        <div className="mb-3">
          <label htmlFor="password" className="form-label">
            Password :
          </label>
          <input
            onChange={(e) => {
              setPassword(e.target.value);
            }}
            type="password"
            className="form-control"
            id="password"
            autoComplete="true"
          />
        </div>
        <button type="submit" className="btn btn-primary">
          LOG IN
        </button>
        <p>
          <br />
          Demo User: <br />
          Username: hotbrian <br />
          Password: password12345
        </p>
      </form>
      <p style={{ marginTop: "2vh" }}>
        Don't have an account? Too bad. Ask Sol to make you one.
      </p>
      <p style={{ marginTop: "2vh" }}>...</p>
      <div className="float-end">
        <button
          type="button"
          className="btn btn-outline-light btn-sm"
          onClick={() => {
            navigate("/register");
          }}
        >
          Or click this really small button
        </button>
      </div>
    </div>
  );
}
