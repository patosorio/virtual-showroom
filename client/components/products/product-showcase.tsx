"use client"

import { useState } from "react"
import Image from "next/image"
import { ProductCard } from "./product-card"
import { ProductDetail } from "./product-detail"
import type { Collection, Product } from "@/types"

interface ProductShowcaseProps {
  collection: Collection
}

export function ProductShowcase({ collection }: ProductShowcaseProps) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(collection.products[0] || null)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Product Image */}
        <div className="space-y-6">
          {selectedProduct && (
            <div className="aspect-[4/5] relative rounded-lg overflow-hidden bg-gray-100">
              <Image
                src={
                  selectedProduct.variants[0]?.images[0] ||
                  "/placeholder.svg?height=600&width=480&query=swimwear model beach lifestyle"
                }
                alt={selectedProduct.name}
                fill
                className="object-cover"
                priority
              />
            </div>
          )}

          {/* Product Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {collection.products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                isSelected={selectedProduct?.id === product.id}
                onClick={() => setSelectedProduct(product)}
              />
            ))}
          </div>
        </div>

        {/* Product Details */}
        <div className="space-y-8">{selectedProduct && <ProductDetail product={selectedProduct} />}</div>
      </div>
    </div>
  )
}
