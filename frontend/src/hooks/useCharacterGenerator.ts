import { useState, useCallback } from 'react';
import axios, { AxiosError } from 'axios';
import { useAuth } from './useAuth';
import {
    CharacterAttributes,
    CharacterStyle,
    GenerateCharacterResponse,
    APIError
} from '../types/animation';

interface UseCharacterGeneratorReturn {
    generateCharacter: (
        prompt: string,
        style: CharacterStyle,
        attributes?: CharacterAttributes
    ) => Promise<GenerateCharacterResponse>;
    loading: boolean;
    error: string | null;
    clearError: () => void;
}

export const useCharacterGenerator = (): UseCharacterGeneratorReturn => {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const { token } = useAuth();

    const clearError = useCallback(() => {
        setError(null);
    }, []);

    const generateCharacter = useCallback(async (
        prompt: string,
        style: CharacterStyle,
        attributes?: CharacterAttributes
    ): Promise<GenerateCharacterResponse> => {
        try {
            setLoading(true);
            setError(null);

            if (!token) {
                throw new Error('Authentication required');
            }

            const response = await axios.post<GenerateCharacterResponse>(
                '/api/animation/character',
                {
                    prompt,
                    style,
                    attributes: attributes || {}
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            if (response.data.error) {
                throw new Error(response.data.error);
            }

            return response.data;
        } catch (err) {
            const error = err as AxiosError<APIError>;
            const errorMessage = error.response?.data?.message || 
                               error.response?.data?.error || 
                               'Failed to generate character';
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [token]);

    return {
        generateCharacter,
        loading,
        error,
        clearError
    };
};
