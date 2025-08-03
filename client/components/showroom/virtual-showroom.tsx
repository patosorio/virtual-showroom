"use client"

import { useState } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ChevronLeft, ChevronRight, ZoomIn, Download } from "lucide-react"
import type { Collection } from "@/types"

interface VirtualShowroomProps {
  collection: Collection
}

export function VirtualShowroom({ collection }: VirtualShowroomProps) {
  const [selectedProductIndex, setSelectedProductIndex] = useState(0)
  const [selectedVariantIndex, setSelectedVariantIndex] = useState(0)

  const currentProduct = collection.products[selectedProductIndex]
  const currentVariant = currentProduct?.variants[selectedVariantIndex]

  const nextProduct = () => {
    if (selectedProductIndex < collection.products.length - 1) {
      setSelectedProductIndex(selectedProductIndex + 1)
      setSelectedVariantIndex(0)
    }
  }

  const prevProduct = () => {
    if (selectedProductIndex > 0) {
      setSelectedProductIndex(selectedProductIndex - 1)
      setSelectedVariantIndex(0)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Fixed Collection Header */}
        <div className="sticky top-0 bg-white z-10 py-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold uppercase tracking-wide text-gray-900">{collection.name}</h1>
          <p className="text-gray-600 mt-2">{collection.description}</p>
        </div>

        {/* Main Content - Scrollable */}
        <div className="py-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Product Selection - Fixed Position */}
            <div className="lg:col-span-1">
              <div className="sticky top-32 space-y-6">
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold uppercase tracking-wide">Collection Items</h2>
                  <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
                    {collection.products.map((product, index) => (
                      <div
                        key={product.id}
                        className={`cursor-pointer rounded-lg border-2 transition-all duration-200 ${
                          index === selectedProductIndex
                            ? "border-gray-900 shadow-lg"
                            : "border-gray-200 hover:border-gray-400"
                        }`}
                        onClick={() => {
                          setSelectedProductIndex(index)
                          setSelectedVariantIndex(0)
                        }}
                      >
                        <div className="aspect-square relative bg-gray-100 rounded-t-lg overflow-hidden">
                          <Image
                            src={
                              product.variants[0]?.images[0] ||
                              `/placeholder.svg?height=150&width=150&query=${product.name || "/placeholder.svg"} ${product.category}`
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

            {/* Main Product Display - Scrollable Content */}
            <div className="lg:col-span-3">
              <div className="space-y-8">
                {currentProduct && (
                  <>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      {/* Product Image */}
                      <div className="relative">
                        <div className="aspect-[3/4] relative bg-gray-100 rounded-lg overflow-hidden">
                          <Image
                            src={
                              currentVariant?.images[0] ||
                              `/placeholder.svg?height=500&width=400&query=${currentProduct.name || "/placeholder.svg"} ${currentVariant?.color} swimwear model`
                            }
                            alt={`${currentProduct.name} - ${currentVariant?.color}`}
                            fill
                            className="object-cover"
                          />
                          <Button
                            size="icon"
                            className="absolute top-4 right-4 bg-white/80 hover:bg-white text-gray-900"
                          >
                            <ZoomIn className="h-4 w-4" />
                          </Button>
                        </div>

                        {/* Navigation Arrows */}
                        <Button
                          size="icon"
                          variant="outline"
                          className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white"
                          onClick={prevProduct}
                          disabled={selectedProductIndex === 0}
                        >
                          <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="outline"
                          className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white"
                          onClick={nextProduct}
                          disabled={selectedProductIndex === collection.products.length - 1}
                        >
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>

                      {/* Product Info */}
                      <div className="space-y-6">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <Badge variant="secondary" className="uppercase text-xs">
                              {currentProduct.category}
                            </Badge>
                            <h2 className="text-2xl font-bold uppercase tracking-wide">{currentProduct.name}</h2>
                            {currentVariant && (
                              <p className="text-gray-600 capitalize">Color: {currentVariant.color}</p>
                            )}
                          </div>
                          <Button className="bg-gray-900 hover:bg-gray-800">
                            <Download className="mr-2 h-4 w-4" />
                            Download Assets
                          </Button>
                        </div>

                        {/* Color Variants */}
                        {currentProduct.variants.length > 1 && (
                          <div className="space-y-3">
                            <h3 className="text-sm font-medium uppercase tracking-wide">Available Colors</h3>
                            <div className="flex gap-3">
                              {currentProduct.variants.map((variant, index) => (
                                <button
                                  key={variant.id}
                                  className={`w-12 h-12 rounded-full border-2 transition-all duration-200 hover:scale-110 ${
                                    index === selectedVariantIndex
                                      ? "border-gray-900 shadow-lg scale-110"
                                      : "border-gray-300"
                                  }`}
                                  style={{ backgroundColor: variant.colorCode }}
                                  onClick={() => setSelectedVariantIndex(index)}
                                  title={variant.color}
                                />
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Product Description */}
                        <div className="prose prose-sm text-gray-600">
                          <p>
                            The {currentProduct.name.toLowerCase()} represents the perfect fusion of modern
                            functionality and timeless elegance. Crafted with premium ECONYL® regenerated nylon, this
                            piece offers both style and sustainability. The thoughtful design ensures comfort and
                            confidence whether you're lounging poolside or diving into ocean adventures.
                          </p>
                        </div>

                        {/* Quick Specs */}
                        <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                          <div className="text-center">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Material</div>
                            <div className="text-sm font-medium">ECONYL® Nylon</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Protection</div>
                            <div className="text-sm font-medium">UPF 50+</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Sizes</div>
                            <div className="text-sm font-medium">XS - XL</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Colors</div>
                            <div className="text-sm font-medium">{currentProduct.variants.length} Available</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Additional Product Information */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <h3 className="text-sm font-medium uppercase tracking-wide">Features</h3>
                        <div className="text-sm text-gray-600 space-y-2">
                          <p>• Premium ECONYL® regenerated nylon construction</p>
                          <p>• UPF 50+ sun protection technology</p>
                          <p>• Chlorine and sun cream resistant</p>
                          <p>• Quick-dry fabric technology</p>
                          <p>• Sustainable and eco-friendly materials</p>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <h3 className="text-sm font-medium uppercase tracking-wide">Fit & Care</h3>
                        <div className="text-sm text-gray-600 space-y-2">
                          <p>• True to size fit</p>
                          <p>• Model is 5'8" wearing size S</p>
                          <p>• Hand wash in cold water</p>
                          <p>• Lay flat to dry</p>
                          <p>• Do not bleach or iron</p>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
