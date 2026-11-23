import type { Category, ProductDetail, ProductSummary } from "./types";
import type { Lang } from "./i18n";

// Carries the HTTP status so the UI can show the error in the chosen language.
export class ApiError extends Error {
  constructor(public status: number, public detail: string | null) {
    super(detail ?? `HTTP ${status}`);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, typeof body.detail === "string" ? body.detail : null);
  }
  return res.json() as Promise<T>;
}

const q = encodeURIComponent;

// lang changes names, labels and explanation texts only; scores and data are the same.
export const api = {
  categories: (lang: Lang) => request<Category[]>(`/api/categories?lang=${lang}`),
  products: (category: string, lang: Lang) =>
    request<ProductSummary[]>(`/api/products?category=${q(category)}&lang=${lang}`),
  product: (id: string, lang: Lang) =>
    request<ProductDetail>(`/api/products/${q(id)}?lang=${lang}`),
  compare: (ids: string[], lang: Lang) =>
    request<ProductDetail[]>(`/api/compare?ids=${ids.map(q).join(",")}&lang=${lang}`),
  customScore: (category: string, weights: Record<string, number>, lang: Lang) =>
    request<ProductSummary[]>(`/api/score?lang=${lang}`, {
      method: "POST",
      body: JSON.stringify({ category, weights }),
    }),
};
