# From Default Plot to Data Story: Per-Capita CO2 Emissions


The script turns a default Matplotlib chart of per-capita CO2 emissions for 22 large economies (1990-2024)
into three storytelling alternatives.

| File | Figure in the assignment | Description |
|---|---|---|
| `figures/fig0_baseline.png` | Figure 1 | Baseline: Matplotlib default settings, nothing changed |
| `figures/fig1_highlight_line.png` | Figure 2 | Focused line chart: four countries highlighted against grey context |
| `figures/fig2_slope.png` | Figure 3 | Slope chart: 1990 compared with 2024 |
| `figures/fig3_ranked_bar.png` | Figure 4 | Ranked bar chart for 2024 with the world average |

## Data

Our World in Data, CO2 and Greenhouse Gas Emissions dataset (https://github.com/owid/co2-data),
variable `co2_per_capita` (tonnes per person, fossil fuels and industry, excluding land-use change),
based on the Global Carbon Budget 2025.

The script downloads the version of **2 June 2026** (commit `382ee6c`), so the figures can be reproduced exactly.

## How to run

Requires Python 3.10 or newer.

```bash
pip install -r requirements.txt
python task2_charts.py
```

On macOS use `python3`. If the download fails with `CERTIFICATE_VERIFY_FAILED`, run the
`Install Certificates.command` file in your Python folder under Applications, or download the CSV
from the link in `task2_charts.py` and save it next to the script as `owid-co2-data.csv`.

The four figures are saved in `figures/`. The script also prints every number quoted in the assignment;
the expected output includes:

- Latest complete year: 2024
- World average 2024: 4.7 t
- Countries above world average: 14 of 22
- Countries that rose since 1990: 9; fell: 13
- First year China > United Kingdom: 2014

Tested with Python 3.13/3.14, pandas 3.0.5 and Matplotlib 3.11.2.
