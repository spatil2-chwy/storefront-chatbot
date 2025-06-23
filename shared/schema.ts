import { z } from "zod";

export const userSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  name: z.string(),
});

export const productSchema = z.object({
  id: z.number(),
  title: z.string(),
  brand: z.string(),
  price: z.number(),
  originalPrice: z.number().optional(),
  autoshipPrice: z.number(),
  rating: z.number().min(0).max(5),
  reviewCount: z.number(),
  image: z.string(),
  images: z.array(z.string()),
  deal: z.boolean(),
  flavors: z.array(z.string()),
  sizes: z.array(z.object({
    name: z.string(),
    price: z.number(),
    pricePerLb: z.string(),
  })),
  description: z.string(),
  inStock: z.boolean(),
  category: z.string(),
  keywords: z.array(z.string()),
});

export const chatMessageSchema = z.object({
  id: z.string(),
  content: z.string(),
  sender: z.enum(['user', 'ai']),
  timestamp: z.date(),
});

export type User = z.infer<typeof userSchema>;
export type Product = z.infer<typeof productSchema>;
export type ChatMessage = z.infer<typeof chatMessageSchema>;
