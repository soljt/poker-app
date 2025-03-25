import { useState, useEffect, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import axios, { AxiosError } from "axios";
import { User } from "../models/User";

export default function Login() {
  const navigate = useNavigate();

  useEffect(() => {
    const checkLogin = async () => {
      if (localStorage.getItem("user")) {
        const userObj = JSON.parse(
          localStorage.getItem("user") || "{}"
        ) as User;
        const res = await axios.get("http://127.0.0.1:5000/user", {
          params: { userId: userObj.id },
        });
        localStorage.setItem("user", JSON.stringify(res.data));
        navigate("/");
      }
    };

    checkLogin();
  }, [navigate]);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!username) return alert("Enter a username");

    try {
      const requestBody = { username, password };
      const res = await axios.post("http://127.0.0.1:5000/login", requestBody);
      localStorage.setItem("user", JSON.stringify(res.data));
      navigate("/");
    } catch (error: unknown) {
      const err = error as AxiosError<{ error: string }>;
      if (err.response) {
        alert(err.response.data.error);
      } else {
        alert("An error occurred");
      }
    }
  };

  return (
    <div className="container" style={{ marginTop: "10vh" }}>
      <form onSubmit={handleLogin}>
        <h2>Login to your account</h2>
        <div className="mb-3">
          <label htmlFor="email" className="form-label">
            Username :
          </label>
          <input
            onChange={(e) => {
              setUsername(e.target.value);
            }}
            type="username"
            className="form-control"
            id="username"
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
          />
        </div>
        <button type="submit" className="btn btn-primary">
          LOG IN
        </button>
        <p style={{ marginTop: "2vh" }}>
          Don't have an account? Too bad. Ask Sol to make you one
        </p>
        <p>
          <br />
          Demo User: <br />
          Username: hotbrian <br />
          Password: password12345
        </p>
      </form>
    </div>
  );
}
