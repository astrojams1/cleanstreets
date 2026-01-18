# Clean Streets - Agent Directives

Guidelines for AI agents working on this codebase.

## Content Guidelines

### Partner Blurbs
- Always write partner descriptions from Clean Streets' point of view
- Use "they/their" when referring to partner organizations, never "we/our"
- Keep blurbs concise (1-2 sentences) and focused on the partner's mission

### Tone
- Professional but warm and community-focused
- Avoid jargon; use plain language accessible to all neighbors
- Emphasize community impact and collective action

## Technical Guidelines

### HTML Structure
- This is a static HTML site using Tailwind CSS via CDN
- Follow existing section patterns: uppercase tracking label, serif heading, content
- Use semantic HTML with proper accessibility attributes (aria-labels, roles)
- Add `scroll-mt-32` class to sections for proper scroll-to behavior with sticky nav

### Styling
- Primary brand color: `brand-action` (#F25C05 - Safety Orange)
- Background: `brand-bg` (#fdf1ec - Warm beige)
- Dark text: `brand-dark` (#1a1a1a)
- Use existing Tailwind classes; extend via `tailwind.config` in `<script>` tag if needed
- Typography: Merriweather for headings, Inter for body text

### Images
- Partner logos go in `images/partners/`
- Apply `partner-logo` class for consistent grayscale styling
- Use descriptive alt text for accessibility

### Navigation
- Update both desktop menu and mobile menu when adding new sections
- Desktop menu: around line 222-254
- Mobile menu: around line 264-293

## Automation
- Supporter list is auto-updated via `scripts/update_supporters.py`
- Impact metrics are fetched from Google Sheets
- Do not manually edit the `#supporters` or `#top-supporters` lists
