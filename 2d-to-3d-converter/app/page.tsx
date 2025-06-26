"use client"

import { useState } from "react"
import { Upload, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import ImageUploader from "@/components/image-uploader"
import ModelViewer from "@/components/model-viewer"
import ProcessingStatus from "@/components/processing-status"
import api, { ConversionOptions } from "@/lib/api"
import { toast } from "sonner"

export default function Home() {
  const [image, setImage] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [modelReady, setModelReady] = useState(false)
  const [processingStep, setProcessingStep] = useState<string>("")
  const [conversionResult, setConversionResult] = useState<any>(null)
  const [conversionOptions, setConversionOptions] = useState<ConversionOptions>({
    model_type: 'mesh',
    quality: 'medium'
  })

  const handleImageUpload = (imageDataUrl: string) => {
    setImage(imageDataUrl)
    setModelReady(false)
    setConversionResult(null)
  }

  const convertTo3D = async () => {
    if (!image) return

    setIsProcessing(true)
    setModelReady(false)
    setConversionResult(null)

    try {
      setProcessingStep("Converting image to file...")
      const file = await api.base64ToFile(image)
      
      setProcessingStep("Analyzing image structure...")
      await new Promise((resolve) => setTimeout(resolve, 1000))

      setProcessingStep("Generating depth map...")
      await new Promise((resolve) => setTimeout(resolve, 1500))

      setProcessingStep("Running 3D reconstruction model...")
      await new Promise((resolve) => setTimeout(resolve, 2000))

      setProcessingStep("Creating 3D mesh...")
      const result = await api.convertImage(file, conversionOptions)
      
      setProcessingStep("Finalizing model...")
      await new Promise((resolve) => setTimeout(resolve, 1000))

      setConversionResult(result)
      setIsProcessing(false)
      setModelReady(true)
      
      toast.success("3D model generated successfully!")
      
    } catch (error) {
      console.error('Conversion failed:', error)
      setIsProcessing(false)
      toast.error("Failed to convert image to 3D model. Please try again.")
    }
  }

  const downloadModel = async () => {
    if (!conversionResult) return
    
    try {
      const blob = await api.downloadModel(conversionResult.file_name)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = conversionResult.file_name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success("Model downloaded successfully!")
    } catch (error) {
      console.error('Download failed:', error)
      toast.error("Failed to download model. Please try again.")
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 md:p-24 bg-gray-50">
      <h1 className="text-3xl font-bold mb-8 text-center">2D to 3D Image Converter</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-6xl">
        <div className="flex flex-col gap-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Upload 2D Image</h2>
            <ImageUploader onImageUpload={handleImageUpload} />

            {image && (
              <div className="mt-4 space-y-4">
                <h3 className="text-lg font-medium mb-2">Preview</h3>
                <div className="relative rounded-md overflow-hidden border border-gray-200 aspect-square">
                  <img
                    src={image || "/placeholder.svg"}
                    alt="Uploaded preview"
                    className="w-full h-full object-contain"
                  />
                </div>
                
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="model-type">Model Type</Label>
                    <Select 
                      value={conversionOptions.model_type} 
                      onValueChange={(value: any) => setConversionOptions(prev => ({ ...prev, model_type: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mesh">3D Mesh</SelectItem>
                        <SelectItem value="point_cloud">Point Cloud</SelectItem>
                        <SelectItem value="textured">Textured Model</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="quality">Quality</Label>
                    <Select 
                      value={conversionOptions.quality} 
                      onValueChange={(value: any) => setConversionOptions(prev => ({ ...prev, quality: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low (Fast)</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High (Slow)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button className="w-full" onClick={convertTo3D} disabled={isProcessing}>
                  <Upload className="mr-2 h-4 w-4" />
                  Convert to 3D
                </Button>
              </div>
            )}
          </Card>
        </div>

        <div className="flex flex-col gap-4">
          <Card className="p-6 h-full flex flex-col">
            <h2 className="text-xl font-semibold mb-4">3D Model Output</h2>

            {isProcessing ? (
              <ProcessingStatus step={processingStep} />
            ) : modelReady ? (
              <div className="flex-1 flex flex-col">
                <div className="flex-1 min-h-[400px] mb-4">
                  <ModelViewer imageUrl={image} />
                </div>
                
                {conversionResult && (
                  <div className="space-y-3 p-4 bg-gray-50 rounded-md">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Model Type:</span>
                      <span className="font-medium capitalize">{conversionResult.model_type}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Quality:</span>
                      <span className="font-medium capitalize">{conversionResult.quality}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">File Size:</span>
                      <span className="font-medium">{(conversionResult.file_size / 1024).toFixed(1)} KB</span>
                    </div>
                    <Button className="w-full" onClick={downloadModel}>
                      <Download className="mr-2 h-4 w-4" />
                      Download Model
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center border border-dashed border-gray-300 rounded-md bg-gray-50 min-h-[400px]">
                <p className="text-gray-500 text-center">
                  {image ? "Click 'Convert to 3D' to generate model" : "Upload an image to get started"}
                </p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </main>
  )
}
