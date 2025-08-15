"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Edit, Trash2, Eye, Calendar, Package, AlertCircle, Loader2 } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useCollections, useDeleteCollection } from "@/hooks/useCollections"
import { transformCollectionsList } from "@/lib/transformers/collections"
import Link from "next/link"

export function CollectionManager() {
  const { data: collectionsResponse, isLoading, error, refetch } = useCollections({
    limit: 100,
    is_published: undefined
  })

  const { mutate: deleteCollection } = useDeleteCollection({
    onSuccess: () => {
      refetch()
    }
  })

  const handleDeleteCollection = (collectionId: string) => {
    if (confirm('Are you sure you want to delete this collection?')) {
      deleteCollection(collectionId)
    }
  }

  const collections = collectionsResponse ? transformCollectionsList(collectionsResponse.items) : []

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex flex-col h-full">

        <div className="flex-shrink-0 py-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold uppercase tracking-wide text-gray-900">Collection Manager</h1>
              <p className="text-gray-600 mt-2">Manage your fashion collections and products</p>
            </div>
            <Link href="/admin/collections/new">
              <Button className="bg-gray-900 hover:bg-gray-800">
                <Plus className="mr-2 h-4 w-4" />
                Add Collection
              </Button>
            </Link>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 py-6 overflow-y-auto">
          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">Loading collections...</p>
              </div>
            </div>
          ) : error ? (
            /* Error State */
            <Alert variant="destructive" className="max-w-md mx-auto">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load collections. Please try refreshing the page.
              </AlertDescription>
            </Alert>
          ) : collections.length === 0 ? (
            /* Empty State */
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-lg px-6">
                <div className="w-24 h-24 mx-auto bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mb-6">
                  <Package className="h-12 w-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">No collections yet</h3>
                <p className="text-gray-600 mb-6">Create your first collection to get started with your virtual showroom.</p>
                <Link href="/admin/collections/new">
                  <Button className="bg-gray-900 hover:bg-gray-800">
                    <Plus className="mr-2 h-4 w-4" />
                    Create First Collection
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            /* Collections Grid */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {collections.map((collection) => (
                <Card key={collection.id} className="hover:shadow-lg transition-shadow flex flex-col h-full">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg uppercase tracking-wide">{collection.name}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {collection.season} {collection.year}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">
                            {collection.products.length} Products
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="flex flex-col flex-1">
                    <div className="flex-1 space-y-4">
                      <p className="text-sm text-gray-600">{collection.description}</p>

                      <div className="space-y-2 text-xs text-gray-500">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3" />
                          <span>
                            Order: {collection.orderDates.start} - {collection.orderDates.end}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Package className="h-3 w-3" />
                          <span>{collection.products.length} products in collection</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2 pt-4 mt-auto">
                      <Link href={`/collections/${collection.id}/showroom`} className="flex-1">
                        <Button variant="outline" size="sm" className="w-full bg-transparent">
                          <Eye className="mr-2 h-3 w-3" />
                          View
                        </Button>
                      </Link>
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        <Edit className="mr-2 h-3 w-3" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 bg-transparent"
                        onClick={() => handleDeleteCollection(collection.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
