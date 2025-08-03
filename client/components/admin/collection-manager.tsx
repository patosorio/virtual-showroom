"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Edit, Trash2, Eye, Calendar, Package } from "lucide-react"
import { mockCollections } from "@/lib/mock-data"
import Link from "next/link"

export function CollectionManager() {
  const [collections, setCollections] = useState(mockCollections)

  const handleDeleteCollection = (collectionId: string) => {
    setCollections(collections.filter((c) => c.id !== collectionId))
  }

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex flex-col h-full">
        {/* Fixed Header */}
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {collections.map((collection) => (
              <Card key={collection.id} className="hover:shadow-lg transition-shadow">
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
                <CardContent className="space-y-4">
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

                  <div className="flex gap-2 pt-2">
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
        </div>
      </div>
    </div>
  )
}
