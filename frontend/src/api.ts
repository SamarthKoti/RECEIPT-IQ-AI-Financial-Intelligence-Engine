let csrfRequest: Promise<string> | null = null;

async function csrfToken(): Promise<string> {
  // Bootstrap before every mutation so expired/deleted cookies recover naturally.
  // Share concurrent bootstraps to avoid racing two initial Set-Cookie responses.
  if (!csrfRequest) {
    csrfRequest = fetch("/api/auth/csrf", {
      credentials: "include",
      cache: "no-store",
    })
      .then(async (response) => {
        if (!response.ok)
          throw new Error(
            "Unable to prepare a secure request. Please refresh and try again.",
          );
        const data = await response.json();
        if (typeof data.csrf_token !== "string")
          throw new Error("Invalid security token response.");
        return data.csrf_token as string;
      })
      .finally(() => {
        csrfRequest = null;
      });
  }
  return csrfRequest;
}

export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("X-Receipt-IQ", "1");
  if (!(options.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  if (
    !["GET", "HEAD", "OPTIONS"].includes(
      (options.method || "GET").toUpperCase(),
    )
  ) {
    headers.set("X-CSRF-Token", await csrfToken());
  }
  const response = await fetch(`/api${path}`, {
    ...options,
    credentials: "include",
    headers,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail
          .map(
            (x: { msg: string; loc: string[] }) =>
              `${x.loc.slice(1).join(" ")}: ${x.msg}`,
          )
          .join("; ")
      : data.detail;
    throw new Error(
      detail || `Request failed (${response.status}). Please try again.`,
    );
  }
  return response.json();
}
export const money = (value: string | number | null, currency = "INR") =>
  new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
export const categories = [
  "Groceries",
  "Dining",
  "Transport",
  "Shopping",
  "Health",
  "Utilities",
  "Other",
];
