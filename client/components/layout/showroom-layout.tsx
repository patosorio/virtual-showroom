"use client"

import type React from "react"
import { useState } from "react"
import { NavigationSidebar } from "./navigation-sidebar"
import { cn } from "@/lib/utils"

interface ShowroomLayoutProps {
  children: React.ReactNode
}

export function ShowroomLayout({ children }: ShowroomLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-white">
      <NavigationSidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <main className={cn("flex-1 transition-all duration-300 ease-in-out", "lg:ml-64")}>{children}</main>
    </div>
  )
}
