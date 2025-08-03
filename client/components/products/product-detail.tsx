"use client"

import { useState } from "react"
import { ColorVariantSelector } from "./color-variant-selector"
import { SpecificationPanel } from "./specification-panel"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Product } from "@/types"
import { Download, FileText } from "lucide-react"

interface ProductDetailProps {
  product: Product
}

export function ProductDetail({ product }: ProductDetailProps) {
  const [selectedVariant, setSelectedVariant] = useState(product.variants[0])

  return (
    <div className="space-y-8">
      {/* Product Header */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="uppercase text-xs">
            {product.category}
          </Badge>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 uppercase tracking-wide">{product.name}</h1>
      </div>

      {/* Color Variants */}
      <ColorVariantSelector
        variants={product.variants}
        selectedVariant={selectedVariant}
        onVariantChange={setSelectedVariant}
      />

      {/* Product Description */}
      <div className="prose prose-sm text-gray-600">
        <p>
          The head-turning {product.name.toLowerCase()} fuses modern functionality with retro elegance - and the spirit
          of adventure. Pretty yet practical, the triangle-style top features signature rubber-coated bronze buckles on
          the front-fastening band and on the straps - ensuring it fits and supports. Bust darts and side stays further
          enhance the silhouette.
        </p>
      </div>

      {/* Technical Specifications */}
      <SpecificationPanel specifications={product.specifications} />

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Button className="flex-1 bg-gray-900 hover:bg-gray-800">
          <FileText className="mr-2 h-4 w-4" />
          View Technical File
        </Button>
        <Button variant="outline" className="flex-1 bg-transparent">
          <Download className="mr-2 h-4 w-4" />
          Download Assets
        </Button>
      </div>
    </div>
  )
}
