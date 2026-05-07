import pandas as pd


def load_data(path="data/raw/events.csv"):
    df = pd.read_csv(path)

    print(f"Dados carregados: {df.shape}")

    return df