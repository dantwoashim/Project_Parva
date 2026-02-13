# Week 40 Usability Walkthrough (Desktop)

## Flow Checked
1. Landing page loads
2. Festival browse/list
3. Festival detail open
4. Mythology tab
5. Ritual tab
6. Explain panel
7. Map/temple section

## Findings
- Detail dates now come from detail API (`dates`) and are consistent with v2 contract.
- Ritual tab renders normalized data shape; empty states are explicit when data absent.
- Explain panel opens and resolves explanation via `/v2/api/festivals/{id}/explain`.
- Error boundary exists for top-level UI fallback.

## Fixes Confirmed
- Temple hooks point to versioned base path by default (`/v2/api`).
- PropTypes updated for backend field names (`description`, `calendar_type`, `regional_focus`).

## Build Validation
- Frontend production build passes.
