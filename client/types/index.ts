export interface Collection {
  id: string
  name: string
  season: string
  year: number
  orderDates: {
    start: string
    end: string
  }
  description: string
  products: Product[]
}

export interface Product {
  id: string
  name: string
  category: "bikini" | "one-piece" | "accessory"
  variants: ProductVariant[]
  specifications: TechnicalSpec[]
  images: ProductImage[]
  pricing: PricingInfo
}

export interface ProductVariant {
  id: string
  color: string
  colorCode: string
  sizes: SizeInfo[]
  images: string[]
}

export interface ProductImage {
  id: string
  url: string
  alt: string
  type: "main" | "detail" | "lifestyle"
}

export interface TechnicalSpec {
  type: "material" | "construction" | "care" | "sizing"
  details: Record<string, any>
}

export interface PricingInfo {
  wholesale: number
  retail: number
  currency: string
}

export interface SizeInfo {
  size: string
  measurements: Record<string, number>
  availability: boolean
}
