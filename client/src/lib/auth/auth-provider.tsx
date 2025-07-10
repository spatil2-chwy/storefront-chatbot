import React, { createContext, ReactNode, useState, useEffect } from 'react';
import { authApi } from '../api/auth';

export interface User {
  customer_key: number;
  customer_id: number;
  name: string;
  email: string;
  password: string;
  operating_revenue_trailing_365?: number;
  customer_order_first_placed_dttm?: string;
  customer_address_zip?: string;
  customer_address_city?: string;
  customer_address_state?: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

// export function AuthProvider({ children }: { children: ReactNode }) {
//   const [user, setUser] = useState<User | null>(null);
//   const [isAuthenticated, setIsAuthenticated] = useState(false);

//   const login = async (email: string, password: string): Promise<boolean> => {
//     try {
//       const response = await axios.post<User>('http://localhost:8000/customers/login', { email, password });
//       const loggedInUser = response.data;

//       setUser(loggedInUser);
//       setIsAuthenticated(true);
//       localStorage.setItem('isAuthenticated', 'true');
//       localStorage.setItem('user', JSON.stringify(loggedInUser));

//       return true;
//     } catch (error: any) {
//       // inspect error
//       console.error('Login error:', error);
//       return false;
//     }
//   };

  // auth.tsx
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const userData = await authApi.login(email, password);
      // we got a valid user back → log them in
      setUser(userData);
      setIsAuthenticated(true);
      // persist so that refreshes also "remember" they're in
      localStorage.setItem("user", JSON.stringify(userData));
      return true;
    } catch {
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
