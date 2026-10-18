import { Plus, Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { categories } from "../api";
import { ErrorBox, Loading } from "../App";
import { Empty, Heading, ReceiptRows, useData } from "../components/receipt-ui";
import type { Receipt } from "../types";
export function Library() {
  const { data, error } = useData<Receipt[]>("/receipts");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loading />;
  const filtered = data.filter(
    (r) =>
      `${r.merchant} ${r.items.map((i) => i.name).join(" ")}`
        .toLowerCase()
        .includes(query.toLowerCase()) &&
      (!category || r.category === category) &&
      (!status || r.status === status),
  );
  return (
    <>
      <Heading
        kicker="YOUR PAPER TRAIL, REIMAGINED"
        title="A memory for every receipt."
        description={`${data.length} receipts. All in one place. All part of your picture.`}
      >
        <Link to="/scan" className="solid-button">
          <Plus size={17} /> New receipt
        </Link>
      </Heading>
      <section className="glass panel">
        <div className="filters">
          <div className="search-field">
            <Search size={17} />
            <input
              aria-label="Search receipts"
              placeholder="Search merchants or products…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <select
            aria-label="Category filter"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
          <select
            aria-label="Status filter"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All receipts</option>
            <option value="review">Needs review</option>
            <option value="confirmed">Confirmed</option>
          </select>
        </div>
        {filtered.length ? (
          <ReceiptRows receipts={filtered} />
        ) : (
          <Empty
            title={
              data.length
                ? "Nothing in this corner."
                : "Your story starts here."
            }
            text={
              data.length
                ? "Try another merchant, category, or status."
                : "Upload your first receipt to start building your price memory."
            }
          />
        )}
      </section>
    </>
  );
}
