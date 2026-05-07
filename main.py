from src.extract import load_data
from src.transform import build_features
from src.analysis import run_analysis
from src.visualization import generate_charts


def main():
    print("Carregando eventos...")
    df = load_data()  # ✅ CORRIGIDO

    print("Transformando dados...")
    df = build_features(df)

    print("Rodando análise...")
    results = run_analysis(df)

    print("Gerando gráficos...")
    generate_charts(results)

    df.to_csv("data/processed/behavioral_features.csv", index=False)
    print("Finalizado 🚀")


if __name__ == "__main__":
    main()