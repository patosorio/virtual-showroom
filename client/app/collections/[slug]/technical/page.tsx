"use client"

import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { TechnicalFilesViewer } from "@/components/products/technical-files-viewer"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { useCollectionBySlug } from "@/hooks/useCollections"
import { transformCollectionResponse } from "@/lib/transformers/collections"
import { notFound } from "next/navigation"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CollectionTechnicalPageProps {
  params: {
    slug: string
  }
}

export default function CollectionTechnicalPage({ params }: CollectionTechnicalPageProps) {
  const { data: collectionResponse, isLoading, error, refetch } = useCollectionBySlug(params.slug)

  if (isLoading) {
    return (
      <ShowroomLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">Loading collection...</p>
          </div>
        </div>
      </ShowroomLayout>
    )
  }

  if (error) {
    return (
      <ShowroomLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center max-w-md">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Collection not found
            </h3>
            <p className="text-gray-600 mb-4">
              The collection you're looking for doesn't exist or has been removed.
            </p>
            <Button onClick={() => refetch()} className="bg-gray-900 hover:bg-gray-800">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          </div>
        </div>
      </ShowroomLayout>
    )
  }

  if (!collectionResponse) {
    notFound()
  }

  const collection = transformCollectionResponse(collectionResponse)

  return (
    <ShowroomLayout>
      <TechnicalFilesViewer collection={collection} />
    </ShowroomLayout>
  )
}
