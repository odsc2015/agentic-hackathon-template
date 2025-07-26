import React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera } from "@react-three/drei";
import { GlowingBrain } from "./GlowingBrain"; // or paste above in same file

export default function DigitalBrain() {
  return (
    <Canvas style={{ width: "100%", height: "100%", background: "transparent" }}>
      <PerspectiveCamera makeDefault position={[0, 0, 5.5]} fov={45} />
      <ambientLight intensity={0.8} />
      <pointLight position={[8, 6, 12]} intensity={1.2} color="#b4e0ff" />
      <GlowingBrain />
      <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />
    </Canvas>
  );
}
