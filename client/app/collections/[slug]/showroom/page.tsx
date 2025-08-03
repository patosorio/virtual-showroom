import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { VirtualShowroom } from "@/components/showroom/virtual-showroom"
import { mockCollections } from "@/lib/mock-data"
import { notFound } from "next/navigation"

interface CollectionShowroomPageProps {
  params: {
    slug: string
  }
}

export default function CollectionShowroomPage({ params }: CollectionShowroomPageProps) {
  const collection = mockCollections.find((c) => c.id === params.slug)

  if (!collection) {
    notFound()
  }

  return (
    <ShowroomLayout>
      <VirtualShowroom collection={collection} />
    </ShowroomLayout>
  )
}
