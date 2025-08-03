"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Package, Users, TrendingUp, Calendar, Plus, Settings } from "lucide-react"
import { mockCollections } from "@/lib/mock-data"
import Link from "next/link"

export function AdminDashboard() {
  const totalProducts = mockCollections.reduce((acc, collection) => acc + collection.products.length, 0)
  const totalCollections = mockCollections.length

  const stats = [
    {
      title: "Total Collections",
      value: totalCollections,
      icon: Package,
      color: "text-blue-600",
    },
    {
      title: "Total Products",
      value: totalProducts,
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      title: "Active Users",
      value: "24",
      icon: Users,
      color: "text-purple-600",
    },
    {
      title: "This Month",
      value: "3 New",
      icon: Calendar,
      color: "text-orange-600",
    },
  ]

  const quickActions = [
    {
      title: "Add Collection",
      description: "Create a new fashion collection",
      href: "/admin/collections/new",
      icon: Plus,
      color: "bg-blue-600",
    },
    {
      title: "Manage Collections",
      description: "Edit existing collections",
      href: "/admin/collections",
      icon: Package,
      color: "bg-green-600",
    },
    {
      title: "System Settings",
      description: "Configure application settings",
      href: "/settings",
      icon: Settings,
      color: "bg-purple-600",
    },
  ]

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex flex-col h-full">
        {/* Fixed Header */}
        <div className="flex-shrink-0 py-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold uppercase tracking-wide text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage your virtual showroom and collections</p>
        </div>

        {/* Main Content */}
        <div className="flex-1 py-6 overflow-y-auto">
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat) => (
                <Card key={stat.title}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">{stat.title}</p>
                        <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                      </div>
                      <stat.icon className={`h-8 w-8 ${stat.color}`} />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Quick Actions */}
            <div>
              <h2 className="text-xl font-semibold uppercase tracking-wide text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {quickActions.map((action) => (
                  <Card key={action.title} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg ${action.color}`}>
                          <action.icon className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 uppercase tracking-wide text-sm">
                            {action.title}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                          <Link href={action.href}>
                            <Button variant="outline" size="sm" className="mt-3 bg-transparent">
                              Get Started
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Recent Collections */}
            <div>
              <h2 className="text-xl font-semibold uppercase tracking-wide text-gray-900 mb-4">Recent Collections</h2>
              <div className="space-y-4">
                {mockCollections.slice(0, 3).map((collection) => (
                  <Card key={collection.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div>
                            <h3 className="font-medium uppercase tracking-wide">{collection.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="outline" className="text-xs">
                                {collection.season} {collection.year}
                              </Badge>
                              <span className="text-sm text-gray-500">{collection.products.length} products</span>
                            </div>
                          </div>
                        </div>
                        <Link href={`/collections/${collection.id}/showroom`}>
                          <Button variant="outline" size="sm">
                            View Collection
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
