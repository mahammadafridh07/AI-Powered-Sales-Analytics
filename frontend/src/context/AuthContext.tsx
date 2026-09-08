import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../lib/api";

interface UserT {
  id: number;
  name: string;
  email: string;
}

interface AuthContextT {
  user: UserT | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextT | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserT | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("salesai_token");
    const storedUser = localStorage.getItem("salesai_user");
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  function persist(accessToken: string, u: UserT) {
    localStorage.setItem("salesai_token", accessToken);
    localStorage.setItem("salesai_user", JSON.stringify(u));
    setToken(accessToken);
    setUser(u);
  }

  async function login(email: string, password: string) {
    const res = await api.post("/auth/login", { email, password });
    persist(res.data.access_token, res.data.user);
  }

  async function register(name: string, email: string, password: string) {
    const res = await api.post("/auth/register", { name, email, password });
    persist(res.data.access_token, res.data.user);
  }

  function logout() {
    localStorage.removeItem("salesai_token");
    localStorage.removeItem("salesai_user");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
