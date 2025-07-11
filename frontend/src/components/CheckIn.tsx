import { useNavigate } from "react-router-dom";

export function CheckIn() {
  const navigate = useNavigate();

  function handleClickCheckIn() {
    navigate("/lobby");
  }

  return (
    <>
      <div className="d-flex justify-content-center">
        <button
          className="btn btn-lg btn-primary btn-block"
          onClick={handleClickCheckIn}
        >
          View Available Games
        </button>
      </div>
    </>
  );
}
