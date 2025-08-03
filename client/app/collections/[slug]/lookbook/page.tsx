import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { LookbookGallery } from "@/components/lookbook/lookbook-gallery"
import { mockCollections } from "@/lib/mock-data"
import { notFound } from "next/navigation"

interface CollectionLookbookPageProps {
  params: {
    slug: string
  }
}

export default function CollectionLookbookPage({ params }: CollectionLookbookPageProps) {
  const collection = mockCollections.find((c) => c.id === params.slug)

  if (!collection) {
    notFound()
  }

  return (
    <ShowroomLayout>
      <LookbookGallery collection={collection} />
    </ShowroomLayout>
  )
}
