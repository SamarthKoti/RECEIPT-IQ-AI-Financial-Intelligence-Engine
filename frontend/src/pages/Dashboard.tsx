import {
  ArrowUpRight,
  ChartNoAxesCombined,
  Fingerprint,
  Plus,
  ReceiptText,
  ScanLine,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { money } from "../api";
import { ErrorBox, Loading, useAuth } from "../App";
import {
  CategoryChart,
  Empty,
  Heading,
  ReceiptRows,
  TrendChart,
  useData,
} from "../components/receipt-ui";
import type { Overview } from "../types";
export function Dashboard() {
  const { user } = useAuth();
  const { data, error } = useData<Overview>("/analytics/overview");
  const cats = useData<{ name: string; value: string }[]>(
    "/analytics/categories",
  );
  const trends =
    useData<{ month: string; total: string }[]>("/analytics/trends");
  if (error || cats.error || trends.error)
    return <ErrorBox message={error || cats.error || trends.error} />;
  if (!data || !cats.data || !trends.data) return <Loading />;
  return (
    <>
      <Heading
        kicker="YOUR FINANCIAL PICTURE"
        title={`A little clearer, ${user!.name.split(" ")[0]}.`}
        description="The everyday numbers. The insights that matter."
      >
        <Link to="/scan" className="solid-button">
          <Plus size={18} /> Scan a receipt
        </Link>
      </Heading>
      <div className="metrics">
        <div className="glass metric">
          <span>
            Total expenses <ChartNoAxesCombined size={19} />
          </span>
          <strong>{money(data.total, data.currency)}</strong>
          <small>Across {data.confirmed} confirmed receipts</small>
        </div>
        <div className="glass metric">
          <span>
            Receipts collected <ReceiptText size={19} />
          </span>
          <strong>{String(data.count).padStart(2, "0")}</strong>
          <small>A memory for every purchase</small>
        </div>
        <div className="glass metric">
          <span>
            Worth a closer look <ScanLine size={19} />
          </span>
          <strong>
            {String(data.alerts).padStart(2, "0")}
            <i>open alerts</i>
          </strong>
          <small>Review signals, not conclusions</small>
        </div>
      </div>
      <div className="dashboard-charts">
        <section className="glass panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">THE BIGGER PICTURE</span>
              <h2>Spending over time</h2>
            </div>
            <span className="badge">{data.currency} · Monthly</span>
          </div>
          <TrendChart data={trends.data} currency={data.currency} />
        </section>
        <section className="glass panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">WHERE IT GOES</span>
              <h2>By category</h2>
            </div>
            <Fingerprint size={21} />
          </div>
          <CategoryChart data={cats.data} currency={data.currency} />
        </section>
      </div>
      <section className="glass panel recent">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">YOUR PAPER TRAIL</span>
            <h2>Recent investigations</h2>
          </div>
          <Link to="/receipts" className="text-link">
            View library <ArrowUpRight size={16} />
          </Link>
        </div>
        {data.recent.length ? (
          <ReceiptRows receipts={data.recent} />
        ) : (
          <Empty />
        )}
      </section>
      <p className="data-note">
        <ShieldCheck size={13} />
        {data.scope}
      </p>
    </>
  );
}
