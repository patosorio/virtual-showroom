import type { Collection } from "@/types/collections"
import type { Product } from "@/types"

export const mockProducts: Product[] = [
  {
    id: "jackie-bikini",
    name: "Jackie Bikini",
    category: "bikini",
    variants: [
      {
        id: "jackie-turquoise",
        color: "turquoise",
        colorCode: "#4fd1c7",
        sizes: [
          { size: "XS", measurements: { bust: 32, waist: 24 }, availability: true },
          { size: "S", measurements: { bust: 34, waist: 26 }, availability: true },
          { size: "M", measurements: { bust: 36, waist: 28 }, availability: true },
          { size: "L", measurements: { bust: 38, waist: 30 }, availability: true },
        ],
        images: ["/placeholder.svg?height=600&width=480"],
      },
      {
        id: "jackie-orange",
        color: "orange",
        colorCode: "#ff6b35",
        sizes: [
          { size: "XS", measurements: { bust: 32, waist: 24 }, availability: true },
          { size: "S", measurements: { bust: 34, waist: 26 }, availability: true },
          { size: "M", measurements: { bust: 36, waist: 28 }, availability: true },
          { size: "L", measurements: { bust: 38, waist: 30 }, availability: true },
        ],
        images: ["/placeholder.svg?height=600&width=480"],
      },
    ],
    specifications: [
      {
        type: "material",
        details: {
          fabric: "ECONYL® regenerated Nylon",
          composition: "78% Recycled PA, 22% EA",
          features: ["UPF 50+", "Sun cream tested", "Chlorine proof"],
        },
      },
      {
        type: "construction",
        details: {
          top: "Triangle-style top with signature rubber-coated bronze buckles",
          bottom: "Retro-style bottoms with fuller coverage and waist-cinching belt",
        },
      },
      {
        type: "sizing",
        details: {
          fit: "True to size",
          model: "Model is 5'8\" wearing size S",
        },
      },
    ],
    images: [
      {
        id: "1",
        url: "/placeholder.svg?height=600&width=480",
        alt: "Jackie Bikini - Turquoise",
        type: "main",
      },
      {
        id: "2",
        url: "/placeholder.svg?height=400&width=300",
        alt: "Jackie Bikini Top Detail",
        type: "detail",
      },
      {
        id: "3",
        url: "/placeholder.svg?height=400&width=300",
        alt: "Jackie Bikini Bottom Detail",
        type: "detail",
      },
    ],
    pricing: {
      wholesale: 45,
      retail: 120,
      currency: "USD",
    },
  },
  {
    id: "marine-hunter",
    name: "Marine Hunter",
    category: "bikini",
    variants: [
      {
        id: "marine-navy",
        color: "navy",
        colorCode: "#1a365d",
        sizes: [
          { size: "XS", measurements: { bust: 32, waist: 24 }, availability: true },
          { size: "S", measurements: { bust: 34, waist: 26 }, availability: true },
          { size: "M", measurements: { bust: 36, waist: 28 }, availability: true },
          { size: "L", measurements: { bust: 38, waist: 30 }, availability: true },
        ],
        images: ["/placeholder.svg?height=600&width=480"],
      },
      {
        id: "marine-blueberry",
        color: "blueberry",
        colorCode: "#4c1d95",
        sizes: [
          { size: "XS", measurements: { bust: 32, waist: 24 }, availability: true },
          { size: "S", measurements: { bust: 34, waist: 26 }, availability: true },
          { size: "M", measurements: { bust: 36, waist: 28 }, availability: true },
          { size: "L", measurements: { bust: 38, waist: 30 }, availability: true },
        ],
        images: ["/placeholder.svg?height=600&width=480"],
      },
    ],
    specifications: [
      {
        type: "material",
        details: {
          fabric: "ECONYL® regenerated Nylon",
          composition: "78% Recycled PA, 22% EA",
          features: ["UPF 50+", "Sun cream tested", "Chlorine proof"],
        },
      },
      {
        type: "construction",
        details: {
          top: "Robust triangle bikini with tactile navy seersucker-style ECONYL",
          bottom: "Fuller coverage with ability to hold and sculpt",
        },
      },
      {
        type: "sizing",
        details: {
          fit: "True to size",
          model: "Model is 5'8\" wearing size S",
        },
      },
    ],
    images: [
      {
        id: "1",
        url: "/placeholder.svg?height=600&width=480",
        alt: "Marine Hunter - Navy",
        type: "main",
      },
      {
        id: "2",
        url: "/placeholder.svg?height=400&width=300",
        alt: "Marine Hunter Technical View",
        type: "detail",
      },
    ],
    pricing: {
      wholesale: 48,
      retail: 125,
      currency: "USD",
    },
  },
  {
    id: "coral-one-piece",
    name: "Coral One-Piece",
    category: "one-piece",
    variants: [
      {
        id: "coral-coral",
        color: "coral",
        colorCode: "#ff6b35",
        sizes: [
          { size: "XS", measurements: { bust: 32, waist: 24 }, availability: true },
          { size: "S", measurements: { bust: 34, waist: 26 }, availability: true },
          { size: "M", measurements: { bust: 36, waist: 28 }, availability: true },
          { size: "L", measurements: { bust: 38, waist: 30 }, availability: true },
        ],
        images: ["/placeholder.svg?height=600&width=480"],
      },
      {
        id: "coral-aqua",
        color: "aqua",
        colorCode: "#4fd1c7",
        sizes: [
          { size: "XS", measurements: { bust: 32, waist: 24 }, availability: true },
          { size: "S", measurements: { bust: 34, waist: 26 }, availability: true },
          { size: "M", measurements: { bust: 36, waist: 28 }, availability: true },
          { size: "L", measurements: { bust: 38, waist: 30 }, availability: true },
        ],
        images: ["/placeholder.svg?height=600&width=480"],
      },
    ],
    specifications: [
      {
        type: "material",
        details: {
          fabric: "ECONYL® regenerated Nylon",
          composition: "78% Recycled PA, 22% EA",
          features: ["UPF 50+", "Sun cream tested", "Chlorine proof"],
        },
      },
      {
        type: "construction",
        details: {
          design: "Classic one-piece with modern cut-out details",
          support: "Built-in shelf bra with removable padding",
        },
      },
      {
        type: "sizing",
        details: {
          fit: "True to size",
          model: "Model is 5'8\" wearing size S",
        },
      },
    ],
    images: [
      {
        id: "1",
        url: "/placeholder.svg?height=600&width=480",
        alt: "Coral One-Piece - Coral",
        type: "main",
      },
    ],
    pricing: {
      wholesale: 52,
      retail: 135,
      currency: "USD",
    },
  },
]

export const mockCollections: Collection[] = [
  {
    id: "coral-reef",
    name: "Coral Reef Collection",
    season: "High Summer",
    year: 2021,
    orderDates: {
      start: "15th October",
      end: "31st October 2021",
    },
    description: "Restoring and protecting the Mexican reef.",
    products: mockProducts,
  },
]
