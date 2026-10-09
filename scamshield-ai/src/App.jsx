import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import AdaptiveLayout from "./components/layout/AdaptiveLayout";
import AppLayout from "./components/layout/AppLayout";
import ProtectedRoute from "./components/layout/ProtectedRoute";
import PublicLayout from "./components/layout/PublicLayout";
import ScrollToTop from "./components/layout/ScrollToTop";

import About from "./pages/About";
import Analysis from "./pages/Analysis";
import Dashboard from "./pages/Dashboard";
import FAQ from "./pages/FAQ";
import Gmail from "./pages/Gmail";
import History from "./pages/History";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Register from "./pages/Register";
import Report from "./pages/Report";
import Results from "./pages/Results";
import Scanner from "./pages/Scanner";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <Routes>
          {/* Public */}
          <Route element={<PublicLayout />}>
            <Route path="/" element={<Landing />} />
          </Route>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Public when logged out, app shell when logged in */}
          <Route element={<AdaptiveLayout />}>
            <Route path="/about" element={<About />} />
            <Route path="/faq" element={<FAQ />} />
          </Route>

          {/* Protected */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/scanner" element={<Scanner />} />
              <Route path="/gmail" element={<Gmail />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/results/:scanId" element={<Results />} />
              <Route path="/history" element={<History />} />
              <Route path="/reports/:scanId" element={<Report />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}