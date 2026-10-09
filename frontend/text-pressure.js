/**
 * text-pressure.js
 * =================
 * Proximity-sensitive typography effect for the StayWise hero title.
 *
 * Each character in "STAY" / "WISE" is wrapped in a <span class="tp-char">.
 * On every animation frame the Euclidean distance from the mouse to each
 * character's bounding-box centre is computed.  Characters within
 * MAX_DISTANCE get a boosted wght (weight), wdth (width), and a slight ital
 * (italic) mapped from the distance — closer = heavier, wider, more slanted.
 *
 * Variable font: Barlow Condensed via Google Fonts already in the page head.
 * Axes used:  wght 100–900  (weight)
 *             wdth 75–125   (width — not all cuts expose this, so we also
 *                            scale font-size slightly as a fallback)
 *
 * The orange accent colour (#e8732b) is blended in at full proximity,
 * fading back to white as distance grows, so each character briefly flares
 * orange when hovered tightly — consistent with the brand palette.
 */
(function () {
  // ── Config ────────────────────────────────────────────────────────────
  const MAX_DISTANCE  = 160;   // px influence radius
  const WEIGHT_MIN    = 100;
  const WEIGHT_MAX    = 900;
  const SCALE_MIN     = 1.0;
  const SCALE_MAX     = 1.22;  // slight size boost at full proximity
  const ORANGE        = [232, 115, 43];
  const WHITE         = [255, 255, 255];

  // ── Build spans ────────────────────────────────────────────────────────
  const lines = [
    document.getElementById('tp-line-1'),
    document.getElementById('tp-line-2'),
  ];

  lines.forEach(line => {
    if (!line) return;
    const text = line.dataset.text || '';
    line.innerHTML = '';          // clear placeholder
    line.style.whiteSpace = 'nowrap';

    [...text].forEach(ch => {
      const span = document.createElement('span');
      span.className = 'tp-char';
      span.textContent = ch;
      // Start at base weight, no variation
      span.style.fontVariationSettings = `'wght' ${WEIGHT_MIN}`;
      span.style.display = 'inline-block';
      span.style.transform = 'scaleX(1)';
      line.appendChild(span);
    });
  });

  // ── Gather all char spans ──────────────────────────────────────────────
  const allChars = Array.from(
    document.querySelectorAll('#hero-title-pressure .tp-char')
  );

  // ── Mouse state ────────────────────────────────────────────────────────
  let mouseX = -9999;
  let mouseY = -9999;
  let rafId  = null;

  window.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  // Reset on mouse leave
  window.addEventListener('mouseleave', () => {
    mouseX = -9999;
    mouseY = -9999;
  });

  // ── Math helpers ──────────────────────────────────────────────────────
  // Linear interpolate
  const lerp = (a, b, t) => a + (b - a) * t;

  // Smooth ease-in curve: closer to cursor = higher value
  // t = 0 (at cursor) → 1.0,  t = 1 (at max dist) → 0.0
  const ease = t => 1 - Math.pow(t, 1.6);

  // Blend two RGB triples
  const blendRGB = (a, b, t) => a.map((v, i) => Math.round(lerp(v, b[i], t)));

  // ── Per-frame update ───────────────────────────────────────────────────
  function tick() {
    allChars.forEach(span => {
      const rect = span.getBoundingClientRect();
      const cx   = rect.left + rect.width  / 2;
      const cy   = rect.top  + rect.height / 2;

      const dist  = Math.hypot(mouseX - cx, mouseY - cy);
      const ratio = Math.max(0, Math.min(1, dist / MAX_DISTANCE));
      const t     = ease(ratio);   // 1 = at cursor, 0 = at max distance

      // Weight: 100 → 900
      const wght  = Math.round(lerp(WEIGHT_MIN, WEIGHT_MAX, t));

      // Scale: 1.0 → 1.22 on the X axis (fake wdth effect)
      const scaleX = lerp(SCALE_MIN, SCALE_MAX, t);

      // Colour: white → orange
      const [r, g, b] = blendRGB(WHITE, ORANGE, t);

      span.style.fontVariationSettings = `'wght' ${wght}`;
      span.style.transform   = `scaleX(${scaleX.toFixed(3)})`;
      span.style.color       = `rgb(${r},${g},${b})`;
    });

    rafId = requestAnimationFrame(tick);
  }

  // Start loop
  rafId = requestAnimationFrame(tick);

  // ── Touch support (mobile fallback) ────────────────────────────────────
  window.addEventListener('touchmove', e => {
    const touch = e.touches[0];
    mouseX = touch.clientX;
    mouseY = touch.clientY;
  }, { passive: true });

  window.addEventListener('touchend', () => {
    mouseX = -9999;
    mouseY = -9999;
  });
})();
