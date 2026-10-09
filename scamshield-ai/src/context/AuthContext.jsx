import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import * as authApi from "../api/authApi";
import { UNAUTHORIZED_EVENT } from "../api/client";
import { clearSession, loadSession, saveSession } from "../utils/storage";
import { isTokenExpired } from "../utils/token";

const AuthContext = createContext(null);

function readInitialSession() {
  const { token, user } = loadSession();
  if (token && isTokenExpired(token)) {
    clearSession();
    return { token: null, user: null, expired: true };
  }
  return { token, user, expired: false };
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const s = readInitialSession();
    return { token: s.token, user: s.user };
  });
  const [sessionExpired, setSessionExpired] = useState(() => readInitialSession().expired);

  const expireSession = useCallback(() => {
    clearSession();
    setSession({ token: null, user: null });
    setSessionExpired(true);
  }, []);

  // Any 401 from the API (non-auth endpoints) ends the session
  useEffect(() => {
    window.addEventListener(UNAUTHORIZED_EVENT, expireSession);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, expireSession);
  }, [expireSession]);

  // Periodic JWT expiry check
  useEffect(() => {
    if (!session.token) return undefined;
    const id = setInterval(() => {
      if (isTokenExpired(session.token)) expireSession();
    }, 30000);
    return () => clearInterval(id);
  }, [session.token, expireSession]);

  const login = useCallback(async (email, password) => {
    const result = await authApi.login({ email, password });
    saveSession(result);
    setSession(result);
    setSessionExpired(false);
    return result.user;
  }, []);

  const register = useCallback(async ({ name, email, password }) => {
    const result = await authApi.register({ name, email, password });
    if (result.token) {
      const next = { token: result.token, user: result.user || { name, email } };
      saveSession(next);
      setSession(next);
      setSessionExpired(false);
      return next.user;
    }
    return login(email, password);
  }, [login]);

  const logout = useCallback(async () => {
    try { await authApi.logout(); } catch { /* ignore: we clear locally regardless */ }
    clearSession();
    setSession({ token: null, user: null });
    setSessionExpired(false);
  }, []);

  const value = useMemo(
    () => ({
      user: session.user,
      token: session.token,
      isAuthenticated: Boolean(session.user || session.token),
      sessionExpired,
      login,
      register,
      logout,
    }),
    [session, sessionExpired, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}