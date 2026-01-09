## 2026-01-09 - Accessibility Fixes for Static HTML
**Learning:** In static HTML/JS sites without a framework like React, state management for ARIA attributes (like `aria-expanded`) must be manually handled in the event handlers. Modifying the HTML structure to include ARIA attributes requires careful matching of IDs.
**Action:** When working with raw HTML, ensure every interactive element has a corresponding ID and ARIA attributes (controls, labelledby) explicitly defined, and update the vanilla JS to toggle them.
