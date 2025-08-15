"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, Save } from "lucide-react"
import Link from "next/link"
import { useCreateCollection } from "@/hooks/useCollections"
import type { CollectionCreate } from "@/types/collections"
import { toast } from "sonner"

export function CreateCollectionForm() {
  const [formData, setFormData] = useState({
    name: "",
    season: "",
    year: new Date().getFullYear(),
    description: "",
    orderStartDate: "",
    orderEndDate: "",
    slug: ""
  })

  const router = useRouter()
  const { mutate: createCollection, isPending } = useCreateCollection({
    onSuccess: () => {
      router.push("/admin/collections")
    }
  })

  // Generate slug from name
  const generateSlug = (name: string) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }

  // Update slug when name changes
  const handleNameChange = (name: string) => {
    setFormData(prev => ({
      ...prev,
      name,
      slug: generateSlug(name)
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    console.log('🚀 SUBMIT - Form data before validation:', formData);
    console.log('🚀 SUBMIT - Season value specifically:', formData.season);
    console.log('🚀 SUBMIT - Season type:', typeof formData.season);

    // Validate required fields
    if (!formData.name || !formData.season || !formData.year || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Validate season
    const validSeasons = ['Spring', 'Summer', 'Fall', 'Winter'];
    if (!validSeasons.includes(formData.season)) {
      toast.error('Please select a valid season');
      return;
    }
    
    const collectionData: CollectionCreate = {
      name: formData.name.trim(),
      slug: (formData.slug || generateSlug(formData.name)).trim(),
      season: formData.season, // Already validated above
      year: formData.year,
      description: formData.description.trim(),
      order_start_date: formData.orderStartDate,
      order_end_date: formData.orderEndDate,
      is_published: true  // Create as published so it shows up immediately
    }

    createCollection(collectionData)
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
                      onChange={(e) => handleNameChange(e.target.value)}
                      placeholder="e.g., Ocean Breeze Collection"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="season" className="text-sm font-medium uppercase tracking-wide">
                      Season
                    </Label>
                    <Select 
                      value={formData.season}
                      onValueChange={(value) => {
                        console.log('Season changed to:', value);
                        setFormData(prev => ({ ...prev, season: value }));
                      }}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select season" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Spring">Spring</SelectItem>
                        <SelectItem value="Summer">Summer</SelectItem>
                        <SelectItem value="Fall">Fall</SelectItem>
                        <SelectItem value="Winter">Winter</SelectItem>
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
                  <Button 
                    type="submit" 
                    className="bg-gray-900 hover:bg-gray-800"
                    disabled={isPending}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    {isPending ? "Creating..." : "Create Collection"}
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
