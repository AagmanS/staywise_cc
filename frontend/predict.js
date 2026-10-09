/* ============================================================
   STAYWISE — PREDICT.JS
   - Calls Flask API at :5000/predict for real ML predictions
   - Renders SHAP explainability section
   - Generates downloadable PDF risk report via jsPDF
   ============================================================ */

const API_URL = "http://localhost:5000/predict";

// Module-level store: populated after each successful prediction
// so the PDF generator always has fresh data.
let _lastResponse  = null;   // raw API JSON response
let _lastFormData  = null;   // raw form field values
let _customerName  = "";     // customer name from the name field

// ── Gauge animation ────────────────────────────────────────────────────────
function animateGauge(prob) {
  const fill   = document.getElementById("gauge-fill");
  const pctEl  = document.getElementById("gauge-pct");
  const needle = document.getElementById("gauge-needle");

  if (fill)   fill.style.strokeDashoffset = String(283 * (1 - prob));

  if (needle) {
    const angle = -90 + prob * 180;
    needle.style.transition = "transform 1.4s cubic-bezier(0.4,0,0.2,1)";
    needle.setAttribute("transform", `rotate(${angle}, 110, 110)`);
  }

  if (pctEl) {
    const target = Math.round(prob * 100);
    let t0 = null;
    const tick = (ts) => {
      if (!t0) t0 = ts;
      const p = Math.min((ts - t0) / 1300, 1);
      const e = 1 - Math.pow(1 - p, 3);
      pctEl.textContent = Math.round(target * e) + "%";
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    pctEl.style.color =
      prob >= 0.60 ? "#ef4444" :
      prob >= 0.20 ? "var(--orange)" :
                     "#4ade80";
  }
}

// ── Verdict box ────────────────────────────────────────────────────────────
function renderVerdict(prob, riskLevel) {
  const box   = document.getElementById("verdict-box");
  const emoji = document.getElementById("verdict-emoji");
  const label = document.getElementById("verdict-label");
  const sub   = document.getElementById("verdict-sub");

  const map = {
    HIGH:   { cls: "v-high", em: "🔴", lbl: "HIGH CHURN RISK",   s: "Immediate intervention is recommended" },
    MEDIUM: { cls: "v-med",  em: "🟡", lbl: "MEDIUM CHURN RISK", s: "Proactive engagement within 2 weeks" },
    LOW:    { cls: "v-low",  em: "🟢", lbl: "LOW CHURN RISK",    s: "Customer is stable — standard management applies" },
  };
  const v = map[riskLevel] || map.LOW;
  if (box)   box.className    = `verdict-box ${v.cls}`;
  if (emoji) emoji.textContent = v.em;
  if (label) label.textContent = v.lbl;
  if (sub)   sub.textContent   = v.s;
}

// ── XAI bar renderer ───────────────────────────────────────────────────────
function renderXaiBars(container, factors, kind) {
  if (!container) return;
  if (!factors || factors.length === 0) {
    container.innerHTML = `<p class="xai-empty">No significant ${kind === "risk" ? "risk" : "protective"} factors detected.</p>`;
    return;
  }
  container.innerHTML = factors.map((f, i) => `
    <div class="xai-row" style="--delay:${i * 80}ms">
      <div class="xai-row-meta">
        <span class="xai-feature-label">${f.label}</span>
        <span class="xai-value-label">${f.value_label}</span>
      </div>
      <div class="xai-bar-track">
        <div class="xai-bar-fill ${kind === "risk" ? "xai-bar-fill-risk" : "xai-bar-fill-prot"}"
             style="--bar-pct:${f.bar_pct}%" role="progressbar"
             aria-valuenow="${f.bar_pct}" aria-valuemin="0" aria-valuemax="100"></div>
      </div>
      <div class="xai-row-right">
        <span class="xai-impact-badge ${kind === "risk" ? "xai-badge-risk" : "xai-badge-prot"}">${f.impact}</span>
        <span class="xai-arrow ${kind === "risk" ? "xai-arrow-risk" : "xai-arrow-prot"}">${kind === "risk" ? "↑" : "↓"}</span>
      </div>
    </div>`).join("");

  requestAnimationFrame(() => {
    container.querySelectorAll(".xai-bar-fill").forEach(el => el.classList.add("xai-bar-animate"));
  });
}

// ── Render XAI section ─────────────────────────────────────────────────────
function renderXai(riskFactors, protectiveFactors) {
  const section   = document.getElementById("xai-section");
  const riskGroup = document.getElementById("xai-risk-group");
  const protGroup = document.getElementById("xai-prot-group");
  if (!section) return;

  section.classList.add("xai-visible");

  if (riskFactors?.length > 0) {
    riskGroup.style.display = "block";
    renderXaiBars(document.getElementById("xai-risk-bars"), riskFactors, "risk");
  } else {
    riskGroup.style.display = "none";
  }

  if (protectiveFactors?.length > 0) {
    protGroup.style.display = "block";
    renderXaiBars(document.getElementById("xai-prot-bars"), protectiveFactors, "prot");
  } else {
    protGroup.style.display = "none";
  }
}

// ── Recommendations ────────────────────────────────────────────────────────
function renderRecommendations(recs) {
  const recList = document.getElementById("rec-list");
  if (!recList || !recs) return;
  const icons = ["🎯", "📞", "🛡️", "💳", "📩", "🎁", "📊", "✅", "🌟", "📈"];
  recList.innerHTML = recs.map((text, i) => `
    <div class="rec-item">
      <div class="rec-icon">${icons[i % icons.length]}</div>
      <span>${text}</span>
    </div>`).join("");
}

// ── Show full result ────────────────────────────────────────────────────────
function showResult(apiResponse, formData) {
  const loadEl   = document.getElementById("r-loading");
  const outputEl = document.getElementById("r-output");

  if (loadEl)   loadEl.style.display = "none";
  if (outputEl) {
    outputEl.style.display    = "flex";
    outputEl.style.opacity    = "0";
    outputEl.style.transition = "opacity 0.4s ease";
    requestAnimationFrame(() => { outputEl.style.opacity = "1"; });
  }

  // Store for PDF
  _lastResponse = apiResponse;
  _lastFormData = formData;
  _customerName = (formData.customer_name || "").trim();

  setTimeout(() => animateGauge(apiResponse.probability), 80);
  renderVerdict(apiResponse.probability, apiResponse.risk_level);
  renderXai(apiResponse.risk_factors, apiResponse.protective_factors);
  renderRecommendations(apiResponse.recommendations);

  // Show PDF button
  const pdfBtn = document.getElementById("btn-pdf");
  if (pdfBtn) pdfBtn.style.display = "inline-flex";

  if (window.innerWidth < 1100) {
    outputEl?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// ── Reset to idle ──────────────────────────────────────────────────────────
function resetToIdle() {
  document.getElementById("r-idle"   )?.style.setProperty("display", "flex");
  document.getElementById("r-loading")?.style.setProperty("display", "none");
  document.getElementById("r-output" )?.style.setProperty("display", "none");
  document.getElementById("xai-section")?.classList.remove("xai-visible");
  const pdfBtn = document.getElementById("btn-pdf");
  if (pdfBtn) pdfBtn.style.display = "none";
  _lastResponse = null;
  _lastFormData = null;
  _customerName = "";
}

// ── Form helpers ───────────────────────────────────────────────────────────
function getFormData() {
  const fd   = new FormData(document.getElementById("predict-form"));
  const data = {};
  for (const [k, v] of fd.entries()) data[k] = v;
  return data;
}

function validateForm(data) {
  const required = [
    "gender", "senior_citizen", "partner", "dependents",
    "tenure_months", "internet_service", "phone_service",
    "contract", "payment_method", "monthly_charges", "total_charges",
  ];
  let valid = true;
  required.forEach(f => {
    const el = document.querySelector(`[name="${f}"]`);
    if (!data[f] || !String(data[f]).trim()) {
      el?.classList.add("error"); valid = false;
    } else {
      el?.classList.remove("error");
    }
  });
  return valid;
}

// ── Form submit → API ──────────────────────────────────────────────────────
document.getElementById("predict-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = getFormData();
  if (!validateForm(data)) {
    document.querySelectorAll(".error").forEach(el => {
      el.style.animation = "shake 0.35s ease";
      setTimeout(() => (el.style.animation = ""), 350);
    });
    return;
  }

  document.getElementById("r-idle"   )?.style.setProperty("display", "none");
  document.getElementById("r-loading")?.style.setProperty("display", "flex");
  document.getElementById("r-output" )?.style.setProperty("display", "none");

  try {
    const res = await fetch(API_URL, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Server error ${res.status}`);
    }
    showResult(await res.json(), data);
  } catch (err) {
    document.getElementById("r-loading")?.style.setProperty("display", "none");
    document.getElementById("r-idle"   )?.style.setProperty("display", "flex");
    const banner = document.getElementById("api-error-banner");
    if (banner) {
      banner.textContent  = `⚠ ${err.message}`;
      banner.style.display = "block";
      setTimeout(() => (banner.style.display = "none"), 6000);
    }
    console.error("[StayWise] API error:", err);
  }
});

// ── Reset & New buttons ────────────────────────────────────────────────────
document.getElementById("reset-btn")?.addEventListener("click", () => {
  document.getElementById("predict-form")?.reset();
  document.querySelectorAll(".error").forEach(el => el.classList.remove("error"));
  resetToIdle();
});
document.getElementById("r-new-btn")?.addEventListener("click", () => {
  document.getElementById("predict-form")?.reset();
  resetToIdle();
});

// ── PDF Report Generator ───────────────────────────────────────────────────
/**
 * Builds and downloads a professional navy-and-orange PDF risk report
 * using jsPDF (loaded from CDN).  No extra install required.
 *
 * Layout:
 *   • Header bar  – StayWise logo + report title + date
 *   • Summary box – probability, risk level, threshold
 *   • Customer details table
 *   • Risk factors / Protective factors (SHAP)
 *   • Recommendations
 *   • Revenue-at-risk estimate
 *   • Footer
 */
function generatePDF() {
  if (!_lastResponse) return;

  const { jsPDF } = window.jspdf;
  if (!jsPDF) { alert("PDF library not loaded yet — please wait a moment and try again."); return; }

  const doc  = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
  const W    = 210;   // page width mm
  const ML   = 14;    // margin left
  const MR   = 14;    // margin right
  const TW   = W - ML - MR;  // text width
  const r    = _lastResponse;
  const fd   = _lastFormData || {};
  const name = _customerName || "Unknown Customer";
  const now  = new Date();
  const dateStr = now.toLocaleDateString("en-GB", { day:"2-digit", month:"short", year:"numeric" });
  const timeStr = now.toLocaleTimeString("en-GB", { hour:"2-digit", minute:"2-digit" });

  // ── Colour palette ─────────────────────────────────────────────────
  const NAVY       = [27,  58,  92];
  const NAVY_DEEP  = [18,  41,  68];
  const ORANGE     = [232, 115, 43];
  const WHITE      = [255, 255, 255];
  const GREY_LIGHT = [220, 228, 236];
  const GREY_TEXT  = [140, 160, 180];
  const RED        = [239,  68,  68];
  const GREEN      = [ 74, 222, 128];

  const riskColor =
    r.risk_level === "HIGH"   ? RED :
    r.risk_level === "MEDIUM" ? ORANGE :
                                GREEN;

  let y = 0;  // current Y cursor

  // ── Helper functions ───────────────────────────────────────────────
  const setFont = (style = "normal", size = 10) => {
    doc.setFont("helvetica", style);
    doc.setFontSize(size);
  };
  const setColor = (rgb) => doc.setTextColor(...rgb);
  const fillRect = (x, fy, w, h, rgb) => {
    doc.setFillColor(...rgb);
    doc.rect(x, fy, w, h, "F");
  };
  const hline = (fy, rgb = GREY_LIGHT, lw = 0.3) => {
    doc.setDrawColor(...rgb);
    doc.setLineWidth(lw);
    doc.line(ML, fy, W - MR, fy);
  };
  // Wrapping text with line-height
  const writeWrapped = (text, x, fy, maxW, lineH = 5) => {
    const lines = doc.splitTextToSize(String(text), maxW);
    lines.forEach((ln, i) => doc.text(ln, x, fy + i * lineH));
    return fy + lines.length * lineH;
  };
  // Small labelled pill
  const pill = (label, x, fy, rgb) => {
    const pad = 2, h = 5;
    setFont("bold", 7);
    const tw = doc.getTextWidth(label) + pad * 2;
    doc.setFillColor(...rgb);
    doc.roundedRect(x, fy - 3.5, tw, h, 1, 1, "F");
    doc.setTextColor(...WHITE);
    doc.text(label, x + pad, fy);
    return x + tw + 2;
  };
  // Section title
  const sectionTitle = (title, fy) => {
    fillRect(ML, fy, 3, 5, ORANGE);
    setFont("bold", 9);
    setColor(NAVY);
    doc.text(title, ML + 5, fy + 4);
    return fy + 9;
  };

  // ══ 1. HEADER BAR ══════════════════════════════════════════════════
  fillRect(0, 0, W, 22, NAVY_DEEP);

  // Brand circle
  doc.setFillColor(...ORANGE);
  doc.circle(ML + 5, 11, 4, "F");
  setFont("bold", 8);
  setColor(WHITE);
  doc.text("S", ML + 3.5, 13);

  // Brand name
  setFont("bold", 13);
  setColor(WHITE);
  doc.text("STAYWISE", ML + 12, 13);

  // Report subtitle
  setFont("normal", 8);
  setColor(GREY_TEXT);
  doc.text("Customer Churn Risk Report", ML + 12, 18);

  // Date top-right
  setFont("normal", 8);
  setColor(GREY_TEXT);
  doc.text(`${dateStr}  ${timeStr}`, W - MR, 11, { align: "right" });
  setFont("normal", 7);
  doc.text("CONFIDENTIAL", W - MR, 17, { align: "right" });

  y = 28;

  // ══ 2. CUSTOMER NAME + ID ROW ══════════════════════════════════════
  fillRect(ML, y, TW, 14, [235, 241, 247]);
  setFont("bold", 12);
  setColor(NAVY_DEEP);
  doc.text(name, ML + 4, y + 6);
  setFont("normal", 8);
  setColor(GREY_TEXT);
  doc.text("CUSTOMER", ML + 4, y + 11);

  // Tenure badge right side
  const tenure = fd.tenure_months ? `Tenure: ${fd.tenure_months} mo` : "";
  if (tenure) {
    setFont("normal", 8);
    setColor(NAVY);
    doc.text(tenure, W - MR - 4, y + 6, { align: "right" });
  }
  const contract = fd.contract || "";
  if (contract) {
    setFont("normal", 7);
    setColor(GREY_TEXT);
    doc.text(contract, W - MR - 4, y + 11, { align: "right" });
  }
  y += 18;

  // ══ 3. PROBABILITY SUMMARY BOX ═════════════════════════════════════
  const boxH = 26;
  fillRect(ML, y, TW, boxH, NAVY);
  // Left: big probability number
  setFont("bold", 28);
  setColor(riskColor);
  doc.text(`${r.probability_pct}%`, ML + 6, y + 18);
  // Label under number
  setFont("bold", 7);
  setColor(GREY_TEXT);
  doc.text("CHURN PROBABILITY", ML + 6, y + 23);

  // Right: risk level + threshold
  const midX = ML + TW / 2 + 10;
  setFont("bold", 14);
  setColor(riskColor);
  doc.text(r.risk_level, midX, y + 13);
  setFont("bold", 7);
  setColor(GREY_TEXT);
  doc.text("RISK CLASSIFICATION", midX, y + 18);
  setFont("normal", 7);
  setColor(GREY_TEXT);
  doc.text(`Decision threshold: ${Math.round((r.threshold || 0.2) * 100)}%`, midX, y + 23);

  // Orange accent line at bottom of box
  fillRect(ML, y + boxH - 1.5, TW, 1.5, ORANGE);
  y += boxH + 8;

  // ══ 4. CUSTOMER DETAILS TABLE ═══════════════════════════════════════
  y = sectionTitle("CUSTOMER DETAILS", y);

  const details = [
    ["Gender",          fd.gender         || "—"],
    ["Senior Citizen",  fd.senior_citizen === "1" ? "Yes" : "No"],
    ["Partner",         fd.partner        || "—"],
    ["Dependents",      fd.dependents     || "—"],
    ["Internet Service",fd.internet_service || "—"],
    ["Phone Service",   fd.phone_service  || "—"],
    ["Multiple Lines",  fd.multiple_lines || "—"],
    ["Contract",        fd.contract       || "—"],
    ["Paperless Billing",fd.paperless_billing || "—"],
    ["Payment Method",  fd.payment_method || "—"],
    ["Monthly Charges", fd.monthly_charges ? `$${parseFloat(fd.monthly_charges).toFixed(2)}` : "—"],
    ["Total Charges",   fd.total_charges  ? `$${parseFloat(fd.total_charges).toFixed(2)}`  : "—"],
  ];

  const colW    = TW / 2 - 2;
  const rowH    = 6.5;
  let col       = 0;
  let rowStartY = y;

  details.forEach(([label, value], idx) => {
    const cx = col === 0 ? ML : ML + TW / 2 + 2;
    const cy = rowStartY + Math.floor(idx / 2) * rowH;

    // Alternating row tint
    if (Math.floor(idx / 2) % 2 === 0) {
      fillRect(cx, cy - 4, colW, rowH, [243, 247, 251]);
    }
    setFont("normal", 7);
    setColor(GREY_TEXT);
    doc.text(label.toUpperCase(), cx + 2, cy);
    setFont("bold", 8);
    setColor(NAVY_DEEP);
    doc.text(String(value), cx + colW - 2, cy, { align: "right" });

    col = col === 0 ? 1 : 0;
  });

  y = rowStartY + Math.ceil(details.length / 2) * rowH + 6;
  hline(y - 2);

  // ══ 5. SHAP RISK FACTORS ════════════════════════════════════════════
  if (r.risk_factors?.length > 0) {
    y = sectionTitle("WHY THIS CUSTOMER IS AT RISK", y);

    r.risk_factors.forEach((f, i) => {
      // Row bg
      if (i % 2 === 0) fillRect(ML, y - 3.5, TW, 7, [253, 245, 240]);

      setFont("bold", 8);
      setColor(NAVY_DEEP);
      doc.text(f.label, ML + 2, y);

      setFont("normal", 7);
      setColor(GREY_TEXT);
      doc.text(String(f.value_label), ML + 55, y);

      // Bar
      const barX = ML + 90, barW = 60, barH = 2.5, barY = y - 2;
      fillRect(barX, barY, barW, barH, [220, 228, 236]);
      fillRect(barX, barY, barW * (f.bar_pct / 100), barH, RED);

      // Impact label
      pill(f.impact.toUpperCase(), barX + barW + 3, y, RED);

      // Arrow
      setFont("bold", 8);
      setColor(RED);
      doc.text("↑", W - MR - 2, y, { align: "right" });

      y += 8;
    });
    y += 2;
    hline(y - 2);
  }

  // ══ 6. PROTECTIVE FACTORS ═══════════════════════════════════════════
  if (r.protective_factors?.length > 0) {
    y = sectionTitle("PROTECTIVE FACTORS", y);

    r.protective_factors.forEach((f, i) => {
      if (i % 2 === 0) fillRect(ML, y - 3.5, TW, 7, [240, 253, 244]);

      setFont("bold", 8);
      setColor(NAVY_DEEP);
      doc.text(f.label, ML + 2, y);

      setFont("normal", 7);
      setColor(GREY_TEXT);
      doc.text(String(f.value_label), ML + 55, y);

      const barX = ML + 90, barW = 60, barH = 2.5, barY = y - 2;
      fillRect(barX, barY, barW, barH, [220, 228, 236]);
      fillRect(barX, barY, barW * (f.bar_pct / 100), barH, GREEN);

      pill(f.impact.toUpperCase(), barX + barW + 3, y, [34, 130, 80]);

      setFont("bold", 8);
      setColor(GREEN);
      doc.text("↓", W - MR - 2, y, { align: "right" });

      y += 8;
    });
    y += 2;
    hline(y - 2);
  }

  // ══ 7. RECOMMENDATIONS ══════════════════════════════════════════════
  if (r.recommendations?.length > 0) {
    y = sectionTitle("RETENTION RECOMMENDATIONS", y);

    r.recommendations.forEach((rec, i) => {
      // Bullet dot
      doc.setFillColor(...ORANGE);
      doc.circle(ML + 2, y - 1, 1, "F");

      setFont("normal", 8);
      setColor(NAVY_DEEP);
      y = writeWrapped(rec, ML + 6, y, TW - 8, 5);
      y += 2;
    });
    hline(y);
    y += 4;
  }

  // ══ 8. REVENUE AT RISK ══════════════════════════════════════════════
  const monthly = parseFloat(fd.monthly_charges) || 0;
  if (monthly > 0) {
    // Estimate: monthly × 12 × probability
    const annualRisk = (monthly * 12 * r.probability).toFixed(2);
    fillRect(ML, y, TW, 14, [255, 247, 237]);
    doc.setDrawColor(...ORANGE);
    doc.setLineWidth(0.4);
    doc.rect(ML, y, TW, 14);
    setFont("bold", 9);
    setColor(NAVY_DEEP);
    doc.text("ESTIMATED ANNUAL REVENUE AT RISK", ML + 4, y + 6);
    setFont("bold", 12);
    setColor(ORANGE);
    doc.text(`$${parseFloat(annualRisk).toLocaleString("en-US", { minimumFractionDigits: 2 })}`, ML + 4, y + 12);
    setFont("normal", 7);
    setColor(GREY_TEXT);
    doc.text("Based on monthly charges × 12 months × churn probability", W - MR - 2, y + 10, { align: "right" });
    y += 20;
  }

  // ══ 9. SHAP FOOTNOTE ════════════════════════════════════════════════
  setFont("italic", 7);
  setColor(GREY_TEXT);
  doc.text(
    "Risk factors determined using SHAP (SHapley Additive exPlanations) on a Logistic Regression model trained on 7,043 telecom records.",
    ML, y, { maxWidth: TW }
  );
  y += 8;

  // ══ 10. FOOTER ══════════════════════════════════════════════════════
  fillRect(0, 285, W, 12, NAVY_DEEP);
  setFont("normal", 7);
  setColor(GREY_TEXT);
  doc.text("StayWise · AI-Powered Churn Prediction · Logistic Regression · ROC-AUC 94.2%", W / 2, 292, { align: "center" });
  setColor([...ORANGE]);
  doc.text("CONFIDENTIAL — FOR INTERNAL USE ONLY", W / 2, 296, { align: "center" });

  // ── Save ──────────────────────────────────────────────────────────────
  const safeName = name.replace(/[^a-z0-9]/gi, "_").toLowerCase() || "customer";
  doc.save(`staywise_risk_report_${safeName}_${now.getTime()}.pdf`);
}

// ── PDF button click ───────────────────────────────────────────────────────
document.getElementById("btn-pdf")?.addEventListener("click", () => {
  if (!_lastResponse) return;
  generatePDF();
});

// ── Sample data ────────────────────────────────────────────────────────────
const SAMPLE_HIGH = {
  customer_name: "Alex Turner",
  gender: "Male", senior_citizen: "0", partner: "No", dependents: "No",
  tenure_months: "3", phone_service: "Yes", multiple_lines: "No",
  internet_service: "Fiber optic", online_security: "No", online_backup: "No",
  device_protection: "No", tech_support: "No", streaming_tv: "Yes",
  streaming_movies: "Yes", contract: "Month-to-month", paperless_billing: "Yes",
  payment_method: "Electronic check", monthly_charges: "95.70", total_charges: "287.10",
};

const SAMPLE_LOW = {
  customer_name: "Sarah Chen",
  gender: "Female", senior_citizen: "0", partner: "Yes", dependents: "Yes",
  tenure_months: "60", phone_service: "Yes", multiple_lines: "Yes",
  internet_service: "DSL", online_security: "Yes", online_backup: "Yes",
  device_protection: "Yes", tech_support: "Yes", streaming_tv: "No",
  streaming_movies: "No", contract: "Two year", paperless_billing: "No",
  payment_method: "Bank transfer (automatic)", monthly_charges: "65.40", total_charges: "3924.00",
};

function fillSample(sample) {
  const form = document.getElementById("predict-form");
  if (!form) return;
  Object.entries(sample).forEach(([key, val]) => {
    const el = form.querySelector(`[name="${key}"]`);
    if (el) el.value = val;
  });
  setTimeout(() =>
    form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true })), 80);
}

document.getElementById("sample-high")  ?.addEventListener("click", () => fillSample(SAMPLE_HIGH));
document.getElementById("sample-low")   ?.addEventListener("click", () => fillSample(SAMPLE_LOW));
document.getElementById("fill-demo-btn")?.addEventListener("click", () => fillSample(SAMPLE_HIGH));

// ── Auto-calc total charges ────────────────────────────────────────────────
const monthlyEl = document.getElementById("monthly");
const tenureEl  = document.getElementById("tenure");
const totalEl   = document.getElementById("total");

function autoTotal() {
  const m = parseFloat(monthlyEl?.value) || 0;
  const t = parseFloat(tenureEl?.value)  || 0;
  if (m > 0 && t > 0 && totalEl && !totalEl.value) {
    totalEl.value = (m * t).toFixed(2);
    totalEl.style.borderColor = "var(--orange)";
    setTimeout(() => (totalEl.style.borderColor = ""), 1800);
  }
}
monthlyEl?.addEventListener("blur", autoTotal);
tenureEl ?.addEventListener("blur", autoTotal);

// ── Shake keyframe ─────────────────────────────────────────────────────────
const _style = document.createElement("style");
_style.textContent = `
  @keyframes shake {
    0%,100%{ transform:translateX(0) }
    20%    { transform:translateX(-5px) }
    40%    { transform:translateX(5px) }
    60%    { transform:translateX(-3px) }
    80%    { transform:translateX(3px) }
  }`;
document.head.appendChild(_style);

console.log(
  "%c StayWise Predictor ✓ ",
  "background:#e8732b;color:white;font-weight:900;padding:4px 10px;border-radius:4px;font-family:monospace"
);
