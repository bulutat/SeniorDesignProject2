import { LANGUAGES, useI18n, type Lang } from "../i18n";

// Language menu in the header: a globe icon and the language names in their own language.
// A native <select> keeps it keyboard and screen-reader friendly without extra code.
export default function LanguageSelect() {
  const { lang, setLang, t } = useI18n();
  return (
    <label className="lang-select">
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
        <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.6" />
        <path
          d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
        />
      </svg>
      <span className="visually-hidden">{t.app.language}</span>
      <select value={lang} onChange={(e) => setLang(e.target.value as Lang)}>
        {LANGUAGES.map((l) => (
          <option key={l.id} value={l.id} lang={l.id}>{l.name}</option>
        ))}
      </select>
    </label>
  );
}
