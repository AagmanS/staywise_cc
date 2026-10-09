/* ============================================
   STAYWISE — MAIN.JS
   Landing page interactions
   ============================================ */

// ---- Intersection Observer — reveal on scroll ----
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll(
  '.what-card, .benefit-card'
).forEach((el, i) => {
  el.classList.add('reveal');
  el.style.transitionDelay = `${i * 60}ms`;
  revealObserver.observe(el);
});

// ---- Scroll reveal for problem + benefits note ----
const sectionRevealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      sectionRevealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.problem-body, .benefits-note').forEach(el => {
  el.classList.add('reveal');
  sectionRevealObserver.observe(el);
});
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ---- CTA button hover ripple effect ----
document.querySelectorAll('.cta-btn').forEach(btn => {
  btn.addEventListener('mouseenter', function(e) {
    this.style.letterSpacing = '3px';
  });
  btn.addEventListener('mouseleave', function() {
    this.style.letterSpacing = '2px';
  });
});

// ---- Feature item stagger on load ----
document.querySelectorAll('.feature-item').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateX(-12px)';
  setTimeout(() => {
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    el.style.opacity = '1';
    el.style.transform = '';
  }, 600 + i * 100);
});

// ---- Hero right stagger on load ----
document.querySelectorAll('.hero-tagline p, .hero-desc, .hero-right-stats, .hero-right .cta-btn').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(14px)';
  setTimeout(() => {
    el.style.transition = 'opacity 0.55s ease, transform 0.55s ease';
    el.style.opacity = '1';
    el.style.transform = '';
  }, 400 + i * 120);
});

// ---- Title lines animate in ----
document.querySelectorAll('.title-line').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(40px)';
  setTimeout(() => {
    el.style.transition = 'opacity 0.7s cubic-bezier(0.4,0,0.2,1), transform 0.7s cubic-bezier(0.4,0,0.2,1)';
    el.style.opacity = '1';
    el.style.transform = '';
  }, 100 + i * 150);
});

// ---- Title underline animate ----
const underline = document.querySelector('.title-underline');
if (underline) {
  underline.style.transform = 'scaleX(0)';
  underline.style.transformOrigin = 'left';
  setTimeout(() => {
    underline.style.transition = 'transform 0.6s cubic-bezier(0.4,0,0.2,1)';
    underline.style.transform = 'scaleX(1)';
  }, 600);
}

console.log('%c StayWise ✓ ', 'background:#e8732b;color:white;font-weight:900;padding:4px 10px;border-radius:4px;font-family:monospace');
