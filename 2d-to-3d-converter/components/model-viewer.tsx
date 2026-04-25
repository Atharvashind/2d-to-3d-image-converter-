"use client"

import { useEffect, useState, Suspense } from "react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls, Environment, useProgress, Html } from "@react-three/drei"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"
import * as THREE from "three"
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"

interface ModelViewerProps {
  modelPath: string | null
  imageUrl: string | null
  onDownload?: () => void
}

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="text-white text-sm bg-black/60 px-3 py-1 rounded">
        Loading {Math.round(progress)}%
      </div>
    </Html>
  )
}

function GLBModel({ url }: { url: string }) {
  const [scene, setScene] = useState<THREE.Group | null>(null)

  useEffect(() => {
    const loader = new GLTFLoader()
    loader.load(
      url,
      (gltf) => {
        const model = gltf.scene

        // Step 1: scale to fit in 2 units
        const box1 = new THREE.Box3().setFromObject(model)
        const size = box1.getSize(new THREE.Vector3())
        const maxDim = Math.max(size.x, size.y, size.z) || 1
        model.scale.setScalar(2.0 / maxDim)

        // TripoSR Y-up, just need to flip 180° around Y to face camera
        model.rotation.set(0, Math.PI, 0)

        // Step 2: after scaling+rotation, re-center so bottom sits at Y=0
        const box2 = new THREE.Box3().setFromObject(model)
        const center2 = box2.getCenter(new THREE.Vector3())
        model.position.set(-center2.x, -box2.min.y, -center2.z)

        model.traverse((child) => {
          if ((child as THREE.Mesh).isMesh) {
            child.castShadow = true
            child.receiveShadow = true
          }
        })

        setScene(model)
      },
      undefined,
      (err) => console.error("GLB load error:", err)
    )
  }, [url])

  if (!scene) return null
  return <primitive object={scene} />
}

export default function ModelViewer({ modelPath, imageUrl, onDownload }: ModelViewerProps) {
  return (
    <div className="relative h-full flex flex-col">
      {onDownload && (
        <div className="absolute top-2 right-2 z-10">
          <Button variant="outline" size="sm" className="bg-white" onClick={onDownload}>
            <Download className="h-4 w-4 mr-1" />
            Download GLB
          </Button>
        </div>
      )}

      <div className="flex-1 min-h-[450px] bg-[#3a3a3a] rounded-md overflow-hidden">
        {modelPath ? (
          <Canvas
            shadows
            gl={{ antialias: true }}
            camera={{ position: [0, 1.2, 3.5], fov: 45, near: 0.01, far: 100 }}
            style={{ background: "#4a4a4a" }}
          >
            <ambientLight intensity={1.5} />
            <directionalLight position={[3, 5, 3]} intensity={2.0} castShadow />
            <directionalLight position={[-3, 2, -2]} intensity={1.0} />
            <directionalLight position={[0, 3, -5]} intensity={0.8} />
            <pointLight position={[0, 2, 3]} intensity={1.0} />

            <Environment preset="studio" />

            {/* Grid floor at Y=0 */}
            <gridHelper args={[8, 24, "#555", "#333"]} position={[0, 0, 0]} />

            <Suspense fallback={<Loader />}>
              <GLBModel url={modelPath} />
            </Suspense>

            <OrbitControls
              makeDefault
              autoRotate={false}
              enableZoom
              enablePan
              minDistance={1}
              maxDistance={12}
              target={[0, 1, 0]}
            />
          </Canvas>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <p className="text-gray-400">3D model will appear here after conversion</p>
          </div>
        )}
      </div>

      {modelPath && (
        <p className="text-xs text-center text-gray-400 mt-2">
          Drag to rotate · Scroll to zoom · Right-click to pan
        </p>
      )}
    </div>
  )
}
