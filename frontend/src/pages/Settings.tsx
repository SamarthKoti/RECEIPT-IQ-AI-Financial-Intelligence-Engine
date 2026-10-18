import { Check, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import { ErrorBox, useAuth } from "../App";
import { Heading } from "../components/receipt-ui";
import type { User } from "../types";
export function Settings() {
  const { user, setUser } = useAuth();
  const [name, setName] = useState(user!.name);
  const [currency, setCurrency] = useState(user!.currency);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  return (
    <>
      <Heading
        kicker="MAKE YOURSELF AT HOME"
        title="Your space. Your preferences."
        description="The little details that make this picture yours."
      />
      <section className="glass panel settings-panel">
        <h2>Your profile</h2>
        <p className="muted">
          Keep your account details and financial view up to date.
        </p>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setError("");
            setBusy(true);
            setSaved(false);
            try {
              setUser(
                await api<User>("/auth/me", {
                  method: "PATCH",
                  body: JSON.stringify({ name, currency }),
                }),
              );
              setSaved(true);
            } catch (e) {
              setError((e as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <ErrorBox message={error} />
          <label>
            Full name
            <input
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setSaved(false);
              }}
              minLength={2}
              maxLength={100}
              required
            />
          </label>
          <label>
            Email address
            <input value={user!.email} readOnly />
            <small>Your sign-in email.</small>
          </label>
          <label>
            Preferred currency
            <select
              value={currency}
              onChange={(e) => {
                setCurrency(e.target.value);
                setSaved(false);
              }}
            >
              <option value="INR">INR — Indian rupee</option>
              <option value="USD">USD — US dollar</option>
              <option value="EUR">EUR — Euro</option>
              <option value="GBP">GBP — British pound</option>
            </select>
            <small>
              Sets the default for new receipts and filters analytics. Existing
              receipts retain their currency.
            </small>
          </label>
          <button disabled={busy} className="solid-button">
            {busy ? "Saving…" : "Save preferences"}
            <Check size={17} />
          </button>
          {saved && (
            <p className="success" role="status">
              Preferences saved. Your overview will use {currency}.
            </p>
          )}
        </form>
        <div className="settings-security">
          <ShieldCheck size={23} />
          <div>
            <h3>A private space for your receipts.</h3>
            <p>
              Your session uses a protected cookie. Uploaded receipts and
              reports are restricted to your account.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
