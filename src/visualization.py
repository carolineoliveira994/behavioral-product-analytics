import os
import matplotlib.pyplot as plt

os.makedirs("output/charts", exist_ok=True)


def plot_funnel(funnel):
    plt.figure(figsize=(8, 5))
    funnel.plot(kind="bar")
    plt.title("Funil real: view → cart → purchase")
    plt.ylabel("Percentual de sessões (%)")
    plt.xlabel("Etapa")
    plt.tight_layout()
    plt.savefig("output/charts/funnel.png")
    plt.close()


def plot_price(price):
    plt.figure(figsize=(8, 5))
    price.plot(kind="bar")
    plt.title("Conversão por faixa de preço")
    plt.ylabel("Taxa de compra (%)")
    plt.xlabel("Faixa de preço")
    plt.tight_layout()
    plt.savefig("output/charts/price.png")
    plt.close()


def plot_decision(decision):
    plt.figure(figsize=(8, 5))
    decision.plot(kind="bar")
    plt.title("Conversão por tempo de decisão")
    plt.ylabel("Taxa de compra (%)")
    plt.xlabel("Tempo")
    plt.tight_layout()
    plt.savefig("output/charts/decision.png")
    plt.close()


def generate_charts(results):
    plot_funnel(results["funnel"])
    plot_price(results["price"])
    plot_decision(results["decision"])