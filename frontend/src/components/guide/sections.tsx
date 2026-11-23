import type { ReactElement } from "react";
import { useI18n } from "../../i18n";
import type { Category } from "../../types";

// Same values as defaults.label_thresholds in config/categories.yaml; update both together.
const RECOMMENDED_FROM = 70;
const NEUTRAL_FROM = 45;

type Body = (props: { category: Category | undefined }) => ReactElement;

// Texts are in src/i18n (guide.*). Criterion names and weights come from the API.
function Start() {
  const g = useI18n().t.guide.start;
  return (
    <>
      <p>{g.intro}</p>
      <h3>{g.howTitle}</h3>
      <ol className="guide-steps">
        {g.steps.map(([title, body]) => (
          <li key={title}><strong>{title}</strong> {body}</li>
        ))}
      </ol>
    </>
  );
}

function Criteria({ category }: { category: Category | undefined }) {
  const g = useI18n().t.guide;
  return (
    <>
      <p>
        {g.criteria.intro} {category && g.criteria.defaults(category.name)}
      </p>
      <dl className="guide-criteria">
        {(category?.criteria ?? []).map((c) => {
          const info = g.info[c.id];
          return (
            <div key={c.id}>
              <dt>
                {c.name}
                <span className="guide-weight">{g.criteria.weight(Math.round(c.weight * 100))}</span>
              </dt>
              {info && (
                <dd>
                  <p>{info.measures}</p>
                  <p className="muted small"><strong>{g.criteria.source}</strong> {info.source}</p>
                  <p className="muted small"><strong>{g.criteria.better}</strong> {info.better}</p>
                </dd>
              )}
            </div>
          );
        })}
      </dl>
    </>
  );
}

function Reading() {
  const { t } = useI18n();
  const r = t.guide.reading;
  return (
    <>
      <h3>{r.scoreTitle}</h3>
      <p>{r.scoreText}</p>
      <ul className="guide-labels">
        <li><span className="chip recommended">{t.labels.recommended}</span> {r.recommendedRange(RECOMMENDED_FROM)}</li>
        <li><span className="chip neutral">{t.labels.neutral}</span> {r.neutralRange(NEUTRAL_FROM, RECOMMENDED_FROM)}</li>
        <li><span className="chip not_recommended">{t.labels.not_recommended}</span> {r.notRecommendedRange(NEUTRAL_FROM)}</li>
      </ul>
      <h3>{r.similarTitle}</h3>
      <p>{r.similarText}</p>
      <h3>{r.whyTitle}</h3>
      <p>
        {r.whyBefore} <span className="pos">{r.up}</span> {r.or} <span className="neg">{r.down}</span>{" "}
        {r.whyAfter}
      </p>
      <h3>{r.noDataTitle}</h3>
      <p>{r.noDataText}</p>
      <h3>{r.tcoTitle}</h3>
      <p>{r.tcoText}</p>
    </>
  );
}

function Limits() {
  const l = useI18n().t.guide.limits;
  return (
    <>
      <p>{l.intro}</p>
      <ul className="guide-list">
        {l.items.map((item) => <li key={item}>{item}</li>)}
      </ul>
      <p className="muted small">{l.method}</p>
    </>
  );
}

export const GUIDE_TABS = [
  { id: "start", Body: Start as Body },
  { id: "criteria", Body: Criteria as Body },
  { id: "reading", Body: Reading as Body },
  { id: "limits", Body: Limits as Body },
] as const;

export type GuideTab = (typeof GUIDE_TABS)[number]["id"];
