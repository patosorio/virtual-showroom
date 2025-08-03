import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { CollectionManager } from "@/components/admin/collection-manager"

export default function AdminCollectionsPage() {
  return (
    <ShowroomLayout>
      <CollectionManager />
    </ShowroomLayout>
  )
}
