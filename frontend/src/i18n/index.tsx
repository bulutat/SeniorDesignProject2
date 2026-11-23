// Interface language: a small typed dictionary per language and a React context.
// The same code is sent to the API (?lang=) for names, labels and explanation texts.
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { Language } from "../types";
import { tr, type Messages } from "./tr";
import { en } from "./en";
import { de } from "./de";

export type Lang = Language;

// Language names are written in their own language, as is usual for language menus.
export const LANGUAGES: { id: Lang; name: string }[] = [
  { id: "tr", name: "Türkçe" },
  { id: "en", name: "English" },
  { id: "de", name: "Deutsch" },
];

const MESSAGES: Record<Lang, Messages> = { tr, en, de };
const STORAGE_KEY = "greenchoice.lang";
const isLang = (v: unknown): v is Lang => v === "tr" || v === "en" || v === "de";

// Browser storage can be unavailable (private mode, blocked cookies); Turkish is the fallback.
function storedLang(): Lang {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return isLang(v) ? v : "tr";
  } catch {
    return "tr";
  }
}

interface I18n {
  lang: Lang;
  t: Messages;
  setLang: (lang: Lang) => void;
  formatTl: (v: number | null | undefined) => string;
  formatNum: (v: number | null | undefined, digits?: number) => string;
}

const I18nContext = createContext<I18n | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(storedLang);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo<I18n>(() => {
    const t = MESSAGES[lang];
    const whole = new Intl.NumberFormat(t.locale, { maximumFractionDigits: 0 });
    return {
      lang,
      t,
      setLang: (next) => {
        setLangState(next);
        try {
          localStorage.setItem(STORAGE_KEY, next);
        } catch {
          // the choice then lasts only for this visit
        }
      },
      // Prices stay in Turkish lira; only the number format follows the language.
      formatTl: (v) => (v == null ? "—" : `${whole.format(v)} TL`),
      formatNum: (v, digits = 0) =>
        v == null ? "—" : v.toLocaleString(t.locale, { maximumFractionDigits: digits }),
    };
  }, [lang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18n {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used inside I18nProvider");
  return ctx;
}
