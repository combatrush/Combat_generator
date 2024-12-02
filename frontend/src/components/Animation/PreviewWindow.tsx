import React, { useRef, useEffect } from 'react';
import { Box, Paper } from '@mui/material';
import { useAnimation } from '../../hooks/useAnimation';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export const PreviewWindow: React.FC = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const { currentAnimation, currentTime } = useAnimation();
    
    useEffect(() => {
        if (!containerRef.current) return;
        
        // Set up Three.js scene
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(
            75,
            containerRef.current.clientWidth / containerRef.current.clientHeight,
            0.1,
            1000
        );
        
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(
            containerRef.current.clientWidth,
            containerRef.current.clientHeight
        );
        containerRef.current.appendChild(renderer.domElement);
        
        // Add orbit controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        
        // Set up basic scene
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(0, 1, 0);
        scene.add(directionalLight);
        
        camera.position.z = 5;
        
        // Animation loop
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        
        animate();
        
        // Handle window resize
        const handleResize = () => {
            if (!containerRef.current) return;
            
            camera.aspect =
                containerRef.current.clientWidth / containerRef.current.clientHeight;
            camera.updateProjectionMatrix();
            
            renderer.setSize(
                containerRef.current.clientWidth,
                containerRef.current.clientHeight
            );
        };
        
        window.addEventListener('resize', handleResize);
        
        // Update scene based on animation data
        if (currentAnimation) {
            // Clear existing objects
            while (scene.children.length > 0) {
                scene.remove(scene.children[0]);
            }
            
            // Add new objects based on animation data
            // This is where you would add your characters, effects, etc.
            // based on the currentAnimation.scene_data
        }
        
        return () => {
            if (containerRef.current) {
                containerRef.current.removeChild(renderer.domElement);
            }
            window.removeEventListener('resize', handleResize);
        };
    }, [currentAnimation, currentTime]);
    
    return (
        <Box
            ref={containerRef}
            sx={{
                width: '100%',
                height: 'calc(100% - 200px)', // Adjust based on timeline height
                bgcolor: 'background.default',
            }}
        />
    );
};
