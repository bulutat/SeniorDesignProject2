import type { Category, ProductDetail, ProductSummary } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `İstek başarısız: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  categories: () => request<Category[]>("/api/categories"),
  products: (category: string) =>
    request<ProductSummary[]>(`/api/products?category=${encodeURIComponent(category)}`),
  product: (id: string) => request<ProductDetail>(`/api/products/${encodeURIComponent(id)}`),
  compare: (ids: string[]) =>
    request<ProductDetail[]>(`/api/compare?ids=${ids.map(encodeURIComponent).join(",")}`),
  customScore: (category: string, weights: Record<string, number>) =>
    request<ProductSummary[]>("/api/score", {
      method: "POST",
      body: JSON.stringify({ category, weights }),
    }),
};
