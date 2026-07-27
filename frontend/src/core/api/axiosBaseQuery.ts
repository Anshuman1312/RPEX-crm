import type { AxiosError, AxiosRequestConfig } from "axios";
import type { BaseQueryFn } from "@reduxjs/toolkit/query";
import { http } from "@/core/api/axios";

interface AxiosBaseQueryArgs {
  url: string;
  method: AxiosRequestConfig["method"];
  data?: AxiosRequestConfig["data"];
  params?: AxiosRequestConfig["params"];
}

interface ApiError {
  status?: number;
  data?: unknown;
  message?: string;
}

export const axiosBaseQuery =
  (): BaseQueryFn<AxiosBaseQueryArgs, unknown, ApiError> => async ({
    url,
    method,
    data,
    params
  }) => {
    try {
      const result = await http({ url, method, data, params });
      return { data: result.data };
    } catch (axiosError) {
      const err = axiosError as AxiosError;
      return {
        error: {
          status: err.response?.status,
          data: err.response?.data,
          message: err.message
        }
      };
    }
  };
