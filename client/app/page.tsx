import { ShowroomLayout } from "@/components/layout/showroom-layout"
import { CollectionsGrid } from "@/components/collections/collections-grid"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { useRequireAuth } from "@/hooks/useRequireAuth"

export default function HomePage() {
  return (
    <AuthGuard>
      <ShowroomLayout>
        <CollectionsGrid />
      </ShowroomLayout>
    </AuthGuard>
  )
}
