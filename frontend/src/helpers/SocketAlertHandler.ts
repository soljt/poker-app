import { toast } from "react-toastify";

export const handleSocketError = (response: { message: string }) => {
    toast.warn(response.message);
}

export const handleSocketMessage = (message: string) => {
    toast.info(message)
}