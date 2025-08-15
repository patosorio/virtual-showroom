"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, ZoomIn, ZoomOut, Maximize2 } from "lucide-react"
import type { Collection } from "@/types/collections"

interface LookbookGalleryProps {
  collection: Collection
}

export function LookbookGallery({ collection }: LookbookGalleryProps) {
  const [zoom, setZoom] = useState(100)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Mock PDF pages - in real implementation, these would be generated from actual PDF
  const pdfPages = [
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook cover page fashion editorial`,
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook page 2 swimwear collection`,
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook page 3 beach lifestyle photography`,
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook page 4 product details technical`,
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook page 5 model photography beach`,
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook page 6 collection overview grid`,
    `/placeholder.svg?height=1200&width=850&query=${collection.name} lookbook back cover contact information`,
  ]

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 25, 200))
  }

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 25, 50))
  }

  const handleDownload = () => {
    // In real implementation, this would download the actual PDF
    console.log(`Downloading ${collection.name} lookbook PDF`)
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Fixed Header with Controls */}
        <div className="sticky top-0 bg-white z-10 py-6 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold uppercase tracking-wide text-gray-900">
                  {collection.name}
                </h1>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="outline" className="text-xs">
                    {collection.season} {collection.year}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    Lookbook PDF
                  </Badge>
                </div>
              </div>
            </div>

            {/* PDF Controls */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
                <Button variant="ghost" size="sm" onClick={handleZoomOut} disabled={zoom <= 50} className="h-8 w-8 p-0">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <span className="text-sm font-medium px-2 min-w-[60px] text-center">{zoom}%</span>
                <Button variant="ghost" size="sm" onClick={handleZoomIn} disabled={zoom >= 200} className="h-8 w-8 p-0">
                  <ZoomIn className="h-4 w-4" />
                </Button>
              </div>

              <Button variant="outline" size="sm" onClick={toggleFullscreen} className="bg-transparent">
                <Maximize2 className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">Fullscreen</span>
              </Button>

              <Button onClick={handleDownload} className="bg-gray-900 hover:bg-gray-800">
                <Download className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">Download PDF</span>
              </Button>
            </div>
          </div>
        </div>

        {/* PDF Viewer */}
        <div className={`py-8 ${isFullscreen ? "fixed inset-0 bg-white z-50 pt-20" : ""}`}>
          {isFullscreen && (
            <Button variant="outline" onClick={toggleFullscreen} className="fixed top-4 right-4 z-50 bg-white">
              Exit Fullscreen
            </Button>
          )}

          <div className="space-y-8">
            {pdfPages.map((pageUrl, index) => (
              <div
                key={index}
                className="flex justify-center"
                style={{ transform: `scale(${zoom / 100})`, transformOrigin: "top center" }}
              >
                <div className="bg-white shadow-2xl rounded-lg overflow-hidden max-w-full">
                  {/* Page Number */}
                  <div className="bg-gray-100 px-4 py-2 text-center">
                    <span className="text-sm text-gray-600 font-medium">
                      Page {index + 1} of {pdfPages.length}
                    </span>
                  </div>

                  {/* PDF Page Content */}
                  <div className="relative">
                    <img
                      src={pageUrl || "/placeholder.svg"}
                      alt={`${collection.name} Lookbook - Page ${index + 1}`}
                      className="w-full h-auto max-w-[850px] block"
                      style={{ aspectRatio: "850/1200" }}
                    />

                    {/* Page Loading Overlay */}
                    <div className="absolute inset-0 bg-gray-100 animate-pulse opacity-0 transition-opacity duration-300" />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* PDF Info Footer */}
          <div className="mt-12 text-center text-gray-500 text-sm">
            <p>End of {collection.name} Lookbook</p>
            <p className="mt-2">
              {pdfPages.length} pages • {collection.season} {collection.year} Collection
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
