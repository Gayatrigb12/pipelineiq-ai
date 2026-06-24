import axios from "axios";

const BASE_URL = "http://localhost:8000";

const client = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

// Response interceptor — unwrap data, normalise errors
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

// GET /health
export const getHealth = () => client.get("/health");

// POST /upload-deals  — payload: { deals: [...] }
export const uploadDeals = (deals) =>
  client.post("/upload-deals", { deals });

// POST /chat  — payload: { question: "..." }
export const askQuestion = (question) =>
  client.post("/chat", { question });