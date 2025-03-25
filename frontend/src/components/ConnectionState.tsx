export function ConnectionState({ isConnected }: { isConnected: boolean }) {
  return <p>State: {String(isConnected)}</p>;
}
