import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { apiClient } from '../api/client';
import { profileApi } from '../api/endpoints';
import type { Profile } from '../types';

interface AuthContextType {
  user: Profile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    try {
      if (apiClient.isAuthenticated()) {
        try {
          const response = await profileApi.getMe();
          setUser(response.data);
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          setUser(null);
          // Don't fail completely if API is not available
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error in refreshUser:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (username: string, password: string) => {
    await apiClient.login(username, password);
    await refreshUser();
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
