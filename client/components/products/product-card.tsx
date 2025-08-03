"use client"

import Image from "next/image"
import type { Product } from "@/types"
import { cn } from "@/lib/utils"

interface ProductCardProps {
  product: Product
  isSelected?: boolean
  onClick?: () => void
}

export function ProductCard({ product, isSelected, onClick }: ProductCardProps) {
  const primaryImage =
    product.variants[0]?.images[0] ||
    `/placeholder.svg?height=200&width=200&query=${product.name} ${product.category} flat lay`

  return (
    <div
      className={cn(
        "group cursor-pointer rounded-lg overflow-hidden transition-all duration-200",
        "hover:shadow-lg hover:scale-105",
        isSelected && "ring-2 ring-blue-500 shadow-lg",
      )}
      onClick={onClick}
    >
      <div className="aspect-square relative bg-gray-100">
        <Image
          src={primaryImage || "/placeholder.svg"}
          alt={product.name}
          fill
          className="object-cover transition-transform duration-200 group-hover:scale-110"
        />
      </div>
      <div className="p-3 bg-white">
        <h3 className="font-medium text-sm text-gray-900 truncate">{product.name}</h3>
        <p className="text-xs text-gray-500 capitalize">{product.category}</p>
      </div>
    </div>
  )
}
