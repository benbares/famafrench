import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Industry Portfolio Analyzer", layout="wide")
st.title("Industry Portfolio Analyzer")

# --- Sidebar controls ---
st.sidebar.header("Settings")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV", type=["csv"],
    help="Upload a portfolio returns CSV. See 'CSV Format' below for supported formats."
)

csv_format = st.sidebar.radio(
    "CSV Format",
    ["Fama-French", "Standard CSV"],
    help=(
        "Fama-French: files from the French Data Library (e.g. 12_Industry_Portfolios.CSV). "
        "Standard CSV: a plain CSV where the first column is a date and the remaining columns are asset returns."
    )
)

if csv_format == "Standard CSV":
    returns_in_pct = st.sidebar.checkbox(
        "Returns are percentages (e.g. 5.24 means 5.24%)",
        value=False,
        help="Check this if your return values are in percentage form rather than decimals (e.g. 5.24 instead of 0.0524)."
    )
    skip_rows = st.sidebar.number_input(
        "Header rows to skip",
        min_value=0, max_value=50, value=0, step=1,
        help="Number of non-data rows at the top of the file to skip before the column headers."
    )
else:
    returns_in_pct = True  # Fama-French files are always in percentage form
    skip_rows = 11

cutoff_date = st.sidebar.date_input(
    "Estimation / Testing Cutoff Date",
    value=pd.Timestamp("1990-12-31"),
    help="Data on or before this date is used to estimate the tangency portfolio. Data after is used for testing."
)

risk_free_rate = st.sidebar.number_input(
    "Monthly Risk-Free Rate (%)",
    min_value=0.0, max_value=5.0, value=0.0, step=0.01,
    help="Used in Sharpe ratio and tangency portfolio calculation."
) / 100

with st.sidebar.expander("Standard CSV format guide"):
    st.markdown(
        """
Your CSV should look like this:

| Date | Asset1 | Asset2 | ... |
|---|---|---|---|
| 2000-01-01 | 0.032 | -0.011 | ... |
| 2000-02-01 | 0.015 | 0.008 | ... |

- **First column:** dates in any standard format (YYYY-MM-DD, MM/DD/YYYY, Jan-2000, etc.)
- **Remaining columns:** one column per asset with monthly return values
- Returns can be decimals (0.032) or percentages (3.2%) — set the checkbox above accordingly
- Missing values should be blank or `NaN`
        """
    )


# --- Helper functions ---
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def convert_ff_date(date_str):
    date_str = str(int(float(date_str)))
    if len(date_str) == 4:
        return pd.to_datetime(date_str + "01", format="%Y%m")
    elif len(date_str) == 6:
        return pd.to_datetime(date_str, format="%Y%m")
    return pd.NaT


def load_fama_french(content: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(content), header=0, skiprows=11)
    df.columns = ["Date"] + list(df.columns[1:])
    df = df[df["Date"].apply(is_number)].dropna(subset=["Date"])
    df["Date"] = df["Date"].apply(convert_ff_date)
    df = df.dropna(subset=["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace("-99.99", "NaN").astype(float) / 100
    return df


def load_standard_csv(content: str, pct: bool, skip: int) -> pd.DataFrame:
    df = pd.read_csv(StringIO(content), skiprows=skip)
    date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True, errors="coerce")
    df = df.dropna(subset=[date_col])
    df = df.rename(columns={date_col: "Date"})
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if pct:
        df = df / 100
    return df


def load_data(file, fmt: str, pct: bool, skip: int) -> pd.DataFrame:
    content = file.read().decode("utf-8", errors="replace")
    if fmt == "Fama-French":
        return load_fama_french(content)
    return load_standard_csv(content, pct, skip)


def tangency_portfolio(expected_returns, cov_matrix, rf=0.0):
    inv_cov = np.linalg.inv(cov_matrix)
    excess = expected_returns - rf
    a = np.dot(inv_cov, excess)
    b = np.dot(np.ones(len(expected_returns)), a)
    return a / b


def sharpe_ratio(returns, rf=0.0):
    excess = returns - rf
    return np.sqrt(12) * excess.mean() / excess.std()


# --- Main analysis ---
if uploaded_file is None:
    st.info("Upload a CSV file in the sidebar to get started. Select the correct CSV Format for your file.")
    st.stop()

with st.spinner("Loading and processing data..."):
    try:
        data = load_data(uploaded_file, csv_format, returns_in_pct, int(skip_rows))
    except Exception as e:
        st.error(f"Failed to parse file: {e}")
        st.stop()

if data.empty or data.shape[1] < 2:
    st.error("The file loaded but contains fewer than 2 asset columns. Check your CSV format settings.")
    st.stop()

cutoff_ts = pd.Timestamp(cutoff_date)
estimation_data = data[data.index <= cutoff_ts]
testing_data = data[data.index > cutoff_ts]

if estimation_data.empty or testing_data.empty:
    st.error("The cutoff date leaves one period empty. Adjust the date and try again.")
    st.stop()

cov_matrix = estimation_data.cov()
expected_returns = estimation_data.mean()

try:
    weights = tangency_portfolio(expected_returns, cov_matrix, risk_free_rate)
except np.linalg.LinAlgError:
    st.error("Covariance matrix is singular — cannot compute tangency portfolio.")
    st.stop()

tangency_returns = (testing_data * weights).sum(axis=1)
equal_weight_returns = testing_data.mean(axis=1)

tangency_sharpe = sharpe_ratio(tangency_returns, risk_free_rate)
equal_weight_sharpe = sharpe_ratio(equal_weight_returns, risk_free_rate)

summary_stats = data.describe().T
summary_stats["skew"] = data.skew()
summary_stats["kurtosis"] = data.kurtosis()

weights_series = pd.Series(weights, index=data.columns).sort_values(ascending=False)

# --- Layout ---
st.subheader("Data Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total months", len(data))
col2.metric("Estimation period", f"{estimation_data.index[0].strftime('%b %Y')} – {estimation_data.index[-1].strftime('%b %Y')}")
col3.metric("Testing period", f"{testing_data.index[0].strftime('%b %Y')} – {testing_data.index[-1].strftime('%b %Y')}")

st.divider()

# --- Summary statistics ---
st.subheader("Table 1: Summary Statistics for Monthly Industry Returns")
st.dataframe(summary_stats.style.format("{:.4f}"), width="stretch")

st.divider()

# --- Tangency portfolio weights ---
st.subheader("Table 2: Tangency Portfolio Weights")
col_left, col_right = st.columns([1, 2])

with col_left:
    st.dataframe(weights_series.to_frame("Weight").style.format("{:.4f}"), width="stretch")

with col_right:
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["steelblue" if w >= 0 else "tomato" for w in weights_series]
    weights_series.plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Tangency Portfolio Weights")
    ax.set_xlabel("Industry")
    ax.set_ylabel("Weight")
    ax.axhline(0, color="black", linewidth=0.8)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.divider()

# --- Tangency returns ---
st.subheader("Figure 2: Monthly Returns — Testing Period")
fig2, ax2 = plt.subplots(figsize=(12, 4))
tangency_returns.plot(ax=ax2, label="Tangency Portfolio", color="steelblue")
equal_weight_returns.plot(ax=ax2, label="Equal Weight Portfolio", color="orange", alpha=0.7)
ax2.set_title("Monthly Returns During Testing Period")
ax2.set_xlabel("Date")
ax2.set_ylabel("Return")
ax2.legend()
ax2.axhline(0, color="black", linewidth=0.5)
plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Tangency Portfolio Return Summary**")
    st.dataframe(tangency_returns.describe().to_frame("Value").style.format("{:.4f}"), width="stretch")
with col_b:
    st.markdown("**Equal Weight Portfolio Return Summary**")
    st.dataframe(equal_weight_returns.describe().to_frame("Value").style.format("{:.4f}"), width="stretch")

st.divider()

# --- Sharpe ratio comparison ---
st.subheader("Table 3: Sharpe Ratio Comparison")
sharpe_df = pd.DataFrame({
    "Tangency Portfolio": [tangency_sharpe],
    "Equally Weighted Portfolio": [equal_weight_sharpe],
}, index=["Sharpe Ratio (annualized)"])
st.dataframe(sharpe_df.style.format("{:.4f}"), width="stretch")

winner = "Tangency" if tangency_sharpe > equal_weight_sharpe else "Equally Weighted"
st.info(f"The **{winner} Portfolio** achieved the higher risk-adjusted return (Sharpe ratio) over the testing period.")

st.divider()

# --- Download results ---
st.subheader("Download Results")
col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    st.download_button("Summary Statistics CSV", summary_stats.to_csv().encode(), "summary_stats.csv", "text/csv")
with col_d2:
    st.download_button("Tangency Weights CSV", weights_series.to_csv().encode(), "tangency_weights.csv", "text/csv")
with col_d3:
    st.download_button("Sharpe Comparison CSV", sharpe_df.to_csv().encode(), "sharpe_comparison.csv", "text/csv")
