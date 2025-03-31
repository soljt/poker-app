import { handleError } from "../helpers/ErrorHandler";
import { auth_api } from "./api";

export const loginAPI = async (username: string, password: string) => {
    try {
        const data = await auth_api.post("/login", {username: username, password: password});
        return data;
    } catch (error) {
        handleError(error);
    }
};

export const logoutAPI = async () => {
    try {
        const data = await auth_api.post("/logout");
        return data;
    } catch (error) {
        handleError(error);
    }
};

export const registerAPI = async (username: string, password: string) => {
    try {
        const data = await auth_api.post("/register", {username: username, chips: 5000, password: password});
        return data;
    } catch (error) {
        handleError(error);
    }
};