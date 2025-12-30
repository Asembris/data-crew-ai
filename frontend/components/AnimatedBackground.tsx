'use client';

import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function StarField() {
    const ref = useRef<THREE.Points>(null);

    // Generate random star positions
    const positions = new Float32Array(3000);
    for (let i = 0; i < 3000; i++) {
        positions[i] = (Math.random() - 0.5) * 20;
    }

    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.x -= delta * 0.05;
            ref.current.rotation.y -= delta * 0.02;
        }
    });

    return (
        <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
            <PointMaterial
                transparent
                color="#8b5cf6"
                size={0.02}
                sizeAttenuation={true}
                depthWrite={false}
            />
        </Points>
    );
}

function FloatingOrbs() {
    const group = useRef<THREE.Group>(null);

    useFrame((state) => {
        if (group.current) {
            group.current.rotation.y = state.clock.elapsedTime * 0.1;
        }
    });

    return (
        <group ref={group}>
            {[...Array(5)].map((_, i) => (
                <mesh
                    key={i}
                    position={[
                        Math.sin(i * 1.2) * 3,
                        Math.cos(i * 0.8) * 2,
                        Math.sin(i * 0.5) * 2 - 5
                    ]}
                >
                    <sphereGeometry args={[0.15 + i * 0.05, 16, 16]} />
                    <meshBasicMaterial
                        color={i % 2 === 0 ? '#8b5cf6' : '#3b82f6'}
                        transparent
                        opacity={0.3}
                    />
                </mesh>
            ))}
        </group>
    );
}

export default function AnimatedBackground() {
    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: 0,
            pointerEvents: 'none',
        }}>
            <Canvas
                camera={{ position: [0, 0, 5], fov: 60 }}
                style={{ background: 'transparent', pointerEvents: 'none' }}
            >
                <ambientLight intensity={0.5} />
                <StarField />
                <FloatingOrbs />
            </Canvas>
        </div>
    );
}
