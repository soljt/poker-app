import axios from "axios";
import { handleError } from "../helpers/ErrorHandler";
import { UserToken } from "../models/User";

const api = "http://localhost:5000";

export const loginAPI = async (username: string, password: string) => {
    try {
        const data = await axios.post<UserToken>(api + "/login", {username: username, password: password});
        return data;
    } catch (error) {
        handleError(error);
    }
};

export const registerAPI = async (username: string, password: string) => {
    try {
        const data = await axios.post<UserToken>(api + "/register", {username: username, chips: 5000, password: password});
        return data;
    } catch (error) {
        handleError(error);
    }
};