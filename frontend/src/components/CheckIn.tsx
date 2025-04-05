import { useNavigate } from "react-router-dom";

export function CheckIn() {
  const navigate = useNavigate();

  function handleClickCheckIn() {
    navigate("/lobby");
  }

  return (
    <>
      <div className="d-flex justify-content-left">
        <button className="btn btn-primary btn-lg" onClick={handleClickCheckIn}>
          View Available Games
        </button>
      </div>
    </>
  );
}
