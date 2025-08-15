"use client"

import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { Plus, Eye, Ruler, BookOpen, Calendar, Package, AlertCircle, RefreshCw } from "lucide-react"
import { useCollections } from "@/hooks/useCollections"
import { transformCollectionsList } from "@/lib/transformers/collections"
import type { Collection } from "@/types/collections"

export function CollectionsGrid() {
  const { 
    data: collectionsResponse, 
    isLoading, 
    error, 
    refetch 
  } = useCollections({
    limit: 20,
    is_published: true, // Only show published collections for non-admin users
  })

  const collections = collectionsResponse?.items ? transformCollectionsList(collectionsResponse.items) : []

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex flex-col h-full">

        <div className="flex-shrink-0 py-4 sm:py-6 lg:py-8 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold uppercase tracking-wide text-gray-900">
                Collections
              </h1>
              <p className="text-gray-600 mt-1 sm:mt-2 text-sm sm:text-base lg:text-lg">
                Explore our fashion collections and virtual showrooms
              </p>
            </div>
            <Link href="/admin/collections/new" className="w-full sm:w-auto">
              <Button className="bg-gray-900 hover:bg-gray-800 text-white px-4 sm:px-6 py-2 sm:py-3 w-full sm:w-auto">
                <Plus className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                Add Collection
              </Button>
            </Link>
          </div>
        </div>

        {/* Collections Grid - Mobile First */}
        <div className="flex-1 py-4 sm:py-6 lg:py-8 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-gray-600">Loading collections...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Unable to connect to server
                </h3>
                <p className="text-gray-600 mb-4">
                  There's a connection issue with the backend server. Please check if the server is running and try again.
                </p>
                <div className="space-y-2">
                  <Button 
                    onClick={() => refetch()} 
                    className="bg-gray-900 hover:bg-gray-800 w-full"
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Try Again
                  </Button>
                  <p className="text-xs text-gray-500">
                    Error: {error?.message || 'Network connection failed'}
                  </p>
                </div>
              </div>
            </div>
          ) : collections.length === 0 ? (
            <div className="flex items-center justify-center h-full min-h-[60vh]">
              <div className="text-center max-w-lg px-6">
                {/* Beautiful Empty State Icon */}
                <div className="relative mb-8">
                  <div className="w-24 h-24 mx-auto bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center">
                    <Package className="h-12 w-12 text-gray-400" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center">
                    <Plus className="h-4 w-4 text-white" />
                  </div>
                </div>

                {/* Engaging Copy */}
                <h3 className="text-2xl font-bold text-gray-900 mb-3">
                  Ready to showcase your collections?
                </h3>
                <p className="text-gray-600 mb-8 leading-relaxed">
                  Transform your fashion designs into immersive digital experiences. 
                  Create your first collection and start building your virtual showroom.
                </p>

                {/* Primary CTA */}
                <div className="space-y-4">
                  <Link href="/admin/collections/new">
                    <Button className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-3 text-lg font-medium rounded-lg shadow-lg hover:shadow-xl transition-all duration-300">
                      <Plus className="mr-3 h-5 w-5" />
                      Create Your First Collection
                    </Button>
                  </Link>
                  
                  {/* Secondary info */}
                  <p className="text-sm text-gray-500">
                    You can upload products, technical files, and create stunning lookbooks
                  </p>
                </div>

                {/* Feature highlights */}
                <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
                  <div className="space-y-2">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg mx-auto flex items-center justify-center">
                      <Eye className="h-6 w-6 text-gray-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Virtual Showroom</h4>
                    <p className="text-sm text-gray-500">Interactive product displays</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg mx-auto flex items-center justify-center">
                      <Ruler className="h-6 w-6 text-gray-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Technical Files</h4>
                    <p className="text-sm text-gray-500">Detailed specifications</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg mx-auto flex items-center justify-center">
                      <BookOpen className="h-6 w-6 text-gray-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Lookbooks</h4>
                    <p className="text-sm text-gray-500">Beautiful galleries</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
              {collections.map((collection) => (
                <CollectionCard key={collection.id} collection={collection} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface CollectionCardProps {
  collection: Collection
}

function CollectionCard({ collection }: CollectionCardProps) {
  // Get the first product image as collection preview
  const previewImage =
    collection.products[0]?.variants[0]?.images[0] ||
    `/placeholder.svg?height=400&width=300&query=${collection.name} collection preview fashion`

  return (
    <Card className="group hover:shadow-xl transition-all duration-300 overflow-hidden h-full flex flex-col">
      <div className="relative flex-shrink-0">
        {/* Collection Preview Image - Responsive aspect ratio */}
        <div className="aspect-[3/4] sm:aspect-[4/5] relative bg-gray-100 overflow-hidden">
          <Image
            src={previewImage || "/placeholder.svg"}
            alt={collection.name}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300" />

          {/* Collection Badge - Mobile optimized */}
          <div className="absolute top-3 sm:top-4 left-3 sm:left-4">
            <Badge className="bg-white/90 text-gray-900 hover:bg-white text-xs sm:text-sm">
              {collection.season} {collection.year}
            </Badge>
          </div>

          {/* Product Count Badge - Mobile optimized */}
          <div className="absolute top-3 sm:top-4 right-3 sm:right-4">
            <Badge variant="secondary" className="bg-gray-900/80 text-white text-xs sm:text-sm">
              {collection.products.length} Products
            </Badge>
          </div>
        </div>
      </div>

      {/* Collection Info - Mobile responsive */}
      <CardContent className="p-4 sm:p-5 lg:p-6 flex flex-col flex-1">
        <div className="flex-1 space-y-3 sm:space-y-4">
          <div className="space-y-2">
            <h2 className="text-lg sm:text-xl font-bold uppercase tracking-wide text-gray-900 group-hover:text-gray-700 transition-colors line-clamp-2">
              {collection.name}
            </h2>
            <p className="text-gray-600 text-sm line-clamp-3 sm:line-clamp-2 min-h-[3rem] sm:min-h-[2.5rem]">
              {collection.description}
            </p>
          </div>

          {/* Collection Details - Mobile responsive */}
          <div className="space-y-2 text-xs sm:text-sm text-gray-500">
            <div className="flex items-start gap-2">
              <Calendar className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0 mt-0.5" />
              <span className="line-clamp-2">
                Order: {collection.orderDates.start} - {collection.orderDates.end}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Package className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
              <span>{collection.products.length} products in collection</span>
            </div>
          </div>
        </div>

        {/* Action Buttons - Mobile First Design */}
        <div className="pt-4 mt-auto">
          {/* Mobile: Stacked buttons */}
          <div className="flex flex-col gap-2 sm:hidden">
            <Link href={`/collections/${collection.id}/showroom`} className="w-full">
              <Button variant="outline" className="w-full bg-transparent hover:bg-gray-50 h-10 justify-start">
                <Eye className="mr-2 h-4 w-4" />
                Virtual Showroom
              </Button>
            </Link>
            <Link href={`/collections/${collection.id}/technical`} className="w-full">
              <Button variant="outline" className="w-full bg-transparent hover:bg-gray-50 h-10 justify-start">
                <Ruler className="mr-2 h-4 w-4" />
                Technical Files
              </Button>
            </Link>
            <Link href={`/collections/${collection.id}/lookbook`} className="w-full">
              <Button variant="outline" className="w-full bg-transparent hover:bg-gray-50 h-10 justify-start">
                <BookOpen className="mr-2 h-4 w-4" />
                Lookbook
              </Button>
            </Link>
          </div>

          {/* Tablet & Desktop: Grid buttons */}
          <div className="hidden sm:grid grid-cols-3 gap-2">
            <Link href={`/collections/${collection.id}/showroom`}>
              <Button
                variant="outline"
                size="sm"
                className="w-full bg-transparent hover:bg-gray-50 px-2 py-2 h-9 text-xs"
              >
                <Eye className="mr-1 h-3 w-3" />
                <span className="truncate">Showroom</span>
              </Button>
            </Link>
            <Link href={`/collections/${collection.id}/technical`}>
              <Button
                variant="outline"
                size="sm"
                className="w-full bg-transparent hover:bg-gray-50 px-2 py-2 h-9 text-xs"
              >
                <Ruler className="mr-1 h-3 w-3" />
                <span className="truncate">Technical</span>
              </Button>
            </Link>
            <Link href={`/collections/${collection.id}/lookbook`}>
              <Button
                variant="outline"
                size="sm"
                className="w-full bg-transparent hover:bg-gray-50 px-2 py-2 h-9 text-xs"
              >
                <BookOpen className="mr-1 h-3 w-3" />
                <span className="truncate">Lookbook</span>
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
