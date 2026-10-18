import {
  ArrowRight,
  ArrowUpRight,
  ChartNoAxesCombined,
  Check,
  CheckCheck,
  ChevronLeft,
  CircleAlert,
  Download,
  Fingerprint,
  Plus,
  ScanLine,
  Trash2,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { api, categories, money } from "../api";
import { ErrorBox, Loading } from "../App";
import { chartStyle, Heading, useData } from "../components/receipt-ui";
import type { Alert, Investigation, Item, Receipt } from "../types";
function ReceiptPreview({
  receipt,
  lines,
  selected,
}: {
  receipt: Receipt;
  lines: number[];
  selected: string;
}) {
  const [zoom, setZoom] = useState(1);
  return (
    <section className="glass receipt-preview">
      <div className="panel-heading">
        <span className="eyebrow">THE ORIGINAL</span>
        <div className="preview-tools">
          <button
            aria-label="Zoom out"
            onClick={() => setZoom(Math.max(1, zoom - 0.25))}
          >
            <ZoomOut size={17} />
          </button>
          <span>{Math.round(zoom * 100)}%</span>
          <button
            aria-label="Zoom in"
            onClick={() => setZoom(Math.min(2, zoom + 0.25))}
          >
            <ZoomIn size={17} />
          </button>
        </div>
      </div>
      <div className="image-scroll">
        <div className="receipt-image-wrap" style={{ width: `${zoom * 100}%` }}>
          <img
            src={receipt.image_url}
            alt={`Original receipt from ${receipt.merchant}`}
          />
          {receipt.ocr_lines.map(
            (line, i) =>
              lines.includes(i) && (
                <div
                  className="evidence-highlight"
                  key={i}
                  style={{
                    left: `${line.box[0] * 100}%`,
                    top: `${line.box[1] * 100}%`,
                    width: `${line.box[2] * 100}%`,
                    height: `${line.box[3] * 100}%`,
                  }}
                  title={line.text}
                />
              ),
          )}
        </div>
      </div>
      <div className="preview-caption">
        <ScanLine size={15} />
        {selected
          ? lines.length
            ? "Highlighted evidence for the selected alert."
            : "This alert compares transaction records; no specific OCR region is available."
          : "Select an insight to see its evidence."}
      </div>
      <details className="ocr-transcript">
        <summary>
          View extracted text · {Math.round(receipt.confidence * 100)}% OCR
          confidence
        </summary>
        <pre>
          {receipt.raw_text ||
            "No text was extracted. Enter receipt details manually."}
        </pre>
      </details>
    </section>
  );
}

function ReceiptEditor({
  receipt,
  onSaved,
  onCancel,
}: {
  receipt: Receipt;
  onSaved: (r: Receipt) => void;
  onCancel: () => void;
}) {
  const [draft, setDraft] = useState<Receipt>(receipt);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const update = (key: string, value: unknown) =>
    setDraft((d) => ({ ...d, [key]: value }));
  const updateItem = (index: number, key: string, value: unknown) =>
    setDraft((d) => ({
      ...d,
      items: d.items.map((item, i) =>
        i === index ? { ...item, [key]: value } : item,
      ),
    }));
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await api<Receipt>(`/receipts/${receipt.id}`, {
        method: "PATCH",
        body: JSON.stringify(draft),
      });
      const r = await api<Receipt>(`/receipts/${receipt.id}/confirm`, {
        method: "POST",
      });
      onSaved(r);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="glass panel editor">
      <span className="eyebrow">YOU HAVE THE FINAL SAY</span>
      <h2>A quick second look.</h2>
      <p>
        Check the extraction against your receipt. Confirm only when the details
        look right.
      </p>
      <ErrorBox message={error} />
      {receipt.warnings.map((w) => (
        <div className="notice" key={w}>
          <CircleAlert size={16} />
          {w}
        </div>
      ))}
      <form onSubmit={save}>
        <div className="form-grid">
          <label>
            Merchant
            <input
              value={draft.merchant}
              onChange={(e) => update("merchant", e.target.value)}
              required
              maxLength={200}
            />
          </label>
          <label>
            Purchase date
            <input
              type="date"
              value={draft.purchase_date || ""}
              onChange={(e) => update("purchase_date", e.target.value)}
              required
            />
          </label>
          <label>
            Category
            <select
              value={draft.category}
              onChange={(e) => update("category", e.target.value)}
            >
              {categories.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </label>
          <label>
            Currency
            <select
              value={draft.currency}
              onChange={(e) => update("currency", e.target.value)}
            >
              {["INR", "USD", "EUR", "GBP"].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="line-items-heading">
          <h3>Line items</h3>
          <span>Amount = full line total</span>
        </div>
        {draft.items.map((item, index) => (
          <div className="edit-item" key={index}>
            <label className="item-name">
              Product
              <input
                aria-label={`Product ${index + 1}`}
                value={item.name}
                onChange={(e) => updateItem(index, "name", e.target.value)}
                required
                maxLength={200}
              />
            </label>
            <label>
              Qty
              <input
                type="number"
                min="0.001"
                step="0.001"
                value={item.quantity}
                onChange={(e) => updateItem(index, "quantity", e.target.value)}
                required
              />
            </label>
            <label>
              Unit
              <select
                value={item.unit}
                onChange={(e) => updateItem(index, "unit", e.target.value)}
              >
                {["each", "g", "kg", "ml", "l"].map((u) => (
                  <option key={u}>{u}</option>
                ))}
              </select>
            </label>
            <label>
              Amount
              <input
                type="number"
                min="0"
                step="0.01"
                value={item.amount}
                onChange={(e) => updateItem(index, "amount", e.target.value)}
                required
              />
            </label>
            <button
              className="delete-item"
              type="button"
              aria-label={`Remove ${item.name || "item"}`}
              onClick={() =>
                update(
                  "items",
                  draft.items.filter((_, i) => i !== index),
                )
              }
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        <button
          type="button"
          className="text-link add-item"
          onClick={() =>
            update("items", [
              ...draft.items,
              {
                name: "",
                quantity: "1",
                unit: "each",
                amount: "0.00",
                line_index: null,
              } satisfies Item,
            ])
          }
        >
          <Plus size={15} /> Add a line item
        </button>
        <div className="form-grid totals">
          {(
            [
              "subtotal",
              "tax",
              "discount",
              "fees",
              "rounding",
              "total",
            ] as const
          ).map((key) => (
            <label key={key}>
              {key === "total" ? "Final amount" : key}
              <input
                type="number"
                min={key === "rounding" ? "-10" : "0"}
                step="0.01"
                value={draft[key] ?? ""}
                required={key !== "subtotal"}
                onChange={(e) =>
                  update(
                    key,
                    e.target.value === "" && key === "subtotal"
                      ? null
                      : e.target.value,
                  )
                }
              />
            </label>
          ))}
        </div>
        <div className="editor-actions">
          <button
            disabled={busy || !draft.items.length}
            className="solid-button"
          >
            {busy ? "Saving your review…" : "Confirm & investigate"}
            <ArrowRight size={17} />
          </button>
          {receipt.status === "confirmed" && (
            <button type="button" className="outline-button" onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </section>
  );
}

export function ReceiptPage() {
  const { id } = useParams();
  const {
    data: receipt,
    error,
    setData: setReceipt,
  } = useData<Receipt>(`/receipts/${id}`);
  const [analysis, setAnalysis] = useState<Investigation | null>(null);
  const [editing, setEditing] = useState(false);
  const [selected, setSelected] = useState<Alert | null>(null);
  const [actionError, setActionError] = useState("");
  const [pending, setPending] = useState(false);
  async function refresh() {
    try {
      setAnalysis(await api<Investigation>(`/receipts/${id}/investigation`));
      setActionError("");
    } catch (e) {
      setActionError((e as Error).message);
    }
  }
  useEffect(() => {
    if (receipt?.status === "confirmed") void refresh();
  }, [receipt]);
  async function decide(alert: Alert, action: string) {
    setPending(true);
    try {
      await api(`/receipts/${id}/alerts/${encodeURIComponent(alert.key)}`, {
        method: "PATCH",
        body: JSON.stringify({ action }),
      });
      await refresh();
    } catch (e) {
      setActionError((e as Error).message);
    } finally {
      setPending(false);
    }
  }
  if (error) return <ErrorBox message={error} />;
  if (!receipt) return <Loading />;
  const review = editing || receipt.status !== "confirmed";
  return (
    <>
      <Link to="/receipts" className="back-link">
        <ChevronLeft size={15} /> Your receipt library
      </Link>
      <Heading
        kicker={review ? "REVIEW THE DETAILS" : "THE RECEIPT INTELLIGENCE LAB"}
        title={receipt.merchant}
        description={`${receipt.purchase_date || "Date to be reviewed"} · ${receipt.category} · ${receipt.total === null ? "Total to be reviewed" : money(receipt.total, receipt.currency)}`}
      >
        <div className="heading-actions">
          {!review && (
            <button className="outline-button" onClick={() => setEditing(true)}>
              Correct details
            </button>
          )}
          <a
            className="outline-button"
            href={`/api/reports/export?receipt_id=${id}`}
          >
            <Download size={16} /> Report
          </a>
        </div>
      </Heading>
      <ErrorBox message={actionError} />
      <div className="investigation-layout">
        <ReceiptPreview
          receipt={receipt}
          lines={selected?.lines || []}
          selected={selected?.key || ""}
        />
        {review ? (
          <ReceiptEditor
            receipt={receipt}
            onCancel={() => setEditing(false)}
            onSaved={(r) => {
              setReceipt(r);
              setEditing(false);
              setSelected(null);
            }}
          />
        ) : (
          <div className="investigation-panels">
            {!analysis ? (
              <Loading label="Connecting the dots…" />
            ) : (
              <>
                <div className="investigation-summary">
                  <span className="live-dot" /> THREE ENGINES. ONE RECEIPT.
                  <span>
                    {analysis.alerts.filter((a) => a.state === "open").length}{" "}
                    to review
                  </span>
                </div>
                {[
                  {
                    kind: "billing",
                    n: "01",
                    title: "Receipt X-Ray",
                    subtitle: "The numbers, under a microscope.",
                    icon: ScanLine,
                    message: analysis.billing_message,
                  },
                  {
                    kind: "price",
                    n: "02",
                    title: "Price Memory",
                    subtitle: "Because every price has a past.",
                    icon: Fingerprint,
                    message: analysis.price_message,
                  },
                  {
                    kind: "spending",
                    n: "03",
                    title: "Expense Detective",
                    subtitle: "The bigger picture behind the purchase.",
                    icon: ChartNoAxesCombined,
                    message: analysis.history_message,
                  },
                ].map((engine) => (
                  <section
                    className="glass intelligence-panel"
                    key={engine.kind}
                  >
                    <div className="engine-panel-heading">
                      <span className="engine-icon">
                        <engine.icon size={23} />
                      </span>
                      <div>
                        <span className="eyebrow">ENGINE {engine.n}</span>
                        <h2>{engine.title}</h2>
                        <p>{engine.subtitle}</p>
                      </div>
                      <span className="engine-number">{engine.n}</span>
                    </div>
                    <p className="engine-message">{engine.message}</p>
                    {analysis.alerts
                      .filter(
                        (a) =>
                          a.kind === engine.kind ||
                          (engine.kind === "billing" && a.kind === "ocr"),
                      )
                      .map((a) => (
                        <article
                          key={a.key}
                          className={`alert-card ${selected?.key === a.key ? "selected" : ""} ${a.state !== "open" ? "resolved" : ""}`}
                        >
                          <button
                            className="alert-select"
                            onClick={() => setSelected(a)}
                          >
                            <span className={`alert-type ${a.kind}`}>
                              {a.kind === "ocr"
                                ? "EXTRACTION UNCERTAINTY"
                                : a.state === "open"
                                  ? "WORTH A LOOK"
                                  : a.state.toUpperCase()}
                            </span>
                            <h3>{a.title}</h3>
                            <p>{a.evidence}</p>
                            <span className="text-link">
                              View evidence <ArrowUpRight size={14} />
                            </span>
                          </button>
                          <div className="alert-actions">
                            {a.state === "open" ? (
                              <>
                                <button
                                  disabled={pending}
                                  onClick={() => void decide(a, "expected")}
                                >
                                  <Check size={13} /> Mark as expected
                                </button>
                                <button
                                  disabled={pending}
                                  onClick={() => void decide(a, "dismissed")}
                                >
                                  <X size={13} /> Dismiss
                                </button>
                              </>
                            ) : (
                              <button
                                disabled={pending}
                                onClick={() => void decide(a, "open")}
                              >
                                Reopen alert
                              </button>
                            )}
                          </div>
                        </article>
                      ))}
                    {engine.kind === "price" && (
                      <>
                        {analysis.match_candidates.map((c, i) => (
                          <div className="match-candidate" key={i}>
                            <p>
                              Same product? <strong>{c.name}</strong> ↔{" "}
                              <strong>{c.historical_name}</strong>
                            </p>
                            <small>
                              {c.merchant} · {c.date} · Similar name;
                              confirmation needed.
                            </small>
                            <button
                              disabled={pending}
                              className="text-link"
                              onClick={async () => {
                                setPending(true);
                                try {
                                  await api(`/receipts/${id}/matches`, {
                                    method: "POST",
                                    body: JSON.stringify(c),
                                  });
                                  await refresh();
                                } catch (e) {
                                  setActionError((e as Error).message);
                                } finally {
                                  setPending(false);
                                }
                              }}
                            >
                              <CheckCheck size={15} /> Confirm product match
                            </button>
                          </div>
                        ))}
                        {analysis.price_trends.map((trend, i) => (
                          <div className="price-trend" key={i}>
                            <div>
                              <strong>{trend.name}</strong>
                              <span>
                                {trend.change !== null
                                  ? `${trend.change > 0 ? "+" : ""}${trend.change}%`
                                  : "No percentage baseline"}{" "}
                                · per {trend.unit}
                              </span>
                            </div>
                            <ResponsiveContainer width="100%" height={135}>
                              <LineChart data={trend.points}>
                                <XAxis
                                  dataKey="date"
                                  tick={{ fill: "#fff", fontSize: 13 }}
                                  axisLine={false}
                                  tickLine={false}
                                />
                                <Tooltip contentStyle={chartStyle} />
                                <Line
                                  dataKey="price"
                                  stroke="#ffe0b1"
                                  strokeWidth={2}
                                  dot={{ r: 3 }}
                                />
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                        ))}
                      </>
                    )}
                  </section>
                ))}
                <p className="data-note">
                  Signals to investigate, not conclusions about fraud. Your
                  receipt review improves every comparison.
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
}
