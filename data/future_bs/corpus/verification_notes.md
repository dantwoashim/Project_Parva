# Future BS Public Corpus Notes

This public repository keeps only a narrow official holdout slice and source-policy metadata.
It must not be described as a complete official historical calendar corpus.

## Public Coverage

- Public official holdout sample: `2078-2083 BS`
- Public source-tier schema: `data/future_bs/public/source_tier_schema.json`
- Public holdout CSV: `data/future_bs/public/official_holdout_2078_2083.csv`

## Private Deployment Data

Larger mixed-source corpora, weak/reference rows, human-review queues, source agreement graphs,
future prediction artifacts, model runs, residual reports, and full solar-ingress caches are ignored
private deployment artifacts.

## Source Rules

- `official_verified`: structured official-source artifacts accepted in repository provenance.
- `printed_verified`: reviewed printed calendar or panchanga evidence.
- `public_witness`: public dated material linking AD and BS dates.
- `publisher_reference`: publisher material used for training or cross-checking only.
- `software_table_reference` and `third_party_reference`: comparison only, not official proof.
- `needs_review`: must not be used for claims without independent review.

## Product Claim Boundary

Future outputs are computed predictions, not official publications.
