import { ArrowUpRight, CircleAlert, Download } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, money } from "../api";
import { ErrorBox, Loading, useAuth } from "../App";
import {
  CategoryChart,
  chartStyle,
  Heading,
  TrendChart,
  useData,
} from "../components/receipt-ui";
import type { Investigation, Overview, Receipt } from "../types";
import { DetailedAnalytics } from "../components/DetailedAnalytics";
export function Insights() {
  const { user } = useAuth();
  const overview = useData<Overview>("/analytics/overview");
  const trends =
    useData<{ month: string; total: string }[]>("/analytics/trends");
  const cats = useData<{ name: string; value: string }[]>(
    "/analytics/categories",
  );
  const [selected, setSelected] = useState("");
  const [investigation, setInvestigation] = useState<Investigation | null>(
    null,
  );
  const [error, setError] = useState("");
  const receipts = useData<Receipt[]>("/receipts");
  useEffect(() => {
    setInvestigation(null);
    setError("");
    if (!selected) return;
    let active = true;
    api<Investigation>(`/receipts/${selected}/investigation`)
      .then((r) => {
        if (active) setInvestigation(r);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [selected]);
  if (overview.error || trends.error || cats.error || receipts.error)
    return (
      <ErrorBox
        message={overview.error || trends.error || cats.error || receipts.error}
      />
    );
  if (!overview.data || !trends.data || !cats.data || !receipts.data)
    return <Loading />;
  const rows = trends.data;
  const last = Number(rows.at(-1)?.total || 0),
    previous = Number(rows.at(-2)?.total || 0);
  return (
    <>
      <Heading
        kicker="STEP BACK. SEE MORE."
        title="Your everyday, in perspective."
        description="Real receipts. Thoughtful comparisons. A clearer picture over time."
      >
        <a className="outline-button" href="/api/reports/export">
          <Download size={16} /> Export report
        </a>
      </Heading>
      <div className="metrics">
        <div className="glass metric">
          <span>Recorded spending</span>
          <strong>{money(overview.data.total, user!.currency)}</strong>
          <small>Confirmed receipts · {user!.currency}</small>
        </div>
        <div className="glass metric">
          <span>Latest recorded month</span>
          <strong>{money(last, user!.currency)}</strong>
          <small>{rows.at(-1)?.month || "No history yet"}</small>
        </div>
        <div className="glass metric">
          <span>Change vs prior recorded month</span>
          <strong>
            {previous
              ? `${(((last - previous) / previous) * 100).toFixed(1)}%`
              : "—"}
          </strong>
          <small>
            {rows.length >= 2
              ? `${rows.at(-2)?.month} → ${rows.at(-1)?.month}`
              : "Two recorded months are needed"}
          </small>
        </div>
      </div>
      <div className="dashboard-charts">
        <section className="glass panel">
          <h2>Monthly spending</h2>
          <TrendChart data={rows} currency={user!.currency} />
        </section>
        <section className="glass panel">
          <h2>Category perspective</h2>
          <CategoryChart data={cats.data} currency={user!.currency} />
        </section>
      </div>
      <DetailedAnalytics />
      <section className="glass panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">FOLLOW THE DETAILS</span>
            <h2>Product histories & anomaly evidence</h2>
          </div>
          <span className="badge">{overview.data.alerts} open alerts</span>
        </div>
        <label className="history-select">
          Choose a confirmed receipt
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            <option value="">Select a receipt to explore</option>
            {receipts.data
              .filter((r) => r.status === "confirmed")
              .map((r) => (
                <option key={r.id} value={r.id}>
                  {r.merchant} · {r.purchase_date} · {r.currency}
                </option>
              ))}
          </select>
        </label>
        <ErrorBox message={error} />
        {selected && !investigation && !error && <Loading />}
        {investigation && (
          <>
            <p className="engine-message">{investigation.history_message}</p>
            {investigation.price_trends.length ? (
              investigation.price_trends.map((t, i) => (
                <div className="price-trend" key={i}>
                  <h3>
                    {t.name} · price per {t.unit}
                  </h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={t.points}>
                      <CartesianGrid stroke="rgba(255,255,255,.1)" />
                      <XAxis
                        dataKey="date"
                        tick={{ fill: "#fff", fontSize: 13 }}
                      />
                      <YAxis tick={{ fill: "#fff", fontSize: 13 }} />
                      <Tooltip contentStyle={chartStyle} />
                      <Line dataKey="price" stroke="#ffd5a5" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ))
            ) : (
              <p className="muted">{investigation.price_message}</p>
            )}
            {investigation.alerts
              .filter((a) => a.kind !== "ocr")
              .map((a) => (
                <Link
                  className="insight-row"
                  to={`/receipts/${selected}`}
                  key={a.key}
                >
                  <CircleAlert size={18} />
                  <span>
                    <strong>{a.title}</strong>
                    <small>{a.evidence}</small>
                  </span>
                  <span className="badge">{a.state}</span>
                  <ArrowUpRight size={16} />
                </Link>
              ))}
          </>
        )}
      </section>
      <p className="data-note">
        {overview.data.scope} Percentage changes compare recorded months, which
        may be incomplete.
      </p>
    </>
  );
}
