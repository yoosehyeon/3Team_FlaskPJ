import { z } from "zod";

export const CoordinateSchema = z.object({
  lat: z.number().min(-90).max(90),
  lng: z.number().min(-180).max(180)
});

export const PlaceResponseSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  category: z.string().nullable(),
  address: z.string().nullable(),
  location: z.any(), // GeoJSON point
  image_url: z.string().nullable(),
  meta: z.any().nullable(),
  created_at: z.string().nullable()
});

export const ReportSubmitSchema = z.object({
  lat: z.number(),
  lng: z.number(),
  type: z.enum(['obstacle', 'elevator_broken', 'ramp_damaged']),
  description: z.string().optional()
});
