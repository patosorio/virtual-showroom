"use client"

import { useState } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, Ruler } from "lucide-react"
import type { Collection } from "@/types/collections"

interface TechnicalFilesViewerProps {
  collection: Collection
}

export function TechnicalFilesViewer({ collection }: TechnicalFilesViewerProps) {
  const [selectedProductIndex, setSelectedProductIndex] = useState(0)
  const [selectedView, setSelectedView] = useState<"front" | "back" | "side">("front")

  const currentProduct = collection.products[selectedProductIndex]

  const technicalViews = {
    front: `/placeholder.svg?height=400&width=300&query=${currentProduct?.name} technical drawing front view flat`,
    back: `/placeholder.svg?height=400&width=300&query=${currentProduct?.name} technical drawing back view flat`,
    side: `/placeholder.svg?height=400&width=300&query=${currentProduct?.name} technical drawing side view flat`,
  }

  const sizeChart = [
    { size: "XS", uk: "6", eu: "34", us: "2", bust: "32", waist: "24", hip: "34" },
    { size: "S", uk: "8", eu: "36", us: "4", bust: "34", waist: "26", hip: "36" },
    { size: "M", uk: "10", eu: "38", us: "6", bust: "36", waist: "28", hip: "38" },
    { size: "L", uk: "12", eu: "40", us: "8", bust: "38", waist: "30", hip: "40" },
    { size: "XL", uk: "14", eu: "42", us: "10", bust: "40", waist: "32", hip: "42" },
  ]

  if (!currentProduct) return null

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Fixed Collection Header */}
        <div className="sticky top-0 bg-white z-10 py-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold uppercase tracking-wide text-gray-900">{collection.name}</h1>
          <p className="text-gray-600 mt-2">Technical specifications and drawings</p>
        </div>

        {/* Main Content - Scrollable */}
        <div className="py-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Product Selection - Fixed Position */}
            <div className="lg:col-span-1">
              <div className="sticky top-32 space-y-6">
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold uppercase tracking-wide">Select Product</h2>
                  <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
                    {collection.products.map((product, index) => (
                      <div
                        key={product.id}
                        className={`cursor-pointer rounded-lg border-2 transition-all duration-200 ${
                          index === selectedProductIndex
                            ? "border-gray-900 shadow-lg"
                            : "border-gray-200 hover:border-gray-400"
                        }`}
                        onClick={() => setSelectedProductIndex(index)}
                      >
                        <div className="aspect-square relative bg-gray-100 rounded-t-lg overflow-hidden">
                          <Image
                            src={
                              product.variants[0]?.images[0] ||
                              `/placeholder.svg?height=150&width=150&query=${product.name || "/placeholder.svg"} ${product.category} technical`
                            }
                            alt={product.name}
                            fill
                            className="object-cover"
                          />
                        </div>
                        <div className="p-3">
                          <h3 className="font-medium text-sm uppercase tracking-wide">{product.name}</h3>
                          <p className="text-xs text-gray-500 capitalize">{product.category}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Technical Details - Scrollable Content */}
            <div className="lg:col-span-3">
              <div className="space-y-8">
                {/* Product Header */}
                <div className="flex items-center justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-blue-900 text-white border-blue-900">
                        COLOR 05/21
                      </Badge>
                      <Badge variant="outline" className="bg-blue-900 text-white border-blue-900">
                        {currentProduct.variants[0]?.color.toUpperCase() || "PRIMARY"}
                      </Badge>
                    </div>
                    <h2 className="text-2xl font-bold uppercase tracking-wide">{currentProduct.name}</h2>
                    <p className="text-sm text-gray-600 uppercase">{currentProduct.category}</p>
                  </div>
                  <Button className="bg-gray-900 hover:bg-gray-800">
                    <Download className="mr-2 h-4 w-4" />
                    Download Tech Pack
                  </Button>
                </div>

                {/* Technical Drawings */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <h3 className="text-sm font-medium uppercase tracking-wide">Technical Drawings</h3>
                    <div className="bg-gray-50 rounded-lg p-6">
                      <Image
                        src={technicalViews[selectedView] || "/placeholder.svg"}
                        alt={`${currentProduct.name} ${selectedView} view`}
                        width={300}
                        height={400}
                        className="w-full h-64 object-contain"
                      />
                    </div>
                    <div className="flex gap-2">
                      {(["front", "back", "side"] as const).map((view) => (
                        <Button
                          key={view}
                          variant={selectedView === view ? "default" : "outline"}
                          size="sm"
                          onClick={() => setSelectedView(view)}
                          className="capitalize"
                        >
                          {view}
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Specifications */}
                  <div className="space-y-6">
                    {/* Material Info */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium uppercase tracking-wide">Material Specifications</h3>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>Made with ECONYL® regenerated Nylon</p>
                        <p>78% Recycled PA</p>
                        <p>22% EA</p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <Badge variant="secondary" className="text-xs">
                            UPF 50+
                          </Badge>
                          <span className="text-gray-600">Sun protection</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <Badge variant="secondary" className="text-xs">
                            SUN CREAM TESTED
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <Badge variant="secondary" className="text-xs">
                            CHLORINE PROOF
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {/* Construction Details */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium uppercase tracking-wide">Construction</h3>
                      <div className="text-sm text-gray-600 space-y-2">
                        <div>
                          <span className="font-medium">TOP:</span> Top with double fabric. Front straps adjustable in 5
                          positions with embroidered eyelets. Custom rubber-coated bronze buckles.
                        </div>
                        <div>
                          <span className="font-medium">BOTTOM:</span> Double fabric offers extra support. Low-cut leg.
                          Low-rise waist. Two belts with 3 position embroidered eyelets.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Size Chart - Full Width */}
                <div className="space-y-4">
                  <h3 className="text-sm font-medium uppercase tracking-wide flex items-center gap-2">
                    <Ruler className="h-4 w-4" />
                    Size Chart
                  </h3>
                  <div className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-4 py-2 text-xs font-medium uppercase tracking-wide text-gray-700">
                      International Sizing
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium">Size</th>
                            <th className="px-3 py-2 text-left font-medium">UK</th>
                            <th className="px-3 py-2 text-left font-medium">EU</th>
                            <th className="px-3 py-2 text-left font-medium">US</th>
                            <th className="px-3 py-2 text-left font-medium">Bust</th>
                            <th className="px-3 py-2 text-left font-medium">Waist</th>
                            <th className="px-3 py-2 text-left font-medium">Hip</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {sizeChart.map((row) => (
                            <tr key={row.size} className="hover:bg-gray-50">
                              <td className="px-3 py-2 font-medium">{row.size}</td>
                              <td className="px-3 py-2">{row.uk}</td>
                              <td className="px-3 py-2">{row.eu}</td>
                              <td className="px-3 py-2">{row.us}</td>
                              <td className="px-3 py-2">{row.bust}"</td>
                              <td className="px-3 py-2">{row.waist}"</td>
                              <td className="px-3 py-2">{row.hip}"</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* Additional Technical Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <h3 className="text-sm font-medium uppercase tracking-wide">Care Instructions</h3>
                    <div className="text-sm text-gray-600 space-y-2">
                      <p>• Hand wash in cold water</p>
                      <p>• Do not bleach</p>
                      <p>• Lay flat to dry</p>
                      <p>• Do not iron</p>
                      <p>• Do not dry clean</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-sm font-medium uppercase tracking-wide">Sustainability</h3>
                    <div className="text-sm text-gray-600 space-y-2">
                      <p>• Made from recycled ocean plastic</p>
                      <p>• ECONYL® regenerated nylon</p>
                      <p>• Fully recyclable at end of life</p>
                      <p>• Carbon neutral shipping</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
