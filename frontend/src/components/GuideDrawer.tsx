import { useEffect, useRef } from "react";
import { useI18n } from "../i18n";
import type { Category } from "../types";
import { GUIDE_TABS, type GuideTab } from "./guide/sections";

interface Props {
  open: boolean;
  tab: GuideTab;
  category: Category | undefined;
  onTab: (tab: GuideTab) => void;
  onClose: () => void;
}

// Side panel with the user guide. Closes with Esc, the close button or a click on the backdrop;
// focus moves into the panel on open and back to the element that opened it on close.
export default function GuideDrawer({ open, tab, category, onTab, onClose }: Props) {
  const { t } = useI18n();
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const opener = document.activeElement as HTMLElement | null;
    panel.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    document.body.classList.add("no-scroll");
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.classList.remove("no-scroll");
      opener?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;
  const Current = GUIDE_TABS.find((g) => g.id === tab)!.Body;

  return (
    <div className="guide-backdrop" onClick={onClose}>
      <div
        className="guide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="guide-title"
        tabIndex={-1}
        ref={panel}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="guide-head">
          <h2 id="guide-title">{t.guide.title}</h2>
          <button className="icon-button" aria-label={t.guide.close} onClick={onClose}>×</button>
        </header>
        <nav className="guide-tabs" role="tablist" aria-label={t.guide.sections}>
          {GUIDE_TABS.map((g) => (
            <button
              key={g.id}
              role="tab"
              id={`guide-tab-${g.id}`}
              aria-selected={g.id === tab}
              aria-controls="guide-panel"
              className={g.id === tab ? "active" : undefined}
              onClick={() => onTab(g.id)}
            >
              {t.guide.tabs[g.id]}
            </button>
          ))}
        </nav>
        <div className="guide-body" role="tabpanel" id="guide-panel" aria-labelledby={`guide-tab-${tab}`}>
          <Current category={category} />
        </div>
      </div>
    </div>
  );
}
