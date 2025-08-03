import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { CollectionDetail } from "@/components/collections/collection-detail"
import { mockCollections } from "@/lib/mock-data"
import { notFound } from "next/navigation"

interface CollectionPageProps {
  params: {
    slug: string
  }
}

export default function CollectionPage({ params }: CollectionPageProps) {
  const collection = mockCollections.find((c) => c.id === params.slug)

  if (!collection) {
    notFound()
  }

  return (
    <ShowroomLayout>
      <CollectionDetail collection={collection} />
    </ShowroomLayout>
  )
}
