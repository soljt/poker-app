import { useState, FormEvent } from "react";
import { useAuth } from "../context/useAuth";
import { toast } from "react-toastify";
import { handleError } from "../helpers/ErrorHandler";

export default function Register() {
  const { registerUser } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    if (!username) return toast.warning("Please enter a username");
    if (password !== confirmPassword)
      return toast.warning("Passwords do not match!");
    try {
      registerUser(username, password);
    } catch (error: unknown) {
      handleError(error);
    }
  };

  return (
    <div className="container" style={{ marginTop: "10vh" }}>
      <form onSubmit={handleRegister}>
        <h2>Create a new account!</h2>
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
        <div className="mb-3">
          <label htmlFor="password" className="form-label">
            Confirm Password :
          </label>
          <input
            onChange={(e) => {
              setConfirmPassword(e.target.value);
            }}
            type="password"
            className="form-control"
            id="confirmPassword"
          />
        </div>
        <button type="submit" className="btn btn-primary">
          REGISTER
        </button>
        <p style={{ marginTop: "2vh" }} className="font-italic">
          You are a bright and resourceful individual for finding this page
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
