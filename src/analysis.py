import pandas as pd


def run_analysis(df):
    print("Rodando análise comportamental REAL...")

    funnel = df[["view", "cart", "purchase"]].mean() * 100
    print("\nFunil real (%):")
    print(funnel)

    df["time_bucket"] = pd.cut(
        df["time_minutes"],
        bins=[0, 5, 30, 120, 1440, float("inf")],
        labels=["≤5min", "5–30min", "30m–2h", "2h–24h", ">24h"],
        include_lowest=True,
    )

    decision = df.groupby("time_bucket", observed=True)["purchase"].mean() * 100
    print("\nConversão por tempo:")
    print(decision)

    price = df.groupby("price_band", observed=True)["purchase"].mean() * 100
    print("\nConversão por preço:")
    print(price)

    return {
        "funnel": funnel,
        "decision": decision,
        "price": price,
    }