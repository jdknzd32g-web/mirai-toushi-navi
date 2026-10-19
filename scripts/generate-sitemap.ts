#!/usr/bin/env tsx
/** Retired: the 2025-only crawler could remove current published URLs. */
console.error('Legacy sitemap generation is disabled. The verified API release pipeline builds sitemap.xml from the current production manifest; see docs/daily-publishing.md.');
process.exitCode = 1;
