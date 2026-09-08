import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import Customers from "./pages/Customers";
import Regions from "./pages/Regions";
import Forecast from "./pages/Forecast";
import Anomalies from "./pages/Anomalies";
import AIAnalyst from "./pages/AIAnalyst";
import Recommendations from "./pages/Recommendations";
import Upload from "./pages/Upload";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route path="/app/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/app/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
            <Route path="/app/customers" element={<ProtectedRoute><Customers /></ProtectedRoute>} />
            <Route path="/app/regions" element={<ProtectedRoute><Regions /></ProtectedRoute>} />
            <Route path="/app/forecast" element={<ProtectedRoute><Forecast /></ProtectedRoute>} />
            <Route path="/app/anomalies" element={<ProtectedRoute><Anomalies /></ProtectedRoute>} />
            <Route path="/app/ai-analyst" element={<ProtectedRoute><AIAnalyst /></ProtectedRoute>} />
            <Route path="/app/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
            <Route path="/app/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
            <Route path="/app/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
