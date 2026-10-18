import {
  ArrowUpRight,
  Check,
  ScanLine,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { ErrorBox } from "../App";
import { Heading } from "../components/receipt-ui";
import type { Receipt } from "../types";
export function Scan() {
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [error, setError] = useState("");
  const [stage, setStage] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  useEffect(() => {
    if (!busy) return;
    const timer = setInterval(() => setStage((s) => Math.min(s + 1, 2)), 2200);
    return () => clearInterval(timer);
  }, [busy]);
  async function upload(file?: File) {
    if (!file || busy) return;
    setError("");
    if (file.size > 12 * 1024 * 1024) {
      setError("Please choose a receipt smaller than 12 MB.");
      return;
    }
    setBusy(true);
    setStage(0);
    const form = new FormData();
    form.append("file", file);
    try {
      const receipt = await api<Receipt>("/receipts/upload", {
        method: "POST",
        body: form,
      });
      navigate(`/receipts/${receipt.id}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Heading
        kicker="FROM PAPER TO PERSPECTIVE"
        title="Meet your next insight."
        description="One receipt is all it takes. We’ll help you read between the lines."
      />
      <div className="scan-layout">
        <section className="glass upload-panel">
          <ErrorBox message={error} />
          <div
            className={`dropzone ${drag ? "dragging" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDrag(false);
              void upload(e.dataTransfer.files[0]);
            }}
          >
            <div className="upload-orbit">
              <UploadCloud size={40} />
            </div>
            <span className="eyebrow">A LITTLE PAPER. A LOT OF POTENTIAL.</span>
            <h2>
              {busy ? "Looking between the lines…" : "Drop your receipt here."}
            </h2>
            <p>
              {busy
                ? "Extracting text and preparing a draft for your review."
                : "Or choose a file. We’ll take it from here."}
            </p>
            <input
              ref={input}
              type="file"
              accept="image/png,image/jpeg,image/webp,application/pdf"
              className="sr-only"
              tabIndex={-1}
              onChange={(e) => void upload(e.target.files?.[0])}
            />
            <button
              className="solid-button"
              disabled={busy}
              onClick={() => input.current?.click()}
            >
              {busy ? (
                <>
                  <span className="spinner" /> Processing receipt
                </>
              ) : (
                <>
                  Choose a receipt <ArrowUpRight size={18} />
                </>
              )}
            </button>
            <small>JPG, PNG, WebP or single-page PDF · Up to 12 MB</small>
          </div>
          {busy && (
            <ol className="processing-steps" aria-live="polite">
              {[
                "Validating your upload",
                "Extracting receipt text",
                "Preparing your review",
              ].map((s, i) => (
                <li key={s} className={stage >= i ? "active" : ""}>
                  {i < stage ? <Check size={15} /> : <span>{i + 1}</span>}
                  {s}
                </li>
              ))}
            </ol>
          )}
          <div className="upload-security">
            <ShieldCheck size={17} />
            <span>
              Your receipt is stored privately and only accessible to your
              account.
            </span>
          </div>
        </section>
        <aside className="scan-aside">
          <span className="eyebrow">A BETTER SCAN STARTS HERE</span>
          <h2>
            A few little things
            <br />
            make a big difference.
          </h2>
          {[
            [
              "01",
              "Keep it clear",
              "A sharp photo helps us read the small print.",
            ],
            [
              "02",
              "Get the whole picture",
              "Include the merchant, every item, and the total.",
            ],
            [
              "03",
              "Make it yours",
              "Review and correct every detail before investigating.",
            ],
          ].map(([n, title, text]) => (
            <div className="scan-tip" key={n}>
              <span>{n}</span>
              <div>
                <h3>{title}</h3>
                <p>{text}</p>
              </div>
            </div>
          ))}
          <div className="scan-tip-note">
            <Sparkle />
            OCR can misread receipts. You always have the final say.
          </div>
        </aside>
      </div>
    </>
  );
}

function Sparkle() {
  return <ScanLine size={20} />;
}
