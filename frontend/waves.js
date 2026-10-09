/**
 * InteractiveWavesBackground — Vanilla JS
 * Perlin noise + canvas + mouse physics → animated wavy vertical lines.
 *
 * Usage:
 *   const w = new InteractiveWaves('#el', { ...opts });
 *   w.start();
 *   w.destroy();
 */

// ─── Perlin Noise ──────────────────────────────────────────────────────────────

const _G3 = [
  [1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],
  [1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],
  [0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1],
];
const _BP = [
  151,160,137,91,90,15,131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,
  37,240,21,10,23,190,6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,
  57,177,33,88,237,149,56,87,174,20,125,136,171,168,68,175,74,165,71,134,139,48,27,
  166,77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
  102,143,54,65,25,63,161,1,216,80,73,209,76,132,187,208,89,18,169,200,196,135,130,
  116,188,159,86,164,100,109,198,173,186,3,64,52,217,226,250,124,123,5,202,38,147,
  118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,223,183,170,213,
  119,248,152,2,44,154,163,70,221,153,101,155,167,43,172,9,129,22,39,253,19,98,108,
  110,79,113,224,232,178,185,112,104,218,246,97,228,251,34,242,193,238,210,144,12,
  191,179,162,241,81,51,145,235,249,14,239,107,49,192,214,31,181,199,106,157,184,84,
  204,176,115,121,50,45,127,4,150,254,138,236,205,93,222,114,67,29,24,72,243,141,
  128,195,78,66,215,61,156,180,
];

class _Noise {
  constructor(seed) {
    this.p = new Array(512);
    this.g = new Array(512);
    seed = (Math.floor(seed) & 0xffffffff) || 1;
    if (seed < 256) seed |= seed << 8;
    for (let i = 0; i < 256; i++) {
      const v = (i & 1) ? _BP[i] ^ (seed & 255) : _BP[i] ^ ((seed >> 8) & 255);
      this.p[i] = this.p[i + 256] = v;
      this.g[i] = this.g[i + 256] = _G3[v % 12];
    }
  }
  _f(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
  _l(a, b, t) { return a + t * (b - a); }
  get2(x, y) {
    const xi = Math.floor(x) & 255, yi = Math.floor(y) & 255;
    x -= Math.floor(x); y -= Math.floor(y);
    const u = this._f(x), v = this._f(y);
    const d = (gi, px, py) => gi[0] * px + gi[1] * py;
    return this._l(
      this._l(d(this.g[xi   + this.p[yi  ]], x,   y  ), d(this.g[xi+1 + this.p[yi  ]], x-1, y  ), u),
      this._l(d(this.g[xi   + this.p[yi+1]], x,   y-1), d(this.g[xi+1 + this.p[yi+1]], x-1, y-1), u),
      v
    );
  }
}

// ─── Main class ────────────────────────────────────────────────────────────────

class InteractiveWaves {
  constructor(container, opts = {}) {
    this.el = typeof container === 'string'
      ? document.querySelector(container) : container;
    if (!this.el) throw new Error('InteractiveWaves: container not found');

    this.cfg = {
      lineColor:     opts.lineColor     ?? 'rgba(255,255,255,0.13)',
      waveSpeedX:    opts.waveSpeedX    ?? 0.0125,
      waveSpeedY:    opts.waveSpeedY    ?? 0.005,
      waveAmpX:      opts.waveAmpX      ?? 32,
      waveAmpY:      opts.waveAmpY      ?? 16,
      xGap:          opts.xGap          ?? 10,
      yGap:          opts.yGap          ?? 32,
      friction:      opts.friction      ?? 0.925,
      tension:       opts.tension       ?? 0.005,
      maxCursorMove: opts.maxCursorMove ?? 100,
      lineWidth:     opts.lineWidth     ?? 1,
    };

    this._noise  = new _Noise(Math.random() * 65536 | 0);
    this._lines  = [];
    this._raf    = null;
    this._r      = { w: 0, h: 0, left: 0, top: 0 };  // bounding rect
    this._m      = { x: -9999, y: -9999, lx: 0, ly: 0, sx: 0, sy: 0,
                     v: 0, vs: 0, a: 0, on: false };  // mouse state

    // Build DOM
    this.el.style.cssText += ';position:relative;overflow:hidden;';
    this._cvs = document.createElement('canvas');
    this._cvs.style.cssText =
      'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;display:block;';
    this._dot = document.createElement('div');
    this._dot.style.cssText =
      'position:absolute;top:0;left:0;width:8px;height:8px;border-radius:50%;' +
      'background:rgba(232,115,43,0.7);box-shadow:0 0 14px 5px rgba(232,115,43,0.28);' +
      'pointer-events:none;will-change:transform;opacity:0;transition:opacity .4s;z-index:3;';
    this.el.prepend(this._cvs);
    this.el.prepend(this._dot);
    this._ctx = this._cvs.getContext('2d');

    // Stable bound handlers (so removeEventListener works)
    this._hResize = () => this._resize();
    this._hMouse  = (e) => this._setMouse(e.clientX, e.clientY);
    this._hTouch  = (e) => { e.preventDefault(); this._setMouse(e.touches[0].clientX, e.touches[0].clientY); };
    this._hTick   = (t) => this._tick(t);
  }

  // ── Size + grid ───────────────────────────────────────────────────────────

  _resize() {
    const rect = this.el.getBoundingClientRect();
    const dpr  = window.devicePixelRatio || 1;
    this._r = { w: rect.width, h: rect.height, left: rect.left, top: rect.top };

    // Always reset transform before scaling to prevent accumulation
    this._ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this._cvs.width  = rect.width  * dpr;
    this._cvs.height = rect.height * dpr;
    this._cvs.style.width  = rect.width  + 'px';
    this._cvs.style.height = rect.height + 'px';

    this._buildGrid();
  }

  _buildGrid() {
    const { w, h }           = this._r;
    const { xGap, yGap }     = this.cfg;
    const cols = Math.ceil((w + 200) / xGap) + 1;
    const rows = Math.ceil((h +  30) / yGap) + 1;
    const x0   = (w - xGap * (cols - 1)) / 2;
    const y0   = (h - yGap * (rows - 1)) / 2;
    this._lines = [];
    for (let c = 0; c < cols; c++) {
      const col = [];
      for (let r = 0; r < rows; r++) {
        col.push({ x: x0 + c * xGap, y: y0 + r * yGap,
                   wx: 0, wy: 0, cx: 0, cy: 0, cvx: 0, cvy: 0 });
      }
      this._lines.push(col);
    }
  }

  // ── Physics ───────────────────────────────────────────────────────────────

  _update(t) {
    const { waveSpeedX, waveSpeedY, waveAmpX, waveAmpY,
            friction, tension, maxCursorMove } = this.cfg;
    const m = this._m, n = this._noise;

    for (const col of this._lines) {
      for (const p of col) {
        const nv = n.get2(
          (p.x + t * waveSpeedX) * 0.002,
          (p.y + t * waveSpeedY) * 0.0015,
        ) * 12;
        p.wx = Math.cos(nv) * waveAmpX;
        p.wy = Math.sin(nv) * waveAmpY;

        if (m.on) {
          const dx    = p.x - m.sx;
          const dy    = p.y - m.sy;
          const dist  = Math.hypot(dx, dy);
          const reach = Math.max(175, m.vs);
          if (dist < reach) {
            const s = 1 - dist / reach;
            const f = Math.cos(dist * 0.001) * s;
            p.cvx += Math.cos(m.a) * f * reach * m.vs * 0.00065;
            p.cvy += Math.sin(m.a) * f * reach * m.vs * 0.00065;
          }
        }

        p.cvx += -p.cx * tension;
        p.cvy += -p.cy * tension;
        p.cvx *= friction;
        p.cvy *= friction;
        p.cx  += p.cvx * 2;
        p.cy  += p.cvy * 2;
        p.cx   = Math.max(-maxCursorMove, Math.min(maxCursorMove, p.cx));
        p.cy   = Math.max(-maxCursorMove, Math.min(maxCursorMove, p.cy));
      }
    }
  }

  // ── Draw ──────────────────────────────────────────────────────────────────

  _pos(p, cur = true) {
    return [p.x + p.wx + (cur ? p.cx : 0), p.y + p.wy + (cur ? p.cy : 0)];
  }

  _draw() {
    const { w, h } = this._r;
    const ctx = this._ctx;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = this.cfg.lineColor;
    ctx.lineWidth   = this.cfg.lineWidth;
    ctx.lineJoin    = 'round';
    ctx.lineCap     = 'round';

    for (const col of this._lines) {
      const n = col.length;
      if (n < 2) continue;
      ctx.beginPath();

      // Move to first point without cursor offset (stable anchor)
      const [x0, y0] = this._pos(col[0], false);
      ctx.moveTo(x0, y0);

      // Smooth the curve: quadratic bezier through mid-points
      for (let i = 0; i < n - 1; i++) {
        const [ax, ay] = this._pos(col[i]);
        const [bx, by] = this._pos(col[i + 1]);
        ctx.quadraticCurveTo(ax, ay, (ax + bx) / 2, (ay + by) / 2);
      }

      // Close to last point
      const [lx, ly] = this._pos(col[n - 1]);
      ctx.lineTo(lx, ly);

      ctx.stroke();
    }
  }

  // ── Tick ──────────────────────────────────────────────────────────────────

  _tick(t) {
    const m = this._m;
    m.sx += (m.x - m.sx) * 0.1;
    m.sy += (m.y - m.sy) * 0.1;
    const dx = m.x - m.lx, dy = m.y - m.ly;
    m.v    = Math.hypot(dx, dy);
    m.vs  += (m.v  - m.vs)  * 0.1;
    m.vs   = Math.min(100, m.vs);
    m.lx   = m.x; m.ly = m.y;
    m.a    = Math.atan2(dy, dx);

    if (m.on) {
      this._dot.style.opacity   = '1';
      this._dot.style.transform =
        `translate3d(calc(${m.sx}px - 50%),calc(${m.sy}px - 50%),0)`;
    }

    this._update(t);
    this._draw();
    this._raf = requestAnimationFrame(this._hTick);
  }

  // ── Mouse ─────────────────────────────────────────────────────────────────

  _setMouse(cx, cy) {
    const m = this._m;
    m.x = cx - this._r.left;
    m.y = cy - this._r.top;
    if (!m.on) { m.sx = m.x; m.lx = m.x; m.sy = m.y; m.ly = m.y; m.on = true; }
  }

  // ── Public ────────────────────────────────────────────────────────────────

  start() {
    // Defer one frame so layout is complete and getBCR is accurate
    requestAnimationFrame(() => {
      this._resize();
      this._raf = requestAnimationFrame(this._hTick);
    });
    window.addEventListener('resize',    this._hResize);
    window.addEventListener('mousemove', this._hMouse);
    window.addEventListener('touchmove', this._hTouch, { passive: false });
    return this;
  }

  destroy() {
    if (this._raf) cancelAnimationFrame(this._raf);
    window.removeEventListener('resize',    this._hResize);
    window.removeEventListener('mousemove', this._hMouse);
    window.removeEventListener('touchmove', this._hTouch);
    this._cvs.remove();
    this._dot.remove();
  }

  setOption(k, v) { this.cfg[k] = v; }
}
