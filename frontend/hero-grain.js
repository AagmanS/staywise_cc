/**
 * hero-grain.js
 * =============
 * Draws 46 horizontal wood-grain contour lines on the hero canvas.
 * Every 9th line is rendered in ice blue (#B9E5F3 @ 34%) instead of white @ 7.5%.
 * Each line is a primary sine wave plus a slower harmonic, both advanced by time,
 * creating the gentle drifting grain effect from the Coldbrook spec — adapted to
 * StayWise's navy colour scheme.
 *
 * Also drives the radial vignette element opacity via a CSS var so the page can
 * deepen the frame on scroll if desired.
 */
(function () {
  const canvas  = document.getElementById('hero-grain');
  const vignette = document.getElementById('hero-vignette');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  // ── Config ──────────────────────────────────────────────────────────
  const TOTAL_LINES   = 46;
  const ICE_EVERY     = 9;          // every 9th line is ice blue
  const LINE_ALPHA    = 0.075;      // white lines opacity
  const ICE_ALPHA     = 0.34;       // ice-blue lines opacity
  const ICE_COLOR     = '185,229,243';
  const WHITE_COLOR   = '255,255,255';
  const LINE_WIDTH    = 1;
  const SPEED         = 0.00018;    // time advancement per ms

  // Sine parameters per line (seeded deterministically from line index)
  // Primary wave: amplitude A1, frequency F1
  // Harmonic:     amplitude A2, frequency F2, phase offset
  function lineParams(i) {
    const seed = i + 1;
    return {
      A1:    14 + (seed * 7  % 18),   // 14–31 px
      F1:    0.0028 + (seed * 0.0003 % 0.0022),
      A2:    5  + (seed * 3  % 9),    // 5–13 px
      F2:    0.0009 + (seed * 0.0002 % 0.0012),
      phi:   (seed * 1.4)  % (Math.PI * 2),
      phi2:  (seed * 2.1)  % (Math.PI * 2),
      tMult: 0.6 + (seed * 0.07 % 0.8),  // different drift speeds
    };
  }

  const params = Array.from({ length: TOTAL_LINES }, (_, i) => lineParams(i));

  // ── Resize ──────────────────────────────────────────────────────────
  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width  = rect.width  * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width  = rect.width  + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);
    _w = rect.width;
    _h = rect.height;
  }

  let _w = 0, _h = 0;
  window.addEventListener('resize', () => { ctx.setTransform(1,0,0,1,0,0); resize(); });
  resize();

  // ── Animation ────────────────────────────────────────────────────────
  let startTime = null;

  function draw(ts) {
    if (!startTime) startTime = ts;
    const t = (ts - startTime) * SPEED;

    ctx.clearRect(0, 0, _w, _h);

    // Spacing between lines — evenly distribute across height with padding
    const padding = _h * 0.04;
    const gap = (_h - padding * 2) / (TOTAL_LINES - 1);

    for (let i = 0; i < TOTAL_LINES; i++) {
      const isIce = ((i + 1) % ICE_EVERY === 0);
      const p = params[i];
      const baseY = padding + i * gap;

      ctx.beginPath();

      for (let x = 0; x <= _w; x += 2) {
        const tAdv = t * p.tMult;
        const y = baseY
          + p.A1 * Math.sin(p.F1 * x + tAdv + p.phi)
          + p.A2 * Math.sin(p.F2 * x - tAdv * 0.6 + p.phi2);

        if (x === 0) ctx.moveTo(x, y);
        else         ctx.lineTo(x, y);
      }

      if (isIce) {
        ctx.strokeStyle = `rgba(${ICE_COLOR},${ICE_ALPHA})`;
        ctx.lineWidth = LINE_WIDTH * 1.2;
      } else {
        ctx.strokeStyle = `rgba(${WHITE_COLOR},${LINE_ALPHA})`;
        ctx.lineWidth = LINE_WIDTH;
      }
      ctx.stroke();
    }

    requestAnimationFrame(draw);
  }

  requestAnimationFrame(draw);
})();
