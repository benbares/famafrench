# Fama-French 12 Industry Portfolio Analyzer

An interactive web app for analyzing Fama-French 12 Industry Portfolio data. It builds a tangency portfolio from a historical estimation period and evaluates its out-of-sample performance against an equally weighted portfolio.

**Live app:** *(add your Streamlit Cloud URL here once deployed)*

---

## Using the App (No Installation Required)

The easiest way to use this app is through the hosted link above — just open it in any browser. No Python, no installs, nothing to download.

If the hosted link is unavailable, follow the local setup instructions below.

---

## Getting the Data

Regardless of how you run the app, you will need to download the data file first:

1. Go to: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
2. Under **Industry Portfolios**, find **"12 Industry Portfolios"** and download the CSV (monthly, value-weighted returns)
3. Extract the `.CSV` file from the zip — it will be named `12_Industry_Portfolios.CSV`

---

## Deploying to Streamlit Cloud (for the app owner)

This is the recommended way to share the app with others. It's free and takes about 5 minutes.

### Step 1 — Push to GitHub

1. Create a free account at [github.com](https://github.com) if you don't have one
2. Create a new **public** repository (e.g., `portfolio-analyzer`)
3. Upload these three files to the repository:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`

   You can drag and drop them directly on the GitHub website — no terminal needed.

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account
2. Click **"New app"**
3. Select your repository and set the main file path to `app.py`
4. Click **"Deploy"** — it will build and launch automatically in about a minute
5. Copy the URL it gives you and share it with anyone

That's it. Anyone with the link can open the app in their browser — no installs required.

---

## Local Setup (if you prefer to run it on your own computer)

### Requirements
- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) package manager (recommended) **or** pip

### Option A — using uv

1. Install uv if you don't have it:
   ```
   pip install uv
   ```

2. Open a terminal in the project folder and create a virtual environment:
   ```
   uv venv .venv --python 3.14
   ```

3. Install dependencies:
   ```
   uv pip install streamlit pandas numpy matplotlib scipy --python .venv\Scripts\python.exe
   ```

### Option B — using pip

1. Open a terminal in the project folder and create a virtual environment:
   ```
   python -m venv .venv
   ```

2. Activate it:
   ```
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running locally

```
.venv\Scripts\streamlit run app.py
```

The app will open automatically at **http://localhost:8501** in your browser.

---

## Getting the Data

This app is designed for **Fama-French Industry Portfolio CSV files**, available for free from the Kenneth French Data Library:

1. Go to: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
2. Under **Industry Portfolios**, download **"12 Industry Portfolios"** (monthly, value-weighted returns)
3. Extract the `.CSV` file from the zip

The file will be named something like `12_Industry_Portfolios.CSV`.

---

## How to Use the App

### 1. Upload Your Data (Sidebar)

Click **"Upload CSV"** in the left sidebar and select your file. Then choose the correct **CSV Format**:

**Fama-French** — for files downloaded directly from the Kenneth French Data Library. The app handles all the messy header rows and date formatting automatically.

**Standard CSV** — for any other monthly returns data. Your file should have a date column first, followed by one column per asset. Two additional options appear:
- *Returns are percentages* — check this if your values are like `5.24` (meaning 5.24%). Leave unchecked if they are already decimals like `0.0524`.
- *Header rows to skip* — if your file has description text before the actual column headers, enter how many rows to skip. Most standard CSVs are `0`.

A format example is available under the **"Standard CSV format guide"** dropdown in the sidebar.

### 2. Configure Settings (Sidebar)

**Estimation / Testing Cutoff Date**
The data is split into two periods at this date:
- **Estimation period** (on or before the cutoff) — used to calculate the optimal portfolio weights
- **Testing period** (after the cutoff) — used to evaluate how those weights performed out-of-sample

Default: December 31, 1990. Adjust this to change how much historical data is used for training vs. evaluation.

**Monthly Risk-Free Rate (%)**
The risk-free rate used in the Sharpe ratio calculation and tangency portfolio optimization. Default is 0%. You can set this to a monthly T-bill rate if desired (e.g., 0.04% for a ~0.5% annual rate).

---

## Output Sections

### Data Overview
Three summary metrics at the top showing:
- Total number of months in the dataset
- The date range of the estimation period
- The date range of the testing period

### Table 1 — Summary Statistics for Monthly Industry Returns
Descriptive statistics across the full dataset for all 12 industries:
- **count, mean, std, min, max** — standard distribution stats
- **25%, 50%, 75%** — quartiles
- **skew** — positive skew means the distribution has a long right tail (occasional large gains)
- **kurtosis** — high kurtosis means more extreme values than a normal distribution

### Table 2 — Tangency Portfolio Weights
Shows how much of the portfolio is allocated to each industry. The tangency portfolio is the mean-variance optimal portfolio — it maximizes the Sharpe ratio based on the estimation period data.
- **Positive weights** = long positions (buying that industry)
- **Negative weights** = short positions (betting against that industry)
- Weights can exceed 1.0 or go below -1.0, which implies leverage

The bar chart gives a visual breakdown — blue bars are long, red bars are short.

### Figure 2 — Monthly Returns (Testing Period)
A line chart comparing month-by-month returns of:
- **Tangency Portfolio** (blue) — the optimized portfolio using weights from the estimation period
- **Equal Weight Portfolio** (orange) — a simple benchmark that puts the same weight in every industry each month

Below the chart are return summary tables for both portfolios (mean, std, min, max, etc.).

### Table 3 — Sharpe Ratio Comparison
Compares the annualized Sharpe ratio of both portfolios over the testing period.

**Sharpe Ratio = (Average Excess Return) / (Standard Deviation) × √12**

A higher Sharpe ratio means better risk-adjusted performance. The app highlights which portfolio won.

### Download Results
Three buttons to export results as CSV files:
- **Summary Statistics CSV** — full Table 1 output
- **Tangency Weights CSV** — the portfolio weights
- **Sharpe Comparison CSV** — the Sharpe ratio table

---

## Project Files

| File | Description |
|---|---|
| `app.py` | The Streamlit application |
| `requirements.txt` | Package versions — used by Streamlit Cloud and pip |
| `.streamlit/config.toml` | Streamlit configuration (disables usage stats) |
| `.venv/` | Python virtual environment (local only, not needed for cloud) |
| `12_Industry_Portfolios.CSV` | Source data (not included — download separately) |
| `BaresBen_FinalProject.ipynb` | Original Jupyter notebook this app is based on |
