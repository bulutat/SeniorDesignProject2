// Which cells of a comparison row hold the best value. Pure functions, no API calls.
//
// Rules: missing values never win; values filled with the category median ("no data") never
// win, because they are not the product's own data; ties all win; a row where every real
// value is the same (or only one product has a real value) has no winner.

export type Better = "higher" | "lower";

export function bestIndexes(values: (number | null | undefined)[], better: Better): Set<number> {
  const real = values
    .map((v, i) => ({ v, i }))
    .filter((x): x is { v: number; i: number } => typeof x.v === "number" && Number.isFinite(x.v));
  if (real.length < 2) return new Set();
  const pick = better === "higher" ? Math.max : Math.min;
  const best = pick(...real.map((x) => x.v));
  if (real.every((x) => x.v === best)) return new Set();
  return new Set(real.filter((x) => x.v === best).map((x) => x.i));
}

// Energy classes on the 2021 EU scale, A best. Other values (e.g. an old "A++") are not ranked.
const SCALE = "ABCDEFG";
export const energyRank = (c: string | null | undefined): number | null => {
  const k = c?.trim().toUpperCase() ?? "";
  return k.length === 1 && SCALE.includes(k) ? SCALE.indexOf(k) : null;
};
