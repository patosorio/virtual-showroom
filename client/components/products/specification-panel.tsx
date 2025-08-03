"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { TechnicalSpec } from "@/types"
import { cn } from "@/lib/utils"

interface SpecificationPanelProps {
  specifications: TechnicalSpec[]
}

export function SpecificationPanel({ specifications }: SpecificationPanelProps) {
  const [expandedSpecs, setExpandedSpecs] = useState<Set<string>>(new Set(["material"]))

  const toggleSpec = (type: string) => {
    const newExpanded = new Set(expandedSpecs)
    if (newExpanded.has(type)) {
      newExpanded.delete(type)
    } else {
      newExpanded.add(type)
    }
    setExpandedSpecs(newExpanded)
  }

  const getSpecTitle = (type: string) => {
    switch (type) {
      case "material":
        return "Materials & Construction"
      case "sizing":
        return "Size Chart"
      case "care":
        return "Care Instructions"
      case "construction":
        return "Technical Details"
      default:
        return type.charAt(0).toUpperCase() + type.slice(1)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-900 uppercase tracking-wide">Technical Specifications</h3>

      <div className="border border-gray-200 rounded-lg divide-y divide-gray-200">
        {specifications.map((spec) => (
          <div key={spec.type} className="p-4">
            <Button
              variant="ghost"
              className="w-full justify-between p-0 h-auto font-medium text-left"
              onClick={() => toggleSpec(spec.type)}
            >
              <span className="uppercase text-sm tracking-wide">{getSpecTitle(spec.type)}</span>
              {expandedSpecs.has(spec.type) ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>

            <div
              className={cn(
                "mt-4 space-y-2 transition-all duration-200",
                expandedSpecs.has(spec.type) ? "block" : "hidden",
              )}
            >
              {spec.type === "material" && (
                <div className="text-sm text-gray-600 space-y-2">
                  <p>Made with ECONYL® regenerated Nylon</p>
                  <p>78% Recycled PA, 22% EA</p>
                  <div className="space-y-1">
                    <p className="font-medium">Features:</p>
                    <ul className="list-disc list-inside space-y-1 ml-4">
                      <li>UPF 50+ sun protection</li>
                      <li>Sun cream tested</li>
                      <li>Chlorine proof</li>
                    </ul>
                  </div>
                </div>
              )}

              {spec.type === "sizing" && (
                <div className="text-sm text-gray-600">
                  <div className="grid grid-cols-4 gap-2 font-mono">
                    <div className="font-medium">Size</div>
                    <div className="font-medium">UK</div>
                    <div className="font-medium">EU</div>
                    <div className="font-medium">US</div>
                    <div>XS</div>
                    <div>6</div>
                    <div>34</div>
                    <div>2</div>
                    <div>S</div>
                    <div>8</div>
                    <div>36</div>
                    <div>4</div>
                    <div>M</div>
                    <div>10</div>
                    <div>38</div>
                    <div>6</div>
                    <div>L</div>
                    <div>12</div>
                    <div>40</div>
                    <div>8</div>
                    <div>XL</div>
                    <div>14</div>
                    <div>42</div>
                    <div>10</div>
                  </div>
                </div>
              )}

              {spec.type === "construction" && (
                <div className="text-sm text-gray-600 space-y-2">
                  <p>
                    <strong>TOP:</strong> Top with double fabric. Front straps adjustable in 5 positions with
                    embroidered eyelets. Customs rubber-coated bronze buckles.
                  </p>
                  <p>
                    <strong>BOTTOM:</strong> Double fabric offers extra support. Low-cut leg. Low-rise waist. Two belts
                    with 3 position embroidered eyelets.
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
