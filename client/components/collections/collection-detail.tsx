"use client"

import { ProductShowcase } from "@/components/products/product-showcase"
import type { Collection } from "@/types/collections"

interface CollectionDetailProps {
  collection: Collection
}

export function CollectionDetail({ collection }: CollectionDetailProps) {
  return (
    <div className="min-h-screen bg-white">
      <ProductShowcase collection={collection} />
    </div>
  )
}
