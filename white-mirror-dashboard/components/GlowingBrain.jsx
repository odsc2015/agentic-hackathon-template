import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// Helper to make a random "brain fold" wire
function BrainFold({ seed = 0, color = "#35d0ff", ...props }) {
  const ref = useRef();
  // Generate random curve
  const curve = React.useMemo(() => {
    const points = [];
    let phi = Math.random() * Math.PI * 2 + seed;
    let theta = Math.random() * Math.PI + seed / 2;
    for (let i = 0; i < 60; i++) {
      // Slightly spiral in 3D
      phi += 0.14 + 0.11 * Math.sin(i + seed);
      theta += 0.12 * Math.cos(i + seed / 2);
      const r = 0.98 + 0.13 * Math.sin(i * 0.41 + seed);
      points.push(
        new THREE.Vector3(
          Math.sin(phi) * Math.cos(theta) * r,
          Math.sin(theta) * r,
          Math.cos(phi) * Math.cos(theta) * r
        )
      );
    }
    return new THREE.CatmullRomCurve3(points, false, "catmullrom", 0.1);
  }, [seed]);

  const geometry = React.useMemo(() => {
    const points = curve.getPoints(60);
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [curve]);

  useFrame(({ clock }) => {
    ref.current.material.color.setHSL(0.55 + 0.12 * Math.sin(clock.getElapsedTime() + seed), 1, 0.7);
  });

  return (
    <line ref={ref} geometry={geometry}>
      <lineBasicMaterial attach="material" color={color} linewidth={1.4} />
    </line>
  );
}

// Glowing particle "neural sparks"
function NeuralParticles() {
  const count = 60;
  const positions = React.useMemo(() => {
    const arr = [];
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;
      const r = 0.85 + Math.random() * 0.26;
      arr.push(
        Math.sin(theta) * Math.cos(phi) * r,
        Math.sin(phi) * r,
        Math.cos(theta) * Math.cos(phi) * r
      );
    }
    return new Float32Array(arr);
  }, []);
  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial color="#aefcff" size={0.07} sizeAttenuation />
    </points>
  );
}

export function GlowingBrain() {
  const group = useRef();
  useFrame(({ clock }) => {
    group.current.rotation.y = Math.sin(clock.getElapsedTime() / 2) * 0.25 + Math.PI / 6;
    group.current.rotation.x = Math.sin(clock.getElapsedTime() / 1.2) * 0.12 + Math.PI / 30;
  });

  return (
    <group ref={group}>
      {/* 12 random folds for the brain */}
      {[...Array(13)].map((_, i) => (
        <BrainFold key={i} seed={i * 111} />
      ))}
      {/* Neural particles */}
      <NeuralParticles />
      {/* Glowing torus knot as brain core */}
      <mesh>
        <torusKnotGeometry args={[0.52, 0.19, 110, 5, 2, 3]} />
        <meshStandardMaterial
          color="#2b7fff"
          wireframe
          emissive="#00dfff"
          emissiveIntensity={1.4}
          transparent
          opacity={0.92}
        />
      </mesh>
    </group>
  );
}
