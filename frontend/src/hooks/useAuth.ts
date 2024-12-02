import { useState, useContext, createContext, useCallback, ReactNode } from 'react';
import axios from 'axios';

interface User {
    id: number;
    email: string;
    username: string;
    roles: string[];
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    register: (email: string, password: string, username: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(() => 
        localStorage.getItem('token')
    );

    const login = useCallback(async (email: string, password: string) => {
        try {
            const response = await axios.post<{ token: string; user: User }>(
                '/api/auth/login',
                { email, password }
            );
            const { token, user } = response.data;
            setToken(token);
            setUser(user);
            localStorage.setItem('token', token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error) {
            throw new Error('Login failed');
        }
    }, []);

    const logout = useCallback(() => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
    }, []);

    const register = useCallback(async (email: string, password: string, username: string) => {
        try {
            const response = await axios.post<{ token: string; user: User }>(
                '/api/auth/register',
                {
                    email,
                    password,
                    username,
                }
            );
            const { token, user } = response.data;
            setToken(token);
            setUser(user);
            localStorage.setItem('token', token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error) {
            throw new Error('Registration failed');
        }
    }, []);

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                login,
                logout,
                register,
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
