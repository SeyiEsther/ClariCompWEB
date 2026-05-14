# ClariComp - static site

Audit-ready carbon reporting for UK manufacturers and contractors. Built for SECR
and PPN 06/21. Static HTML + CSS + a tiny bit of vanilla JS - no build step,
no framework, no dependencies.

## Deploy to Netlify

### Option 1 - drag and drop
1. Sign in at https://app.netlify.com
2. Drag the unzipped folder onto the "Sites" page (or visit https://app.netlify.com/drop)
3. Netlify publishes the site immediately on a free `*.netlify.app` subdomain
4. Add your custom domain `claricomp.co.uk` from Site settings -> Domain management

### Option 2 - Git-backed
1. Push this folder to a GitHub / GitLab / Bitbucket repo
2. In Netlify, "Add new site" -> "Import existing project"
3. Build command: (leave blank). Publish directory: `.`
4. `netlify.toml` is already configured

### Custom domain
- Add `claricomp.co.uk` and `www.claricomp.co.uk` in Domain management
- Point DNS at Netlify (or let Netlify manage DNS)
- HTTPS is automatic via Let's Encrypt

## File map

| File                    | Purpose                                       |
|-------------------------|-----------------------------------------------|
| index.html              | Home                                          |
| how-it-works.html       | Six-step walkthrough                          |
| methodology.html        | DEFRA + Haversine methodology, factor table   |
| compliance.html         | PPN 06/21 tender hub                          |
| pricing.html            | Three tiers, comparison table                 |
| guides.html             | Articles hub                                  |
| guide-crp.html          | CRP guide                                     |
| guide-spreadsheet.html  | Spreadsheet guide                             |
| guide-buyers.html       | Buyers guide                                  |
| guide-auditor.html      | Auditor guide                                 |
| faq.html                | 12 common questions                           |
| contact.html            | Direct email + booking placeholder            |
| privacy.html            | Data privacy statement                        |
| preview.html            | Upload form with validation states (demo)     |
| results.html            | Preview dashboard (demo data)                 |
| sample-report.html      | PDF mock + report contents                    |
| styles.css              | Shared design system                          |
| chrome.js               | Nav + footer injection                        |
| netlify.toml            | Headers + caching                             |

## Things to wire up before launch

- `preview.html` form currently navigates to `results.html`. Wire the form
  submission to a real backend (Netlify Functions, a separate API, etc.)
- Template `.xlsx` and sample PDF downloads are placeholders (alert dialogs).
  Drop real files in and replace the `onclick`s.
- Contact form (`contact.html`) is a placeholder. Wire to Netlify Forms by
  adding `data-netlify="true"` and a `name` attribute to the `<form>`, or
  swap in a real submission endpoint.
- Calendly link on contact page is a placeholder.

## Brand

- Colour tokens in `styles.css` :root - white, blue-light, navy, mid, teal,
  bg, card, border, text, text-mid, text-light
- Typography: DM Serif Display (headings), DM Sans (body), DM Mono (technical)
- Logo: monogram + wordmark, rendered inline via `chrome.js`
