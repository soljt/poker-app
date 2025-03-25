import axios from "axios";
import { toast } from "react-toastify";

interface ValidationErrors {
  [key: string]: string[];
}

interface APIErrorResponse {
  errors?: ValidationErrors | { description: string }[];
  error?: string;
}

export const handleError = (error: unknown): void => {
  if (axios.isAxiosError(error)) {
    const err = error.response;
    const data = err?.data as APIErrorResponse | undefined;

    if (Array.isArray(data?.errors)) {
      // Case: errors is an array of { description: string }
      data.errors.forEach((errorItem) => {
        if ("description" in errorItem) {
          toast.warning(errorItem.description);
        }
      });
    } else if (data?.errors && typeof data.errors === "object") {
      // Case: errors is an object { fieldName: ["Error message"] }
      Object.entries(data.errors).forEach(([, messages]) => {
        if (Array.isArray(messages) && messages.length > 0) {
          toast.warning(messages[0]); // Show the first error message
        }
      });
    } else if (typeof data?.error === "string") {
      // Case: Simple error message
      toast.warning(data.error);
    } else if (err?.status === 401) {
      toast.warning("Please login");
      window.history.pushState({}, "LoginPage", "/login");
    } else if (data) {
      toast.warning(String(data));
    }
  }
};

