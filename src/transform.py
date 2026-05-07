import pandas as pd


def build_features(df):
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")

    df = df.sort_values(["user_session", "event_time"])

    funnel = (
        df.groupby(["user_session", "event_type"])
        .size()
        .unstack(fill_value=0)
    )

    funnel["view"] = (funnel.get("view", 0) > 0).astype(int)
    funnel["cart"] = (funnel.get("cart", 0) > 0).astype(int)
    funnel["purchase"] = (funnel.get("purchase", 0) > 0).astype(int)

    first_event = df.groupby("user_session")["event_time"].min()
    last_event = df.groupby("user_session")["event_time"].max()

    funnel["time_minutes"] = (
        (last_event - first_event).dt.total_seconds() / 60
    )

    funnel["price"] = df.groupby("user_session")["price"].mean()

    bins = [0, 50, 150, 300, 600, float("inf")]
    labels = ["≤50", "51–150", "151–300", "301–600", ">600"]

    funnel["price_band"] = pd.cut(funnel["price"], bins=bins, labels=labels)

    funnel["behavior"] = funnel["purchase"].apply(
        lambda x: "purchased" if x == 1 else "abandoned"
    )

    return funnel.reset_index()