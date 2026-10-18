import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  ArrowUpRight,
  ChartNoAxesCombined,
  ChevronRight,
  Eye,
  EyeOff,
  Fingerprint,
  LayoutDashboard,
  LogOut,
  Menu,
  ReceiptText,
  ScanLine,
  Settings2,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import {
  createContext,
  lazy,
  Suspense,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { api } from "./api";
import type { User } from "./types";

const Dashboard = lazy(() =>
  import("./pages/Dashboard").then((m) => ({ default: m.Dashboard })),
);
const Insights = lazy(() =>
  import("./pages/Insights").then((m) => ({ default: m.Insights })),
);
const Library = lazy(() =>
  import("./pages/Library").then((m) => ({ default: m.Library })),
);
const ReceiptPage = lazy(() =>
  import("./pages/ReceiptPage").then((m) => ({ default: m.ReceiptPage })),
);
const Scan = lazy(() =>
  import("./pages/Scan").then((m) => ({ default: m.Scan })),
);
const Settings = lazy(() =>
  import("./pages/Settings").then((m) => ({ default: m.Settings })),
);

const Auth = createContext<{
  user: User | null;
  setUser: (u: User | null) => void;
}>({ user: null, setUser: () => {} });
export const useAuth = () => useContext(Auth);
export const ErrorBox = ({ message }: { message: string }) =>
  message ? (
    <div className="error" role="alert">
      {message}
    </div>
  ) : null;
export const Loading = ({
  label = "Bringing things into focus…",
}: {
  label?: string;
}) => (
  <div className="loading" role="status">
    <span className="spinner" />
    {label}
  </div>
);
export const Brand = () => (
  <Link to="/" className="brand" aria-label="Receipt IQ home">
    <span className="brand-icon">
      <ScanLine size={22} />
    </span>
    RECEIPT<span className="brand-iq">IQ</span>
    <span className="brand-dot" />
  </Link>
);

function Atmosphere() {
  return (
    <div className="atmosphere" aria-hidden="true">
      <div className="ambient-light" />
      <div className="orb orb-large" />
      <div className="orb orb-bottom" />
      <div className="orb orb-small" />
      <div className="orb orb-tiny" />
      <div className="ring ring-top" />
      <div className="ring ring-bottom" />
      <div className="grain" />
    </div>
  );
}

function Landing() {
  return (
    <div className="landing">
      <Atmosphere />
      <motion.main
        className="landing-glass"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9 }}
      >
        <header className="landing-header">
          <Brand />
          <nav>
            <a href="#intelligence">The intelligence</a>
            <a href="#how-it-works">How it works</a>
            <Link className="outline-button small" to="/login">
              Log in <ArrowUpRight size={14} />
            </Link>
          </nav>
        </header>
        <div className="hero-layout">
          <div className="hero-art">
            <div className="art-caption">
              <span className="live-dot" /> LESS GUESSWORK. MORE CLARITY.
            </div>
            <div className="floating-receipt">
              <div className="mini-brand">EVERYDAY, UNDERSTOOD.</div>
              <div className="receipt-scan">
                <ScanLine size={31} />
                <span>
                  One receipt.
                  <br />A clearer picture.
                </span>
              </div>
              <div className="receipt-dashes" />
              <div className="receipt-lines">
                <span />
                <span />
                <span />
              </div>
              <div className="receipt-result">
                <span className="check-dot">✓</span> A little more insight.
              </div>
            </div>
            <div className="orbit-label">
              <Sparkles size={15} /> Intelligence in the everyday
            </div>
          </div>
          <section className="hero-copy">
            <div className="eyebrow">
              <span /> YOUR EVERYDAY. A LITTLE SMARTER.
            </div>
            <h1>
              YOUR RECEIPTS.
              <br />
              <span>REIMAGINED.</span>
            </h1>
            <p>
              Don’t just scan your bills.
              <br />
              <strong>Understand them.</strong>
            </p>
            <div className="hero-description">
              Transform everyday receipts into intelligent financial insights.
              Detect billing errors, track price changes, and understand
              spending with AI-powered investigations.
            </div>
            <Link to="/scan" className="outline-button hero-cta">
              SCAN SMARTER <ArrowUpRight size={19} />
            </Link>
            <div className="hero-note">
              <ShieldCheck size={14} /> Your receipts. Your eyes only.
            </div>
          </section>
        </div>
        <footer className="landing-footer">
          <span>MEET YOUR FINANCIAL SIXTH SENSE</span>
          <a href="#intelligence">
            Explore the intelligence <span className="down-arrow">↓</span>
          </a>
          <span>01 — 03</span>
        </footer>
      </motion.main>
      <section className="below-fold" id="intelligence">
        <div className="section-intro">
          <span className="eyebrow">THREE ENGINES. ONE CLEARER PICTURE.</span>
          <h2>
            There’s more to a receipt
            <br />
            than the total.
          </h2>
          <p>
            A second look at the numbers. A memory for the prices.
            <br />A little perspective on the bigger picture.
          </p>
        </div>
        <div className="engine-grid">
          {[
            {
              n: "01",
              icon: ScanLine,
              title: "Receipt X-Ray",
              text: "Look between the lines.",
              description:
                "Reconcile the arithmetic, spot repeated items, and see exactly what needs a second look.",
            },
            {
              n: "02",
              icon: Fingerprint,
              title: "Price Memory",
              text: "Remember what you paid.",
              description:
                "Compare matched products over time, with quantities and units brought onto the same scale.",
            },
            {
              n: "03",
              icon: ChartNoAxesCombined,
              title: "Expense Detective",
              text: "Connect the everyday dots.",
              description:
                "Understand unusual spending through explainable comparisons with your own history.",
            },
          ].map((e) => (
            <article className="glass engine-card" key={e.n}>
              <div className="engine-top">
                <e.icon size={25} />
                <span>{e.n}</span>
              </div>
              <h3>{e.title}</h3>
              <h4>{e.text}</h4>
              <p>{e.description}</p>
              <Link to="/register">
                Take a closer look <ArrowUpRight size={16} />
              </Link>
            </article>
          ))}
        </div>
        <div id="how-it-works" className="how">
          <span className="eyebrow">FROM PAPER TO PERSPECTIVE</span>
          <h2>Upload. Review. Understand.</h2>
          <p>
            Bring a receipt. Check the extracted details. Let three independent
            engines help you investigate.
          </p>
          <Link to="/register" className="solid-button">
            Find your first insight <ArrowRight size={17} />
          </Link>
        </div>
        <footer className="site-footer">
          <Brand />
          <span>Financial clarity starts with the little things.</span>
          <span>© {new Date().getFullYear()} Receipt IQ</span>
        </footer>
      </section>
    </div>
  );
}

function AuthPage({ register = false }: { register?: boolean }) {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  if (user) return <Navigate to="/dashboard" replace />;
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    setError("");
    if (register && data.get("password") !== data.get("confirm")) {
      setError("Your passwords don’t match. Please try again.");
      return;
    }
    setBusy(true);
    try {
      const u = await api<User>(`/auth/${register ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(data)),
      });
      setUser(u);
      navigate("/dashboard");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth-scene">
      <Atmosphere />
      <header className="auth-header">
        <Brand />
        <Link to="/">
          Back to the everyday <ArrowUpRight size={16} />
        </Link>
      </header>
      <main className="auth-layout">
        <section className="auth-story">
          <span className="eyebrow">A LITTLE PAPER. A LOT OF POSSIBILITY.</span>
          <h1>
            Clarity looks
            <br />
            good on you.
          </h1>
          <p>
            Your spending tells a story.
            <br />
            Let’s make sense of it.
          </p>
          <div className="auth-story-note">
            <Fingerprint size={25} />
            <span>
              Private by design.
              <br />
              <small>Insights from your receipts, for you.</small>
            </span>
          </div>
        </section>
        <motion.section
          className="glass auth-card"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="auth-card-icon">
            <ScanLine size={26} />
          </div>
          <span className="eyebrow">YOUR FINANCIAL SIXTH SENSE</span>
          <h2>{register ? "A fresh perspective." : "Welcome back."}</h2>
          <p>
            {register
              ? "Create your account. Find clarity in the everyday."
              : "Your next insight is waiting for you."}
          </p>
          <form onSubmit={submit}>
            <ErrorBox message={error} />
            {register && (
              <label>
                Full name
                <input
                  name="name"
                  autoComplete="name"
                  placeholder="Your full name"
                  minLength={2}
                  maxLength={100}
                  required
                />
              </label>
            )}
            <label>
              Email address
              <input
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                required
              />
            </label>
            <label>
              Password
              <div className="password-field">
                <input
                  name="password"
                  type={show ? "text" : "password"}
                  autoComplete={register ? "new-password" : "current-password"}
                  placeholder={
                    register ? "At least 8 characters" : "Enter your password"
                  }
                  minLength={register ? 8 : 1}
                  maxLength={128}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShow(!show)}
                  aria-label={show ? "Hide password" : "Show password"}
                >
                  {show ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </label>
            {register && (
              <label>
                Confirm password
                <input
                  name="confirm"
                  type={show ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="One more time"
                  minLength={8}
                  required
                />
              </label>
            )}
            <button disabled={busy} className="solid-button auth-submit">
              {busy
                ? "One moment…"
                : register
                  ? "Create account"
                  : "Step into clarity"}
              <ArrowRight size={18} />
            </button>
          </form>
          <p className="auth-switch">
            {register ? "Already have an account?" : "New to Receipt IQ?"}{" "}
            <Link to={register ? "/login" : "/register"}>
              {register ? "Log in" : "Create an account"}{" "}
              <ChevronRight size={13} />
            </Link>
          </p>
          <div className="auth-security">
            <ShieldCheck size={14} /> Secure sign-in. Private receipt storage.
          </div>
        </motion.section>
      </main>
    </div>
  );
}

function Shell({ children }: { children: ReactNode }) {
  const { user, setUser } = useAuth();
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const nav = useNavigate();
  if (!user) return <Navigate to="/login" replace />;
  const links = [
    { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
    { to: "/scan", label: "Scan receipt", icon: ScanLine },
    { to: "/receipts", label: "Receipt library", icon: ReceiptText },
    { to: "/insights", label: "Insights", icon: ChartNoAxesCombined },
    { to: "/settings", label: "Settings", icon: Settings2 },
  ];
  return (
    <div className="app-scene">
      <Atmosphere />
      <header className="app-header">
        <Brand />
        <nav className={open ? "app-nav open" : "app-nav"}>
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)}>
              <l.icon size={16} />
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="account-menu">
          <span className="avatar">{user.name[0].toUpperCase()}</span>
          <button
            aria-label="Log out"
            title="Log out"
            onClick={async () => {
              try {
                await api("/auth/logout", { method: "POST" });
                setUser(null);
                nav("/");
              } catch (e) {
                setError((e as Error).message);
              }
            }}
          >
            <LogOut size={17} />
          </button>
          <button
            className="mobile-menu"
            aria-label="Toggle navigation"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </header>
      <main className="app-main">
        <ErrorBox message={error} />
        {children}
      </main>
      <footer className="app-footer">
        <span>
          RECEIPT IQ <span className="muted">/ A little more clarity.</span>
        </span>
        <span>
          <span className="live-dot" /> PRIVATE WORKSPACE
        </span>
      </footer>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const location = useLocation();
  useEffect(() => {
    api<User>("/auth/me")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setReady(true));
  }, []);
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);
  if (!ready)
    return (
      <div className="boot">
        <Loading />
      </div>
    );
  return (
    <Auth.Provider value={{ user, setUser }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
        >
          <Suspense fallback={<Loading />}>
            <Routes location={location}>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<AuthPage />} />
              <Route path="/register" element={<AuthPage register />} />
              <Route
                path="/dashboard"
                element={
                  <Shell>
                    <Dashboard />
                  </Shell>
                }
              />
              <Route
                path="/scan"
                element={
                  <Shell>
                    <Scan />
                  </Shell>
                }
              />
              <Route
                path="/receipts"
                element={
                  <Shell>
                    <Library />
                  </Shell>
                }
              />
              <Route
                path="/receipts/:id"
                element={
                  <Shell>
                    <ReceiptPage />
                  </Shell>
                }
              />
              <Route
                path="/insights"
                element={
                  <Shell>
                    <Insights />
                  </Shell>
                }
              />
              <Route
                path="/settings"
                element={
                  <Shell>
                    <Settings />
                  </Shell>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </motion.div>
      </AnimatePresence>
    </Auth.Provider>
  );
}
