import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { TechnicalFilesViewer } from "@/components/products/technical-files-viewer"
import { mockCollections } from "@/lib/mock-data"
import { notFound } from "next/navigation"

interface CollectionTechnicalPageProps {
  params: {
    slug: string
  }
}

export default function CollectionTechnicalPage({ params }: CollectionTechnicalPageProps) {
  const collection = mockCollections.find((c) => c.id === params.slug)

  if (!collection) {
    notFound()
  }

  return (
    <ShowroomLayout>
      <TechnicalFilesViewer collection={collection} />
    </ShowroomLayout>
  )
}
