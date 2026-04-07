# Known Limitations

Project Parva is useful today, but it is not complete or universally authoritative.

## Calendrical and data limits

1. Regional and tradition-specific observance can differ. Parva outputs are profile-based, not a universal religious authority.
2. Some festival rows are still provisional or source-review-driven rather than fully authority-reviewed.
3. Fine boundary cases near sunrise can differ when timezone or location inputs change.
4. Conflict handling is explicit, but a stable public default is still a policy choice when sources disagree.

## Product and platform limits

1. The reference frontend is maintained as a public reference app, not a fully finished consumer product.
2. Account sync, cross-device member state, and premium household workflows are not fully delivered in the open-source core today.
3. Remote place search may rely on external geocoding providers when the offline gazetteer is insufficient.
4. Experimental alias tracks (`/v2`, `/v4`, `/v5`) are not independent API versions.

## Operational limits

1. Self-hosting without durable Redis-backed throttling is fine for local or low-risk environments, but not the intended production posture.
2. Public trust metadata improves traceability. It is not legal, civil, or doctrinal certification.
3. Raw archival source material under `data/source_archive/` still needs ongoing redistribution and cleanup review.
