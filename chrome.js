// ClariComp - shared nav + footer rendering
// Injected into placeholders <div id="nav"></div> and <div id="footer"></div>

(function () {
  const path = (location.pathname.split('/').pop() || 'index.html').toLowerCase();

  const navLinks = [
    { href: 'how-it-works.html', label: 'How it works' },
    { href: 'methodology.html', label: 'Methodology' },
    { href: 'compliance.html', label: 'Tender compliance' },
    { href: 'guides.html', label: 'Guides' },
    { href: 'pricing.html', label: 'Pricing' },
  ];

  const logoSvg = (stroke, dot) => `
    <svg class="logo-mark" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="0.75" y="0.75" width="30.5" height="30.5" rx="1.5" stroke="${stroke}" stroke-width="1.2"/>
      <path d="M23 10.2C21.32 8.45 18.95 7.4 16.3 7.4C10.92 7.4 6.5 11.82 6.5 17.2C6.5 22.58 10.92 27 16.3 27" stroke="${stroke}" stroke-width="2.4" stroke-linecap="round"/>
      <line x1="20" y1="17.2" x2="26.5" y2="17.2" stroke="${stroke}" stroke-width="2.2" stroke-linecap="round"/>
      <circle cx="26.5" cy="17.2" r="1.6" fill="${dot}"/>
    </svg>`;

  const isActive = (href) => {
    if (href === 'guides.html' && /guide-/.test(path)) return true;
    return href === path;
  };

  const navHTML = `
    <nav class="nav">
      <div class="nav__inner">
        <a href="index.html" class="nav__brand" aria-label="ClariComp home">
          ${logoSvg('#203848', '#546C7B')}
          <span class="wordmark">
            <span class="wordmark__clari">Clari</span><span class="wordmark__comp">Comp</span>
          </span>
        </a>
        <div class="nav__links">
          ${navLinks
            .map((l) => `<a href="${l.href}" class="${isActive(l.href) ? 'is-active' : ''}">${l.label}</a>`)
            .join('')}
        </div>
        <a href="preview.html" class="nav__cta">Try the preview</a>
      </div>
    </nav>`;

  const footerHTML = `
    <footer class="footer">
      <div class="container">
        <div class="footer__grid">
          <div class="footer__col footer__brand">
            <a href="index.html" class="nav__brand" style="color: var(--white);">
              ${logoSvg('#E3EDF5', '#95A7B3')}
              <span class="wordmark">
                <span class="wordmark__clari" style="color: #E3EDF5;">Clari</span><span class="wordmark__comp" style="color: #95A7B3;">Comp</span>
              </span>
            </a>
            <p>Audit-ready carbon reporting for UK manufacturers and contractors. Built on DEFRA 2025 and the GHG Protocol.</p>
          </div>
          <div class="footer__col">
            <h4>Product</h4>
            <a href="how-it-works.html">How it works</a>
            <a href="methodology.html">Methodology</a>
            <a href="pricing.html">Pricing</a>
            <a href="preview.html">Try the preview</a>
            <a href="sample-report.html">Sample report</a>
          </div>
          <div class="footer__col">
            <h4>Compliance</h4>
            <a href="compliance.html">Tender compliance</a>
            <a href="guides.html">Guides</a>
            <a href="faq.html">FAQ</a>
            <a href="privacy.html">Data privacy</a>
          </div>
          <div class="footer__col">
            <h4>Contact</h4>
            <a href="mailto:seyi@claricomp.co.uk">seyi@claricomp.co.uk</a>
            <a href="contact.html">Book a call</a>
            <a href="https://claricomp.co.uk" target="_blank" rel="noopener">claricomp.co.uk</a>
          </div>
        </div>
        <div class="footer__bottom">
          <div>© 2026 ClariComp · DEFRA 2025 · GHG Protocol · Haversine methodology</div>
          <div>Built in the UK</div>
        </div>
      </div>
    </footer>`;

  const navMount = document.getElementById('nav');
  const footerMount = document.getElementById('footer');
  if (navMount) navMount.outerHTML = navHTML;
  if (footerMount) footerMount.outerHTML = footerHTML;
})();
