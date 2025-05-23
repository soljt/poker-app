const HostGameManager = ({
  handleCreateGame,
}: {
  handleCreateGame: () => void;
}) => {
  return (
    <div className="vstack gap-3">
      {
        <button className="btn btn-lg btn-info" onClick={handleCreateGame}>
          Create Game
        </button>
      }
    </div>
  );
};

export default HostGameManager;
