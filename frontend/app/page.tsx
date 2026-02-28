"use client";

import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ─── Types ────────────────────────────────────────────────────────────────────
interface FormState {
  room_type: number;
  neighbourhood_cleansed: number;
  accommodates: number;
  bedrooms: number;
  bathrooms: number;
  number_of_reviews: number;
  review_scores_rating: number;
  availability_365: number;
  minimum_nights: number;
}

// ─── Constants ────────────────────────────────────────────────────────────────
const ROOM_TYPES = [
  { label: "Entire home / apt", value: 0 },
  { label: "Hotel room",        value: 1 },
  { label: "Private room",      value: 2 },
  { label: "Shared room",       value: 3 },
];

// Displayed in arrondissement order (1er → 20e) for UX.
// Each `value` is the sklearn LabelEncoder code (alphabetical order) — sent to the API.
const NEIGHBOURHOODS = [
  { label: "Louvre (1er)",             value: 7,  avg: 125 },
  { label: "Bourse (2e)",              value: 1,  avg: 115 },
  { label: "Temple (3e)",              value: 17, avg: 96  },
  { label: "Hôtel-de-Ville (4e)",      value: 6,  avg: 108 },
  { label: "Panthéon (5e)",            value: 13, avg: 112 },
  { label: "Luxembourg (6e)",          value: 8,  avg: 130 },
  { label: "Palais-Bourbon (7e)",      value: 12, avg: 145 },
  { label: "Élysée (8e)",              value: 19, avg: 148 },
  { label: "Opéra (9e)",               value: 11, avg: 98  },
  { label: "Entrepôt (10e)",           value: 4,  avg: 88  },
  { label: "Popincourt (11e)",         value: 15, avg: 86  },
  { label: "Reuilly (12e)",            value: 16, avg: 76  },
  { label: "Gobelins (13e)",           value: 5,  avg: 72  },
  { label: "Observatoire (14e)",       value: 10, avg: 85  },
  { label: "Vaugirard (15e)",          value: 18, avg: 78  },
  { label: "Passy (16e)",              value: 14, avg: 135 },
  { label: "Batignolles-Monceau (17e)", value: 0, avg: 92  },
  { label: "Buttes-Montmartre (18e)", value: 3,  avg: 82  },
  { label: "Buttes-Chaumont (19e)",   value: 2,  avg: 78  },
  { label: "Ménilmontant (20e)",      value: 9,  avg: 79  },
];

const DEFAULT_FORM: FormState = {
  room_type: 0,
  neighbourhood_cleansed: 7, // Louvre (1er)
  accommodates: 2,
  bedrooms: 1,
  bathrooms: 1,
  number_of_reviews: 20,
  review_scores_rating: 4.5,
  availability_365: 120,
  minimum_nights: 2,
};

// ─── Sub-components ───────────────────────────────────────────────────────────
function Section({
  title,
  children,
  delay = 0,
}: {
  title: string;
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="glass-card rounded-2xl p-5"
    >
      <h2 className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/35 mb-4">
        {title}
      </h2>
      {children}
    </motion.div>
  );
}

function SliderField({
  label,
  value,
  min,
  max,
  step = 1,
  onChange,
  display,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (v: number) => void;
  display?: string;
}) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm text-white/55">{label}</span>
        <span className="text-sm font-semibold text-violet-300 tabular-nums">
          {display ?? value}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{
          background: `linear-gradient(to right, #7c3aed ${pct}%, rgba(255,255,255,0.12) ${pct}%)`,
        }}
      />
    </div>
  );
}

function NumberField({
  label,
  value,
  min = 0,
  onChange,
}: {
  label: string;
  value: number;
  min?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-white/55">{label}</span>
      <input
        type="number"
        min={min}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="input-glass"
      />
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function Home() {
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [price, setPrice] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [barTooltip, setBarTooltip] = useState<{ x: number; price: number } | null>(null);
  const barRef = useRef<HTMLDivElement>(null);

  const BAR_MAX = 500;

  const set =
    (key: keyof FormState) =>
    (v: number): void =>
      setForm((prev) => ({ ...prev, [key]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "https://estimair-backend.onrender.com";
      const res = await fetch(`${apiUrl}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      const data = await res.json();
      setPrice(data.predicted_price);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const neighbourhood = NEIGHBOURHOODS.find(
    (n) => n.value === form.neighbourhood_cleansed
  );
  const avgPrice = neighbourhood?.avg ?? 100;
  const delta = price !== null ? price - avgPrice : 0;
  const deltaSign = delta >= 0 ? "+" : "";
  const pricePct = price !== null ? Math.min((price / BAR_MAX) * 100, 100) : 0;
  const lowPct   = price !== null ? Math.max(((price - 69) / BAR_MAX) * 100, 0) : 0;
  const highPct  = price !== null ? Math.min(((price + 69) / BAR_MAX) * 100, 100) : 0;

  const handleBarMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!barRef.current) return;
    const rect = barRef.current.getBoundingClientRect();
    const pct = Math.max(0, Math.min((e.clientX - rect.left) / rect.width, 1));
    setBarTooltip({ x: pct * 100, price: Math.round(pct * BAR_MAX) });
  };

  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      {/* ── Ambient glow blobs ──────────────────────────────────────────────── */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-[-8%] left-[28%] w-[620px] h-[620px] rounded-full bg-violet-700/10 blur-[130px]" />
        <div className="absolute bottom-[5%] right-[15%] w-[420px] h-[420px] rounded-full bg-purple-800/8 blur-[110px]" />
        <div className="absolute top-[60%] left-[5%] w-[300px] h-[300px] rounded-full bg-indigo-700/6 blur-[100px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-2xl px-4 py-14 pb-20">
        {/* ── Header ───────────────────────────────────────────────────────── */}
        <motion.header
          initial={{ opacity: 0, y: -28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-center mb-11"
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 mb-7 rounded-full border border-violet-500/30 bg-violet-500/8 text-xs text-violet-300 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            Powered by XGBoost + MLflow
          </div>

          {/* Title */}
          <h1 className="text-5xl font-extrabold tracking-tight mb-3">
            <span
              style={{
                background:
                  "linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.85) 50%, rgba(255,255,255,0.4) 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              EstimAir
            </span>
          </h1>

          <p className="text-white/45 text-lg">
            AI-powered Airbnb price estimator for Paris
          </p>
        </motion.header>

        {/* ── Main content (form ↔ result) ─────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {price === null ? (
            /* ── FORM ──────────────────────────────────────────────────────── */
            <motion.form
              key="form"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.3 }}
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              {/* Property type */}
              <Section title="Property type" delay={0.05}>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-white/40 mb-2">
                      Room type
                    </label>
                    <select
                      value={form.room_type}
                      onChange={(e) => set("room_type")(Number(e.target.value))}
                      className="select-glass"
                    >
                      {ROOM_TYPES.map((r) => (
                        <option key={r.value} value={r.value}>
                          {r.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-white/40 mb-2">
                      Neighbourhood
                    </label>
                    <select
                      value={form.neighbourhood_cleansed}
                      onChange={(e) =>
                        set("neighbourhood_cleansed")(Number(e.target.value))
                      }
                      className="select-glass"
                    >
                      {NEIGHBOURHOODS.map((n) => (
                        <option key={n.value} value={n.value}>
                          {n.label}
                        </option>
                      ))}
                    </select>
                    <p className="text-[10px] text-white/25 mt-1.5 pl-0.5">
                      Paris intra-muros · 20 arrondissements
                    </p>
                  </div>
                </div>
              </Section>

              {/* Capacity */}
              <Section title="Capacity" delay={0.1}>
                <div className="space-y-5">
                  <SliderField
                    label="Accommodates"
                    value={form.accommodates}
                    min={1}
                    max={16}
                    onChange={set("accommodates")}
                    display={`${form.accommodates} guest${form.accommodates > 1 ? "s" : ""}`}
                  />
                  <SliderField
                    label="Bedrooms"
                    value={form.bedrooms}
                    min={0}
                    max={10}
                    onChange={set("bedrooms")}
                    display={`${form.bedrooms} bedroom${form.bedrooms !== 1 ? "s" : ""}`}
                  />
                  <SliderField
                    label="Bathrooms"
                    value={form.bathrooms}
                    min={0}
                    max={5}
                    step={0.5}
                    onChange={set("bathrooms")}
                    display={`${form.bathrooms} bathroom${form.bathrooms !== 1 ? "s" : ""}`}
                  />
                </div>
              </Section>

              {/* Availability */}
              <Section title="Availability" delay={0.15}>
                <div className="space-y-5">
                  <SliderField
                    label="Available days / year"
                    value={form.availability_365}
                    min={0}
                    max={365}
                    onChange={set("availability_365")}
                    display={`${form.availability_365} days`}
                  />
                  <NumberField
                    label="Minimum nights"
                    value={form.minimum_nights}
                    min={1}
                    onChange={set("minimum_nights")}
                  />
                </div>
              </Section>

              {/* Reviews */}
              <Section title="Reviews" delay={0.2}>
                <div className="space-y-5">
                  <NumberField
                    label="Number of reviews"
                    value={form.number_of_reviews}
                    min={0}
                    onChange={set("number_of_reviews")}
                  />
                  <SliderField
                    label="Review score"
                    value={form.review_scores_rating}
                    min={0}
                    max={5}
                    step={0.1}
                    onChange={set("review_scores_rating")}
                    display={`${form.review_scores_rating.toFixed(1)} / 5`}
                  />
                </div>
              </Section>

              {/* Error */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit */}
              <motion.button
                type="submit"
                disabled={loading}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                whileHover={{ scale: loading ? 1 : 1.01 }}
                whileTap={{ scale: loading ? 1 : 0.99 }}
                className="w-full py-4 rounded-2xl font-semibold text-white text-base cursor-pointer disabled:cursor-not-allowed transition-all"
                style={{
                  background: loading
                    ? "rgba(124, 58, 237, 0.5)"
                    : "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
                  boxShadow: loading
                    ? "none"
                    : "0 0 30px rgba(124, 58, 237, 0.35)",
                }}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-3">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Estimating price…
                  </span>
                ) : (
                  "Predict Price"
                )}
              </motion.button>
            </motion.form>
          ) : (
            /* ── RESULT ─────────────────────────────────────────────────────── */
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.94, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ type: "spring", stiffness: 240, damping: 24 }}
              className="glass-card rounded-3xl p-8 space-y-7"
            >
              {/* Price headline */}
              <div className="text-center">
                <p className="text-white/35 text-sm mb-2 uppercase tracking-widest text-[11px]">
                  Estimated nightly price
                </p>
                <motion.div
                  initial={{ scale: 0.7, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.1 }}
                  className="text-[80px] font-black leading-none tabular-nums"
                  style={{
                    background:
                      "linear-gradient(135deg, #a78bfa 0%, #7c3aed 60%, #c084fc 100%)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    backgroundClip: "text",
                  }}
                >
                  €{Math.round(price)}
                </motion.div>
                <p className="text-white/35 mt-1">per night</p>
              </div>

              {/* Property summary chips */}
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  ROOM_TYPES.find((r) => r.value === form.room_type)?.label,
                  neighbourhood?.label,
                  `${form.accommodates} guests`,
                  `${form.bedrooms}bd · ${form.bathrooms}ba`,
                ].map((chip) => (
                  <span
                    key={chip}
                    className="px-3 py-1 rounded-full text-xs text-white/50 border border-white/10 bg-white/4"
                  >
                    {chip}
                  </span>
                ))}
              </div>

              {/* vs neighbourhood average */}
              <div className="glass-card-inner rounded-2xl p-4 text-center">
                <p className="text-[11px] text-white/35 mb-1">
                  vs. {neighbourhood?.label} avg (≈€{avgPrice}/night)
                </p>
                <p
                  className={`text-xl font-bold ${
                    delta >= 0 ? "text-amber-400" : "text-emerald-400"
                  }`}
                >
                  {deltaSign}€{Math.abs(Math.round(delta))} (
                  {deltaSign}
                  {Math.abs((delta / avgPrice) * 100).toFixed(0)}%)
                </p>
              </div>

              {/* Confidence range bar with interactive tooltip */}
              <div>
                <p className="text-[11px] text-white/35 mb-3 text-center">
                  Price range · model MAE ±€69
                </p>

                {/* Wrapper: handles mouse events, no overflow-hidden */}
                <div
                  ref={barRef}
                  className="relative cursor-crosshair select-none"
                  style={{ paddingTop: "28px" }} // space for tooltip above bar
                  onMouseMove={handleBarMouseMove}
                  onMouseLeave={() => setBarTooltip(null)}
                >
                  {/* Tooltip bubble */}
                  {barTooltip && (
                    <div
                      className="absolute top-0 -translate-x-1/2 pointer-events-none"
                      style={{ left: `${barTooltip.x}%` }}
                    >
                      <div className="px-2 py-1 rounded-lg bg-violet-600 text-white text-[11px] font-semibold whitespace-nowrap shadow-lg shadow-violet-900/40">
                        €{barTooltip.price}
                      </div>
                      {/* Arrow */}
                      <div className="flex justify-center">
                        <div className="border-4 border-transparent border-t-violet-600" />
                      </div>
                    </div>
                  )}

                  {/* Track */}
                  <div className="relative h-2 bg-white/8 rounded-full overflow-hidden">
                    {/* Confidence band */}
                    <div
                      className="absolute top-0 h-full rounded-full bg-violet-500/30"
                      style={{ left: `${lowPct}%`, width: `${highPct - lowPct}%` }}
                    />
                  </div>

                  {/* Point estimate dot — outside overflow-hidden so it's fully visible */}
                  <motion.div
                    initial={{ left: "0%" }}
                    animate={{ left: `calc(${pricePct}% - 6px)` }}
                    transition={{ type: "spring", stiffness: 200, damping: 22, delay: 0.2 }}
                    className="absolute w-3 h-3 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.6)]"
                    style={{ top: "calc(28px - 2px)" }} // vertically centered on bar
                  />
                </div>

                <div className="flex justify-between text-[10px] text-white/25 mt-1.5 px-0.5">
                  <span>€0</span>
                  <span>€{BAR_MAX}+</span>
                </div>
              </div>

              {/* Try another */}
              <div className="flex justify-center pt-1">
                <button
                  onClick={() => {
                    setPrice(null);
                    setError(null);
                  }}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl border border-white/10 hover:border-violet-500/40 hover:bg-violet-500/8 text-white/50 hover:text-white/90 text-sm transition-all duration-200 cursor-pointer"
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="opacity-60">
                    <path
                      d="M1 7a6 6 0 1 0 6-6M1 1v6h6"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  Try another
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Footer ───────────────────────────────────────────────────────── */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="text-center mt-14 space-y-1.5"
        >
          <p className="text-white/20 text-xs">
            Built with FastAPI · XGBoost · MLflow · DVC
          </p>
          <a
            href="https://github.com/BradleyJason/airbnb-price-predictor"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block text-white/25 hover:text-white/55 text-xs transition-colors duration-200"
          >
            github.com/BradleyJason/airbnb-price-predictor
          </a>
        </motion.footer>
      </div>
    </main>
  );
}
