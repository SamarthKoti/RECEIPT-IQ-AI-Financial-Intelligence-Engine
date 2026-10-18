import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, money } from "../api";
import { ErrorBox, Loading } from "../App";
import { chartStyle, palette } from "./receipt-ui";

type Detail = {
  count: number;
  total: string;
  average: string;
  currency: string;
  daily: { date: string; total: string; cumulative: string; count: number }[];
  merchants: { name: string; total: string; count: number }[];
  categories: string[];
  monthly_categories: Record<string, string>[];
  weekdays: {
    day: string;
    total: string;
    count: number;
    average: string | null;
  }[];
};
const tick = { fill: "#fff7ef", fontSize: 13 };
const compact = (value: number) =>
  new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);

export function DetailedAnalytics() {
  const [period, setPeriod] = useState("");
  const [data, setData] = useState<Detail | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setData(null);
    setError("");
    api<Detail>(`/analytics/details${period ? `?days=${period}` : ""}`)
      .then((result) => {
        if (active) setData(result);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [period]);
  const format = (value: unknown) =>
    money(Number(value), data?.currency || "INR");
  return (
    <section
      className="detailed-analytics"
      aria-label="Detailed spending analytics"
    >
      <div className="panel-heading detail-heading">
        <div>
          <span className="eyebrow">LOOK A LITTLE CLOSER</span>
          <h2>The patterns behind your purchases</h2>
          <p>
            Explore when you spend, where it goes, and how your mix changes.
          </p>
        </div>
        <label>
          Detailed view
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="">All recorded dates</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </label>
      </div>
      <ErrorBox message={error} />
      {!data && !error ? (
        <Loading label="Reading your spending patterns…" />
      ) : (
        data && (
          <>
            <div className="detail-summary">
              <span>
                <strong>{data.count}</strong> confirmed purchases
              </span>
              <span>
                <strong>{money(data.average, data.currency)}</strong> average
                purchase
              </span>
              <span>
                <strong>{money(data.total, data.currency)}</strong> in this view
              </span>
            </div>
            {!data.count ? (
              <div className="glass empty">
                <h3>Your patterns start with your receipts.</h3>
                <p>
                  No confirmed {data.currency} receipts in this period. Choose a
                  wider range or confirm a receipt to populate these charts.
                </p>
              </div>
            ) : (
              <div className="detail-chart-grid">
                <article className="glass panel detail-chart">
                  <h3>Daily spending & running total</h3>
                  <p>
                    Bars show each purchase day. The line tracks accumulated
                    spending in this view.
                  </p>
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart
                      data={data.daily.map((d) => ({
                        ...d,
                        total: Number(d.total),
                        cumulative: Number(d.cumulative),
                      }))}
                      margin={{ top: 15, right: 10, bottom: 5, left: 0 }}
                    >
                      <CartesianGrid stroke="#ffffff26" vertical={false} />
                      <XAxis
                        dataKey="date"
                        tick={tick}
                        tickFormatter={(v) => String(v).slice(5)}
                        minTickGap={25}
                      />
                      <YAxis
                        yAxisId="daily"
                        tick={tick}
                        tickFormatter={compact}
                        width={50}
                      />
                      <YAxis
                        yAxisId="running"
                        orientation="right"
                        tick={tick}
                        tickFormatter={compact}
                        width={50}
                      />
                      <Tooltip contentStyle={chartStyle} formatter={format} />
                      <Legend />
                      <Bar
                        yAxisId="daily"
                        dataKey="total"
                        name="Daily spend · left axis"
                        fill="#f6a369"
                        radius={[5, 5, 0, 0]}
                        maxBarSize={40}
                      />
                      <Line
                        yAxisId="running"
                        dataKey="cumulative"
                        name="Running total · right axis"
                        stroke="#fff0c5"
                        strokeWidth={3}
                        dot={{ r: 4 }}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                  <small>
                    Only dates with confirmed receipts are plotted. Missing
                    receipts are not assumed to be zero spending.
                  </small>
                </article>
                <article className="glass panel detail-chart">
                  <h3>Where you spend most</h3>
                  <p>
                    Your six largest merchants by total spend. Compare
                    concentration across stores.
                  </p>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      layout="vertical"
                      data={data.merchants.map((m) => ({
                        ...m,
                        total: Number(m.total),
                      }))}
                      margin={{ right: 20, left: 0, top: 15, bottom: 5 }}
                    >
                      <CartesianGrid stroke="#ffffff26" horizontal={false} />
                      <XAxis
                        type="number"
                        tick={tick}
                        tickFormatter={compact}
                      />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={115}
                        tick={tick}
                        tickFormatter={(v) =>
                          String(v).length > 16
                            ? String(v).slice(0, 15) + "…"
                            : v
                        }
                      />
                      <Tooltip contentStyle={chartStyle} formatter={format} />
                      <Bar
                        dataKey="total"
                        name="Merchant spend"
                        fill="#ffc491"
                        radius={[0, 6, 6, 0]}
                        maxBarSize={35}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                  <small>
                    {data.merchants[0]?.name} leads with{" "}
                    {data.merchants[0]?.count} recorded{" "}
                    {data.merchants[0]?.count === 1 ? "purchase" : "purchases"}.
                  </small>
                </article>
                <article className="glass panel detail-chart">
                  <h3>Your category mix over time</h3>
                  <p>
                    Each monthly bar shows which categories contributed to the
                    total.
                  </p>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={data.monthly_categories.map((m) =>
                        Object.fromEntries(
                          Object.entries(m).map(([key, value]) => [
                            key,
                            key === "month" ? value : Number(value),
                          ]),
                        ),
                      )}
                      margin={{ top: 15, right: 12, left: 0, bottom: 5 }}
                    >
                      <CartesianGrid stroke="#ffffff26" vertical={false} />
                      <XAxis dataKey="month" tick={tick} />
                      <YAxis tick={tick} tickFormatter={compact} width={55} />
                      <Tooltip contentStyle={chartStyle} formatter={format} />
                      <Legend />
                      {data.categories.map((category, i) => (
                        <Bar
                          key={category}
                          dataKey={category}
                          stackId="spend"
                          fill={palette[i % palette.length]}
                          maxBarSize={65}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                  <small>
                    Recorded months may be incomplete; this chart describes
                    receipts you have confirmed.
                  </small>
                </article>
                <article className="glass panel detail-chart">
                  <h3>Which days bring bigger purchases?</h3>
                  <p>
                    Average receipt amount by weekday, rather than total spend,
                    makes purchase sizes comparable.
                  </p>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={data.weekdays.map((w) => ({
                        ...w,
                        average: w.average === null ? null : Number(w.average),
                      }))}
                      margin={{ top: 15, right: 12, left: 0, bottom: 5 }}
                    >
                      <CartesianGrid stroke="#ffffff26" vertical={false} />
                      <XAxis dataKey="day" tick={tick} />
                      <YAxis tick={tick} tickFormatter={compact} width={55} />
                      <Tooltip contentStyle={chartStyle} formatter={format} />
                      <Bar
                        dataKey="average"
                        name="Average purchase"
                        fill="#ebc69d"
                        radius={[5, 5, 0, 0]}
                        maxBarSize={40}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                  <small>
                    No bar means no recorded purchases that day. Small samples
                    describe activity, not a reliable prediction.
                  </small>
                </article>
              </div>
            )}
            <details className="analytics-table">
              <summary>View the numbers behind the charts</summary>
              <div className="table-scroll">
                <table>
                  <caption>Daily confirmed spending · {data.currency}</caption>
                  <thead>
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Receipts</th>
                      <th scope="col">Spend</th>
                      <th scope="col">Running total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.daily.map((d) => (
                      <tr key={d.date}>
                        <th scope="row">{d.date}</th>
                        <td>{d.count}</td>
                        <td>{money(d.total, data.currency)}</td>
                        <td>{money(d.cumulative, data.currency)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          </>
        )
      )}
    </section>
  );
}
