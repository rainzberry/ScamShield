import client from "./client";
import { apiError } from "../utils/errors";

export async function register({ name, email, password }) {
  const { data } = await client.post("/auth/register", { name, email, password });
  if (data?.success === false) throw apiError(data.error || data.message || "Registration failed.");
  return { token: data?.token || data?.access_token || null, user: data?.user || null };
}

export async function login({ email, password }) {
  const { data } = await client.post("/auth/login", { email, password });
  if (!data || data.success === false) {
    throw apiError(data?.error || data?.message || "Login failed.");
  }
  const token = data.token || data.access_token || null;
  const user = data.user || { email };
  if (!token && !data.user) throw apiError("Unexpected response from the server.");
  return { token, user };
}

export async function logout() {
  await client.post("/auth/logout");
}