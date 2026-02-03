import pandas as pd

# ----------------------------
# Fetch NASDAQ tickers
# ----------------------------
nasdaq_url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
nasdaq_df = pd.read_csv(nasdaq_url, sep="|")
nasdaq_tickers = nasdaq_df["Symbol"].tolist()

# ----------------------------
# Fetch NYSE tickers
# ----------------------------
nyse_url = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
nyse_df = pd.read_csv(nyse_url, sep="|")
nyse_tickers = nyse_df["ACT Symbol"].tolist()

# ----------------------------
# Merge and clean tickers
# ----------------------------
all_tickers = set(nasdaq_tickers + nyse_tickers)

# Remove invalid entries (NaN or empty strings)
all_tickers = {t for t in all_tickers if isinstance(t, str) and t.strip() != ""}

# Save to file
with open("tickers_list.txt", "w") as f:
    for t in sorted(all_tickers):
        f.write(t.strip().upper() + "\n")

print(f"Saved {len(all_tickers)} tickers to tickers_list.txt")
