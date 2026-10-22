// src/greenchoice/schemas.py ile birebir aynı tutulmalı.

export type Label = "recommended" | "neutral" | "not_recommended";

export interface Criterion {
  id: string;
  name: string;
  weight: number;
}

export interface Category {
  id: string;
  name: string;
  product_count: number;
  criteria: Criterion[];
}

export interface Explanation {
  criterion: string;
  criterion_name: string;
  direction: "positive" | "negative";
  impact: number;
  text: string;
}

export interface ProductSummary {
  id: string;
  name: string;
  brand: string | null;
  category: string;
  price_tl: number | null;
  energy_class: string | null;
  score: number;
  label: Label;
  label_text: string;
}

export interface ReviewStats {
  n_reviews: number;
  rating_avg: number | null;
  rating_count: number | null;
  aspects: Record<string, { pos: number; neg: number }>;
}

export interface ProductDetail extends ProductSummary {
  model_code: string | null;
  url: string | null;
  specs: Record<string, number | string | null>;
  annual_kwh: number | null;
  tco_tl: number | null;
  lifetime_years: number;
  sub_scores: Record<string, number>;
  imputed: string[];
  explanations: Explanation[];
  review_stats: ReviewStats;
  method: string;
}
