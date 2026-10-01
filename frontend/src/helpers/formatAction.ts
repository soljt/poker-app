import { LastAction } from "../types";

export const formatLastAction = ({ action, amount, allin }: LastAction) => {
  if (action === "fold") return "Folded";
  if (action === "check") return "Checked";
  if (allin) return `All-in ${amount}`;
  if (action === "call") return `Called ${amount}`;
  if (action === "bet") return `Bet ${amount}`;
  return `Raised to ${amount}`;
};

export const describeLastAction = (username: string, last: LastAction) => {
  if (last.allin && last.action !== "fold")
    return `${username} went all-in for ${last.amount}`;
  const label = formatLastAction(last);
  return `${username} ${label[0].toLowerCase()}${label.slice(1)}`;
};
