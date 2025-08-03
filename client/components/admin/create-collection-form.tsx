"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, Save } from "lucide-react"
import Link from "next/link"

export function CreateCollectionForm() {
  const [formData, setFormData] = useState({
    name: "",
    season: "",
    year: new Date().getFullYear(),
    description: "",
    orderStartDate: "",
    orderEndDate: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
    console.log("Creating collection:", formData)
  }

  const handleInputChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex flex-col h-full">
        {/* Fixed Header */}
        <div className="flex-shrink-0 py-6 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <Link href="/admin/collections">
              <Button variant="outline" size="icon">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold uppercase tracking-wide text-gray-900">Create New Collection</h1>
              <p className="text-gray-600 mt-2">Add a new fashion collection to your showroom</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 py-6 overflow-y-auto">
          <Card>
            <CardHeader>
              <CardTitle className="uppercase tracking-wide">Collection Details</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-sm font-medium uppercase tracking-wide">
                      Collection Name
                    </Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => handleInputChange("name", e.target.value)}
                      placeholder="e.g., Ocean Breeze Collection"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="season" className="text-sm font-medium uppercase tracking-wide">
                      Season
                    </Label>
                    <Select value={formData.season} onValueChange={(value) => handleInputChange("season", value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select season" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="spring">Spring</SelectItem>
                        <SelectItem value="summer">Summer</SelectItem>
                        <SelectItem value="high-summer">High Summer</SelectItem>
                        <SelectItem value="fall">Fall</SelectItem>
                        <SelectItem value="winter">Winter</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="year" className="text-sm font-medium uppercase tracking-wide">
                      Year
                    </Label>
                    <Input
                      id="year"
                      type="number"
                      value={formData.year}
                      onChange={(e) => handleInputChange("year", Number.parseInt(e.target.value))}
                      min="2020"
                      max="2030"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium uppercase tracking-wide">Order Period</Label>
                    <div className="grid grid-cols-2 gap-2">
                      <Input
                        type="date"
                        value={formData.orderStartDate}
                        onChange={(e) => handleInputChange("orderStartDate", e.target.value)}
                        required
                      />
                      <Input
                        type="date"
                        value={formData.orderEndDate}
                        onChange={(e) => handleInputChange("orderEndDate", e.target.value)}
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description" className="text-sm font-medium uppercase tracking-wide">
                    Description
                  </Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange("description", e.target.value)}
                    placeholder="Describe the inspiration and theme of this collection..."
                    rows={4}
                    required
                  />
                </div>

                <div className="flex gap-4 pt-6">
                  <Button type="submit" className="bg-gray-900 hover:bg-gray-800">
                    <Save className="mr-2 h-4 w-4" />
                    Create Collection
                  </Button>
                  <Link href="/admin/collections">
                    <Button variant="outline">Cancel</Button>
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
