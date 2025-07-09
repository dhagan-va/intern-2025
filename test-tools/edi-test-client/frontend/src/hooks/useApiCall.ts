import { useState } from "react";
const API_BASE = "http://localhost:5001";

export const useApiCall = () => {
  const [message, setMessage] = useState("");
  const apiCall = async (endpoint: string, method = "POST", body?: object) => {
    try {
      const response = await fetch(`${API_BASE}/${endpoint}`, {
        method,
        headers: body ? { "Content-Type": "application/json" } : {},
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await response.json();
      setMessage(data.message || data.error);
    } catch (error) {
      console.error(`Error with ${endpoint}:`, error);
      setMessage(`Error with ${endpoint}`);
    }
  };
  return { apiCall, message };
};
