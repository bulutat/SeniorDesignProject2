const tl = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 });

export const formatTl = (v: number | null | undefined) => (v == null ? "—" : `${tl.format(v)} TL`);

export const formatNum = (v: number | null | undefined, digits = 0) =>
  v == null ? "—" : v.toLocaleString("tr-TR", { maximumFractionDigits: digits });
