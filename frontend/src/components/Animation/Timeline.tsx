import React, { useState, useRef, useEffect } from 'react';
import { Box, Paper, IconButton, Slider, Typography } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import { useAnimation } from '../../hooks/useAnimation';

interface Track {
    id: string;
    name: string;
    type: 'character' | 'effect' | 'sound';
    keyframes: { time: number; value: any }[];
}

export const Timeline: React.FC = () => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(30); // seconds
    const animationRef = useRef<number>();
    const { tracks, updateKeyframe } = useAnimation();

    const startAnimation = () => {
        if (!isPlaying) {
            setIsPlaying(true);
            animationRef.current = requestAnimationFrame(animate);
        }
    };

    const stopAnimation = () => {
        if (isPlaying) {
            setIsPlaying(false);
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        }
    };

    const animate = (timestamp: number) => {
        // Animation logic here
        setCurrentTime((prevTime) => {
            const newTime = prevTime + 0.016; // 60fps
            if (newTime >= duration) {
                stopAnimation();
                return 0;
            }
            return newTime;
        });
        animationRef.current = requestAnimationFrame(animate);
    };

    const handleTimeChange = (event: Event, newValue: number | number[]) => {
        setCurrentTime(newValue as number);
    };

    return (
        <Paper sx={{ p: 2, mt: 'auto' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <IconButton onClick={isPlaying ? stopAnimation : startAnimation}>
                    {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                </IconButton>
                <Typography sx={{ ml: 2 }}>
                    {Math.floor(currentTime / 60)}:
                    {Math.floor(currentTime % 60)
                        .toString()
                        .padStart(2, '0')}
                </Typography>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {tracks?.map((track: Track) => (
                    <Box
                        key={track.id}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                        }}
                    >
                        <Typography sx={{ width: 100 }}>{track.name}</Typography>
                        <Box sx={{ flexGrow: 1 }}>
                            <Slider
                                value={currentTime}
                                max={duration}
                                onChange={handleTimeChange}
                                aria-labelledby="timeline-slider"
                            />
                        </Box>
                    </Box>
                ))}
            </Box>
        </Paper>
    );
};
