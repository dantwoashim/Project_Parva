# Tibetan Calendar Notes (Year-2 Week 5)

This release adds a **v1 approximate Tibetan plugin** to support ecosystem integration while preserving explicit confidence labels.

## Precision Modes
- `computed`: proxy through existing Nepal festival rule outputs where available.
- `approximate`: placeholder calendar mapping for unsupported exact conversions.

## Covered Observances (v1)
- Sonam Lhosar
- Gyalpo Lhosar
- Tamu Lhosar
- Saga Dawa (approximate proxy)

## Limitations
- Reverse Tibetan conversion is not enabled.
- Month/leap logic is not yet table-backed.
- Confidence field must be surfaced in consumer UI.
