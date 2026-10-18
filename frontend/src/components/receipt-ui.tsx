import { ArrowUpRight, ReceiptText } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, money } from "../api";
import type { Receipt } from "../types";
export function useData<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    api<T>(url)
      .then((x) => {
        if (active) setData(x);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [url]);
  return { data, error, setData };
}

export const Empty = ({
  title = "A fresh start.",
  text = "Your insights begin with your first receipt.",
}: {
  title?: string;
  text?: string;
}) => (
  <div className="empty">
    <div className="empty-icon">
      <ReceiptText size={30} />
    </div>
    <h3>{title}</h3>
    <p>{text}</p>
    <Link to="/scan" className="outline-button">
      Scan a receipt <ArrowUpRight size={16} />
    </Link>
  </div>
);

export const Heading = ({
  kicker,
  title,
  description,
  children,
}: {
  kicker: string;
  title: string;
  description: string;
  children?: React.ReactNode;
}) => (
  <div className="page-heading">
    <div>
      <span className="eyebrow">{kicker}</span>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
    {children}
  </div>
);

export const palette = [
  "#f69b62",
  "#e66e36",
  "#e9c9a6",
  "#b8886b",
  "#f7dfc0",
  "#b0b29b",
  "#d0a493",
];

export const chartStyle = {
  background: "#fbf5ec",
  border: "1px solid #e4c6b3",
  borderRadius: 12,
  color: "#6b4938",
};

export function TrendChart({
  data,
  currency,
}: {
  data: { month: string; total: string }[];
  currency: string;
}) {
  return data.length ? (
    <ResponsiveContainer width="100%" height={245}>
      <AreaChart
        data={data.map((x) => ({ ...x, total: Number(x.total) }))}
        margin={{ left: 0, right: 16, top: 12, bottom: 0 }}
      >
        <defs>
          <linearGradient id="expenseFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f79450" stopOpacity={0.65} />
            <stop offset="100%" stopColor="#f79450" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,.13)" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fill: "#fff7ef", fontSize: 13 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "#fff7ef", fontSize: 13 }}
          axisLine={false}
          tickLine={false}
          width={55}
        />
        <Tooltip
          contentStyle={chartStyle}
          formatter={(v) => money(Number(v), currency)}
        />
        <Area
          type="monotone"
          dataKey="total"
          name="Spending"
          stroke="#ffcf9e"
          strokeWidth={2.5}
          dot={{ r: 4, fill: '#ffcf9e' }}
          fill="url(#expenseFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  ) : (
    <div className="chart-empty">
      Your monthly story will appear here.
      <span>Confirm a receipt to get started.</span>
    </div>
  );
}

export function CategoryChart({
  data,
  currency,
}: {
  data: { name: string; value: string }[];
  currency: string;
}) {
  return data.length ? (
    <div className="category-chart">
      <ResponsiveContainer width="100%" height={190}>
        <PieChart>
          <Pie
            data={data.map((x) => ({ ...x, value: Number(x.value) }))}
            dataKey="value"
            innerRadius={58}
            outerRadius={80}
            paddingAngle={5}
            stroke="none"
          >
            {data.map((x, i) => (
              <Cell key={x.name} fill={palette[i % palette.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={chartStyle}
            formatter={(v) => money(Number(v), currency)}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="category-legend">
        {data.map((x, i) => (
          <div key={x.name}>
            <span>
              <i style={{ background: palette[i % palette.length] }} />
              {x.name}
            </span>
            <strong>{money(x.value, currency)}</strong>
          </div>
        ))}
      </div>
    </div>
  ) : (
    <div className="chart-empty">
      Every category has a story.<span>Yours is yet to begin.</span>
    </div>
  );
}

export function ReceiptRows({ receipts }: { receipts: Receipt[] }) {
  return (
    <div className="receipt-rows">
      {receipts.map((r) => (
        <Link className="receipt-row" to={`/receipts/${r.id}`} key={r.id}>
          <span className="receipt-icon">
            <ReceiptText size={21} />
          </span>
          <span className="receipt-merchant">
            <strong>{r.merchant}</strong>
            <small>
              {r.purchase_date || "Date needs review"} · {r.category}
            </small>
          </span>
          <span className={`badge ${r.status === "review" ? "warning" : ""}`}>
            {r.possible_duplicate
              ? "Possible duplicate"
              : r.status === "review"
                ? "Needs review"
                : "Investigated"}
          </span>
          <strong>{r.total === null ? "—" : money(r.total, r.currency)}</strong>
          <ArrowUpRight size={17} />
        </Link>
      ))}
    </div>
  );
}
