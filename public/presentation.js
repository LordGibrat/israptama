class PresentationController {
  constructor() {
    this.slides = [...document.querySelectorAll('.slide')];
    this.index = 0;
    this.lastWheel = 0;
    this.touchY = null;
    this.counter = document.getElementById('counter');
    this.progress = document.getElementById('progress');
    document.getElementById('previous').addEventListener('click', () => this.go(this.index - 1));
    document.getElementById('next').addEventListener('click', () => this.go(this.index + 1));
    document.addEventListener('keydown', (event) => {
      if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(event.key)) { event.preventDefault(); this.go(this.index + 1); }
      if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(event.key)) { event.preventDefault(); this.go(this.index - 1); }
      if (event.key === 'Home') { event.preventDefault(); this.go(0); }
      if (event.key === 'End') { event.preventDefault(); this.go(this.slides.length - 1); }
    });
    document.addEventListener('wheel', (event) => {
      if (Math.abs(event.deltaY) < 12 || Date.now() - this.lastWheel < 520) return;
      event.preventDefault(); this.lastWheel = Date.now(); this.go(this.index + Math.sign(event.deltaY));
    }, { passive: false });
    document.addEventListener('touchstart', (event) => { this.touchY = event.changedTouches[0].screenY; }, { passive: true });
    document.addEventListener('touchend', (event) => {
      if (this.touchY === null) return;
      const delta = this.touchY - event.changedTouches[0].screenY;
      if (Math.abs(delta) > 45) this.go(this.index + Math.sign(delta));
      this.touchY = null;
    }, { passive: true });
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) if (entry.isIntersecting) this.activate(this.slides.indexOf(entry.target));
    }, { threshold: .55 });
    this.slides.forEach(slide => observer.observe(slide));
    this.activate(0);
  }
  activate(index) {
    if (index < 0) return;
    this.index = index;
    this.slides.forEach((slide, position) => slide.classList.toggle('is-active', position === index));
    this.counter.textContent = `${index + 1} / ${this.slides.length}`;
    this.progress.style.width = `${100 * (index + 1) / this.slides.length}%`;
    document.getElementById('previous').disabled = index === 0;
    document.getElementById('next').disabled = index === this.slides.length - 1;
  }
  go(index) {
    const target = Math.max(0, Math.min(this.slides.length - 1, index));
    this.activate(target);
    this.slides[target].scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
}
new PresentationController();
