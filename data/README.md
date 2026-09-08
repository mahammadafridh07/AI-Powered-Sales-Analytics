# Sample Data

`sample_sales.csv` is a synthetically generated but *realistic* sales
dataset — not random noise. It's produced by `generate_sample_data.py` and
includes:

- 3 years of daily order activity (2023–2025)
- ~29,600 order line items across ~15,800 orders
- 1,400 customers across 5 regions and 5 data-driven segments
- 37 products across 5 categories with different price/margin/popularity
- Region-specific YoY growth rates (8–18%)
- Category-specific seasonality (e.g., Electronics peaks in Nov/Dec)
- Weekly seasonality (weekend dips for B2B-leaning categories)
- ~0.4% injected anomalies (revenue spikes/drops) so anomaly detection has
  real signal to find

Regenerate it any time with:
```bash
python3 generate_sample_data.py
```

The app is seeded from this file via `backend/app/seed.py` (`python -m app.seed`),
which runs the data through the same validation/cleaning pipeline as a real
user upload.
