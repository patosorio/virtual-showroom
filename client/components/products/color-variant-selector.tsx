"use client"

import type { ProductVariant } from "@/types"
import { cn } from "@/lib/utils"

interface ColorVariantSelectorProps {
  variants: ProductVariant[]
  selectedVariant: ProductVariant
  onVariantChange: (variant: ProductVariant) => void
}

export function ColorVariantSelector({ variants, selectedVariant, onVariantChange }: ColorVariantSelectorProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-900 uppercase tracking-wide">Color Options</h3>
      <div className="flex flex-wrap gap-3">
        {variants.map((variant) => (
          <button
            key={variant.id}
            className={cn(
              "w-12 h-12 rounded-full border-2 transition-all duration-200",
              "hover:scale-110 hover:shadow-md",
              selectedVariant.id === variant.id ? "border-gray-900 shadow-lg scale-110" : "border-gray-300",
            )}
            style={{ backgroundColor: variant.colorCode }}
            onClick={() => onVariantChange(variant)}
            title={variant.color}
          />
        ))}
      </div>
      <p className="text-sm text-gray-600">
        Selected: <span className="font-medium capitalize">{selectedVariant.color}</span>
      </p>
    </div>
  )
}
