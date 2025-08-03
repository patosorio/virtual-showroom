import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { ProductDetail } from "@/components/products/product-detail"
import { mockProducts } from "@/lib/mock-data"
import { notFound } from "next/navigation"

interface ProductPageProps {
  params: {
    slug: string
  }
}

export default function ProductPage({ params }: ProductPageProps) {
  const product = mockProducts.find((p) => p.id === params.slug)

  if (!product) {
    notFound()
  }

  return (
    <ShowroomLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="space-y-6">
            <div className="aspect-[4/5] relative rounded-lg overflow-hidden bg-gray-100">
              <img
                src={product.images[0]?.url || "/placeholder.svg?height=600&width=480"}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>
          </div>
          <div>
            <ProductDetail product={product} />
          </div>
        </div>
      </div>
    </ShowroomLayout>
  )
}
