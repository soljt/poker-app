import { Roles } from "../types";

export type User = {
    username: string;
    chips: bigint;
    role: Roles
}