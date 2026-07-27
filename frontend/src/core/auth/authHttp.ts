import axios from "axios";
import { env } from "@/config/env";

export const authHttp = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15000,
  withCredentials: true
});
