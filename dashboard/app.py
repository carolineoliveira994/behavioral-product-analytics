import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Análise Comportamental do Funil",
    layout="wide"
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "events_sample_dashboard.csv"

df = pd.read_csv(DATA_PATH)

st.sidebar.header("Filtros")

min_price = st.sidebar.slider(
    "Preço mínimo",
    0,
    1000,
    50
)

df_filtered = df[df["price"] >= min_price].copy()
df_filtered["event_time"] = pd.to_datetime(df_filtered["event_time"])

views = len(df_filtered[df_filtered["event_type"] == "view"])
carts = len(df_filtered[df_filtered["event_type"] == "cart"])
purchases = len(df_filtered[df_filtered["event_type"] == "purchase"])
users = df_filtered["user_id"].nunique()

conversion_rate = (purchases / views) * 100 if views > 0 else 0
dropoff_rate = 100 - conversion_rate
view_to_cart = (carts / views) * 100 if views > 0 else 0
cart_to_purchase = (purchases / carts) * 100 if carts > 0 else 0


def limpar_grafico(fig):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False
    )
    return fig


st.title("📊 Por que olhamos, olhamos e não compramos?")
st.subheader("Uma análise comportamental do funil de e-commerce")

st.error(
    f"""
    Principal achado: apenas {view_to_cart:.2f}% dos usuários avançam da visualização para o carrinho.

    O problema mais relevante não parece estar no checkout,
    mas na etapa anterior: transformar interesse em intenção de compra.
    """
)

st.divider()

st.markdown("## Resumo")

st.success(
    """
    Os dados indicam alto volume de navegação, mas baixa conversão.

    A jornada sugere um comportamento exploratório: muitos usuários visualizam produtos,
    poucos avançam para o carrinho e a compra tende a exigir recorrência,
    tempo de decisão e maior estímulo antes do checkout.
    """
)

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Usuários", f"{users:,.0f}")
col2.metric("Taxa de Conversão", f"{conversion_rate:.2f}%")
col3.metric("Abandono", f"{dropoff_rate:.2f}%")
col4.metric("Compras", f"{purchases:,.0f}")
col5.metric("Visualização → Carrinho",f"{view_to_cart:.2f}%")

st.divider()

st.markdown("## 📉 O maior abandono acontece antes do carrinho")

st.info(
    """
    A primeira grande quebra do funil ocorre entre visualizar um produto
    e adicioná-lo ao carrinho. Isso indica que muitos usuários demonstram curiosidade,
    mas ainda não intenção clara de compra.
    """
)

funnel_data = {
    "Etapa": ["Visualização", "Carrinho", "Compra"],
    "Usuários": [views, carts, purchases]
}

df_funnel = pd.DataFrame(funnel_data)

fig_funnel = px.funnel(
    df_funnel,
    x="Usuários",
    y="Etapa",
    title="Funil de Conversão de Usuários",
    color_discrete_sequence=["#4F46E5"]
)

fig_funnel = limpar_grafico(fig_funnel)
st.plotly_chart(fig_funnel, use_container_width=True)

st.divider()

st.markdown("## 🧠 A maioria dos usuários permanece em comportamento exploratório")

user_journey = (
    df_filtered
    .groupby("user_id")["event_type"]
    .unique()
)

view_only = 0
cart_users = 0
purchase_users = 0

for events in user_journey:
    if (
        "view" in events
        and "cart" not in events
        and "purchase" not in events
    ):
        view_only += 1
    elif "cart" in events and "purchase" not in events:
        cart_users += 1
    elif "purchase" in events:
        purchase_users += 1

journey_data = pd.DataFrame({
    "Etapa da Jornada": [
        "Somente Visualização",
        "Abandono de Carrinho",
        "Compradores"
    ],
    "Usuários": [
        view_only,
        cart_users,
        purchase_users
    ]
})

fig_journey = px.bar(
    journey_data,
    x="Etapa da Jornada",
    y="Usuários",
    title="Segmentação da Jornada do Usuário"
)

fig_journey.update_traces(
    marker_color=[
        "#6B7280",
        "#EF4444",
        "#10B981"
    ]
)

fig_journey = limpar_grafico(fig_journey)
st.plotly_chart(fig_journey, use_container_width=True)

st.divider()

st.markdown("## 🔥 A intenção de compra varia conforme o comportamento")

comportamento_usuario = (
    df_filtered
    .groupby("user_id")
    .agg({
        "user_session": "nunique",
        "event_type": lambda x: list(x)
    })
    .reset_index()
)

comportamento_usuario.columns = [
    "user_id",
    "sessoes",
    "eventos"
]


def classificar_intencao(row):
    sessoes = row["sessoes"]
    eventos = row["eventos"]

    if "purchase" in eventos:
        return "Convertido"
    elif "cart" in eventos or sessoes >= 3:
        return "Alta Intenção"
    elif sessoes == 2:
        return "Média Intenção"
    else:
        return "Baixa Intenção"


comportamento_usuario["segmento_intencao"] = (
    comportamento_usuario
    .apply(classificar_intencao, axis=1)
)

ordem_segmentos = [
    "Baixa Intenção",
    "Média Intenção",
    "Alta Intenção",
    "Convertido"
]

dados_intencao = (
    comportamento_usuario["segmento_intencao"]
    .value_counts()
    .reindex(ordem_segmentos, fill_value=0)
    .reset_index()
)

dados_intencao.columns = [
    "Segmento",
    "Usuários"
]

fig_intencao = px.bar(
    dados_intencao,
    x="Segmento",
    y="Usuários",
    title="Segmentação de Intenção Comportamental"
)

fig_intencao.update_traces(
    marker_color=[
        "#6B7280",
        "#F59E0B",
        "#3B82F6",
        "#10B981"
    ]
)

fig_intencao = limpar_grafico(fig_intencao)
st.plotly_chart(fig_intencao, use_container_width=True)

st.divider()

st.markdown("## ⏱ Usuários que compram precisam de mais tempo de decisão")

views_df = (
    df_filtered[df_filtered["event_type"] == "view"]
    .groupby("user_id")["event_time"]
    .min()
    .reset_index(name="primeira_visualizacao")
)

purchase_df = (
    df_filtered[df_filtered["event_type"] == "purchase"]
    .groupby("user_id")["event_time"]
    .min()
    .reset_index(name="primeira_compra")
)

time_to_purchase = pd.merge(
    views_df,
    purchase_df,
    on="user_id"
)

time_to_purchase["horas_ate_compra"] = (
    time_to_purchase["primeira_compra"]
    - time_to_purchase["primeira_visualizacao"]
).dt.total_seconds() / 3600

time_to_purchase = time_to_purchase[
    time_to_purchase["horas_ate_compra"] >= 0
]

fig_time = px.histogram(
    time_to_purchase,
    x="horas_ate_compra",
    nbins=30,
    title="Distribuição do Tempo até a Compra"
)

fig_time.update_traces(
    marker_color="#4F46E5"
)

fig_time = limpar_grafico(fig_time)
st.plotly_chart(fig_time, use_container_width=True)

st.divider()

st.markdown("## 📚 O que aprendemos")

st.success(
    """
    - O principal abandono ocorre antes do carrinho.
    - Muitos usuários navegam, mas não demonstram intenção imediata de compra.
    - Usuários recorrentes e com múltiplas sessões indicam maior potencial de conversão.
    - A compra parece exigir tempo de consideração, não apenas exposição ao produto.
    """
)

st.divider()

st.markdown("## 🚨 Limitações e Qualidade dos Dados")

st.error(
    """
    Em alguns cenários, o número de compras supera o número de eventos de carrinho.

    Isso pode indicar falhas de rastreamento, eventos ausentes ou sessões incompletas.
    Por isso, os resultados devem ser interpretados como uma análise comportamental exploratória.
    """
)

st.divider()

st.markdown("## 🛠 Recomendações")

st.info(
    """
    As ações devem focar em aumentar intenção antes do carrinho,
    não apenas em otimizar o checkout.
    """
)

st.success(
    """
    - Melhorar estímulos para adicionar produtos ao carrinho
    - Criar incentivos para usuários recorrentes
    - Reforçar recomendações personalizadas
    - Testar ofertas para produtos de maior valor
    - Investigar possíveis falhas de tracking no funil
    """
)

st.divider()

st.markdown("## Conclusão Final")

st.info(
    """
    A análise sugere que o desafio principal está em transformar navegação em intenção.

    O usuário demonstra interesse, mas precisa de mais estímulos,
    recorrência e confiança antes de avançar para a compra.
    """
)