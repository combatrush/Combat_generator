import { useState, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from './useAuth';

interface Animation {
    id: number;
    title: string;
    description: string;
    duration: number;
    fps: number;
    resolution: string;
    scene_data: any;
    settings: any;
    status: string;
    render_progress: number;
    output_url: string;
}

interface Track {
    id: string;
    name: string;
    type: 'character' | 'effect' | 'sound';
    keyframes: { time: number; value: any }[];
}

export const useAnimation = () => {
    const [currentAnimation, setCurrentAnimation] = useState<Animation | null>(null);
    const [tracks, setTracks] = useState<Track[]>([]);
    const [currentTime, setCurrentTime] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { token } = useAuth();

    const loadAnimation = useCallback(async (id: number) => {
        try {
            setLoading(true);
            setError(null);

            const response = await axios.get(`/api/animation/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            setCurrentAnimation(response.data);
            setTracks(response.data.scene_data?.tracks || []);
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to load animation');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [token]);

    const saveAnimation = useCallback(async () => {
        if (!currentAnimation) return;

        try {
            setLoading(true);
            setError(null);

            const response = await axios.put(
                `/api/animation/${currentAnimation.id}`,
                {
                    ...currentAnimation,
                    scene_data: { ...currentAnimation.scene_data, tracks }
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setCurrentAnimation(response.data);
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to save animation');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [currentAnimation, tracks, token]);

    const updateKeyframe = useCallback((
        trackId: string,
        time: number,
        value: any
    ) => {
        setTracks(prevTracks => {
            const trackIndex = prevTracks.findIndex(t => t.id === trackId);
            if (trackIndex === -1) return prevTracks;

            const track = prevTracks[trackIndex];
            const keyframeIndex = track.keyframes.findIndex(k => k.time === time);

            const newKeyframes = [...track.keyframes];
            if (keyframeIndex === -1) {
                newKeyframes.push({ time, value });
                newKeyframes.sort((a, b) => a.time - b.time);
            } else {
                newKeyframes[keyframeIndex] = { time, value };
            }

            const newTracks = [...prevTracks];
            newTracks[trackIndex] = { ...track, keyframes: newKeyframes };
            return newTracks;
        });
    }, []);

    const startRendering = useCallback(async () => {
        if (!currentAnimation) return;

        try {
            setLoading(true);
            setError(null);

            const response = await axios.post(
                `/api/animation/${currentAnimation.id}/render`,
                {},
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setCurrentAnimation(prev => prev ? {
                ...prev,
                status: 'rendering',
                render_task_id: response.data.task_id
            } : null);
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to start rendering');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [currentAnimation, token]);

    return {
        currentAnimation,
        tracks,
        currentTime,
        loading,
        error,
        setCurrentTime,
        loadAnimation,
        saveAnimation,
        updateKeyframe,
        startRendering
    };
};
