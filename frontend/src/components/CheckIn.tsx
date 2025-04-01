import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export function CheckIn() {
  const { socket } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    function handleCheckedIn(response: { message: string }) {
      alert(response.message);
    }
    socket?.on("checked_in", handleCheckedIn);

    return () => {
      socket?.off("checked_in", handleCheckedIn); // Cleanup listener on unmount
    };
  }, [socket]); // Runs only once when the component mounts

  function handleClickCheckIn() {
    socket?.emit("check_in");
    navigate("/lobby");
    // socket.on("checked_in", (response) => alert(response.message));
  }

  return (
    <>
      <div className="d-flex justify-content-left">
        <button className="btn btn-primary btn-lg" onClick={handleClickCheckIn}>
          Check In
        </button>
      </div>
    </>
  );
}
