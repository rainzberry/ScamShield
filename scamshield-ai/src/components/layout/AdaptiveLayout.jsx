import { useAuth } from "../../context/AuthContext";
import AppLayout from "./AppLayout";
import PublicLayout from "./PublicLayout";

/* About / FAQ are reachable both logged-in (app shell) and logged-out (public shell). */
export default function AdaptiveLayout() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <AppLayout /> : <PublicLayout contained />;
}