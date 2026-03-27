import { z } from 'zod';

// 프론트엔드 -> 백엔드 요청 파라미터 검증 스키마
export const placesRequestSchema = z.object({
  lat: z.number().min(-90).max(90),
  lng: z.number().min(-180).max(180),
  radius: z.number().min(10).max(5000).default(300),
});

// 백엔드 -> 프론트엔드 응답(단일 시설) 검증 스키마
export const placeFeatureSchema = z.object({
  type: z.literal("Feature"),
  geometry: z.object({
    type: z.literal("Point"),
    coordinates: z.tuple([z.number(), z.number()]),
  }),
  properties: z.object({
    id: z.string().uuid(),
    name: z.string(),
    category: z.string().nullable().optional(),
    address: z.string().nullable().optional(),
    image_url: z.string().nullable().optional(),
    meta: z.record(z.any()).optional().nullable(),
  }),
});

// 백엔드 -> 프론트엔드 전체 응답(FeatureCollection) 검증 스키마
export const placesResponseSchema = z.object({
  type: z.literal("FeatureCollection"),
  features: z.array(placeFeatureSchema),
});
