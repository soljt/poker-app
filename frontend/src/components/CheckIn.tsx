import { socket } from "../socket";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function CheckIn() {
  const navigate = useNavigate();
  useEffect(() => {
    function handleCheckedIn(response: { message: string }) {
      alert(response.message);
    }
    socket.on("checked_in", handleCheckedIn);

    return () => {
      socket.off("checked_in", handleCheckedIn); // Cleanup listener on unmount
    };
  }, []); // Runs only once when the component mounts

  function handleClickCheckIn() {
    socket.emit("check_in");
    const user = localStorage.getItem("user");
    alert({ typeof: user });
    //navigate("/lobby");
    // socket.on("checked_in", (response) => alert(response.message));
  }

  function handleClickLogin() {
    navigate("/login");
  }

  return (
    <>
      <div className="d-flex justify-content-around">
        <button className="btn btn-primary btn-lg" onClick={handleClickCheckIn}>
          Check In
        </button>
        <button className="btn btn-secondary btn-lg" onClick={handleClickLogin}>
          Login
        </button>
      </div>
    </>
  );
}
