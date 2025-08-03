"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import {
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  Plus,
  Settings,
  User,
  Shield,
  Layers,
  Eye,
  Ruler,
  BookOpen,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { mockCollections } from "@/lib/mock-data"

interface NavigationSidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function NavigationSidebar({ isOpen, onToggle }: NavigationSidebarProps) {
  const [expandedCollections, setExpandedCollections] = useState<Set<string>>(new Set(["coral-reef"]))
  const [activeSection, setActiveSection] = useState("coral-reef-showroom")

  const toggleCollection = (collectionId: string) => {
    const newExpanded = new Set(expandedCollections)
    if (newExpanded.has(collectionId)) {
      newExpanded.delete(collectionId)
    } else {
      newExpanded.add(collectionId)
    }
    setExpandedCollections(newExpanded)
  }

  const profileItems = [
    {
      id: "add-collection",
      label: "ADD COLLECTION",
      href: "/admin/collections/new",
      icon: "Plus",
    },
    {
      id: "manage-collections",
      label: "MANAGE COLLECTIONS",
      href: "/admin/collections",
      icon: "Settings",
    },
    {
      id: "user-settings",
      label: "USER SETTINGS",
      href: "/settings",
      icon: "User",
    },
    {
      id: "admin-panel",
      label: "ADMIN PANEL",
      href: "/admin",
      icon: "Shield",
    },
  ]

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={onToggle} />}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-full w-64 bg-gray-900 text-white z-50 transform transition-transform duration-300 ease-in-out",
          "lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-700">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden mb-4 text-white hover:bg-gray-800"
              onClick={onToggle}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <Link href="/" className="flex items-center hover:opacity-80 transition-opacity">
              <Image
                src="/images/medina-logo-white.png"
                alt="MEDINA - Go to Homepage"
                width={120}
                height={40}
                className="h-8 w-auto"
                priority
              />
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-6 space-y-8 overflow-y-auto">
            {/* Collections Section */}
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Collections</h3>
              <div className="space-y-2">
                {mockCollections.map((collection) => (
                  <div key={collection.id}>
                    {/* Collection Header */}
                    <button
                      className="flex items-center justify-between w-full px-3 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
                      onClick={() => toggleCollection(collection.id)}
                    >
                      <div className="flex items-center">
                        <Layers className="mr-3 h-4 w-4" />
                        <span className="uppercase tracking-wide text-xs">{collection.name}</span>
                      </div>
                      {expandedCollections.has(collection.id) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </button>

                    {/* Collection Sub-menu */}
                    {expandedCollections.has(collection.id) && (
                      <div className="ml-6 mt-2 space-y-1">
                        <Link
                          href={`/collections/${collection.id}/showroom`}
                          className={cn(
                            "flex items-center px-3 py-2 text-sm rounded-md transition-colors",
                            activeSection === `${collection.id}-showroom`
                              ? "bg-gray-800 text-white"
                              : "text-gray-400 hover:bg-gray-800 hover:text-white",
                          )}
                          onClick={() => setActiveSection(`${collection.id}-showroom`)}
                        >
                          <Eye className="mr-3 h-3 w-3" />
                          Virtual Showroom
                        </Link>
                        <Link
                          href={`/collections/${collection.id}/technical`}
                          className={cn(
                            "flex items-center px-3 py-2 text-sm rounded-md transition-colors",
                            activeSection === `${collection.id}-technical`
                              ? "bg-gray-800 text-white"
                              : "text-gray-400 hover:bg-gray-800 hover:text-white",
                          )}
                          onClick={() => setActiveSection(`${collection.id}-technical`)}
                        >
                          <Ruler className="mr-3 h-3 w-3" />
                          Technical Files
                        </Link>
                        <Link
                          href={`/collections/${collection.id}/lookbook`}
                          className={cn(
                            "flex items-center px-3 py-2 text-sm rounded-md transition-colors",
                            activeSection === `${collection.id}-lookbook`
                              ? "bg-gray-800 text-white"
                              : "text-gray-400 hover:bg-gray-800 hover:text-white",
                          )}
                          onClick={() => setActiveSection(`${collection.id}-lookbook`)}
                        >
                          <BookOpen className="mr-3 h-3 w-3" />
                          Lookbook
                        </Link>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Profile Section */}
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Profile & Admin</h3>
              <ul className="space-y-2">
                {profileItems.map((item) => {
                  const IconComponent =
                    item.icon === "Plus"
                      ? Plus
                      : item.icon === "Settings"
                        ? Settings
                        : item.icon === "User"
                          ? User
                          : Shield
                  return (
                    <li key={item.id}>
                      <Link
                        href={item.href}
                        className="flex items-center px-3 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
                      >
                        <IconComponent className="mr-3 h-4 w-4" />
                        {item.label}
                      </Link>
                    </li>
                  )
                })}
              </ul>
            </div>
          </nav>
        </div>
      </aside>
    </>
  )
}
