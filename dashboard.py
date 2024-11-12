import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import locale
from datetime import datetime as dt
import altair as alt
import pandas as pd
import streamlit as st
from src.get_data import GoogleFinance


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

## CONFIGURACOES INICIAIS ##########################################################################################################################################################
st.set_page_config("FINANCES", layout="wide", page_icon="📊")
st.header("FINANCES")

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

## OBTER DADOS DE PLANILHAS ##########################################################################################################################################################
# @st.cache_data
# @st.cache_resource
def get_plans():
    plans = GoogleFinance()
    return plans

## FILTROS DE MES PARA BIG NUMBERS ##########################################################################################################################################################
def filter_latest_month(dataframe: pd.DataFrame):
    df = dataframe
    today = pd.to_datetime("today").to_period("M").start_time
    filtro = df["MES"] == today
    df = df.loc[filtro]
    return df

def filter_previous_month(dataframe: pd.DataFrame):
    df = dataframe
    today = pd.to_datetime("today").to_period("M").start_time
    previous_month = today + pd.DateOffset(months=-1)
    filtro = df["MES"] == previous_month
    df = df.loc[filtro]
    return df

## INSTANCIAR ##########################################################################################################################################################
plans = get_plans()
dre = plans.dre_df_transformation()
ativos = plans.ativos_df_transformation()
cartao = plans.cartao_df_transformation()
luz = plans.luz_df_transformation()


## GERAR DATAS ##########################################################################################################################################################
dre_today = filter_latest_month(dre)
ativos_previous = filter_previous_month(ativos)
actual_month = pd.to_datetime("today").to_period("M").start_time
previous_month = actual_month + pd.DateOffset(months=-1)
forward_month = actual_month + pd.DateOffset(months=1)
twelve_month = actual_month + pd.DateOffset(months=-11)
thirth_month = actual_month + pd.DateOffset(months=-12)
fourth_month = actual_month + pd.DateOffset(months=-13)

## CORES ##########################################################################################################################################################
color_green = "#50fa7b"
color_red = "#ff5e5b"
stroke = 2.5

## BIG NUMBERS ##########################################################################################################################################################
data, bn_receita, bn_despesa, bn_dif, bn_pb, bn_pl, bn_carro = st.columns(7)

with data:
    mes = dre_today["MES_STR"].iloc[0]
    st.metric("Mês", mes)

with bn_receita:
    receita = float(dre_today["RECEITA TOTAL"])
    receita = locale.currency(receita, grouping=True)
    receita = receita.split(",")[0]
    st.metric("Receita", receita)

with bn_despesa:
    despesa = float(dre_today["DESPESAS TOTAL"])
    despesa = locale.currency(despesa, grouping=True)
    despesa = despesa.split(",")[0]
    st.metric("Despesas", despesa)

with bn_dif:
    dif = float(dre_today["RESULTADO"])
    dif = locale.currency(dif, grouping=True)
    dif = dif.split(",")[0]
    st.metric("Resultado", dif)

with bn_pb:
    patri_total = float(ativos_previous["PATRIMONIO_BRUTO"])
    patri_total = locale.currency(patri_total, grouping=True)
    patri_total = patri_total.split(",")[0]
    st.metric("Patrimônio Bruto", patri_total)

with bn_pl:
    patri_liq = float(ativos_previous["PATRIMONIO_LIQUIDO"])
    patri_liq = locale.currency(patri_liq, grouping=True)
    patri_liq = patri_liq.split(",")[0]
    st.metric("Patrimônio Líquido", patri_liq)

with bn_carro:
    carro = float(ativos_previous["CARRO"])
    carro = locale.currency(carro, grouping=True)
    carro = carro.split(",")[0]
    st.metric("Carro", carro)

## GRAFICOS RECEITA, DESPESA E RESULTADO ##########################################################################################################################################################
rec_desp, econ, econ_perc = st.columns(3)

with rec_desp:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["Valor_Formatado"] = dre_filtered["RECEITA TOTAL"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else ""
    )
    chart = (
        alt.Chart(dre_filtered)
        .transform_fold(["RECEITA TOTAL", "DESPESAS TOTAL"], as_=["Categoria", "Valor"])
        .mark_line(strokeWidth=stroke)
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    #ticks=True,
                    grid=False,
                    domain=True,
                    #tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["RECEITA TOTAL", "DESPESAS TOTAL"],
                    range=[f"{color_green}", f"{color_red}"],
                ),
                legend=None,
            ),
        )
        .properties(title="RECEITA vs DESPESA")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=-10,  # Ajuste de posição
        fontWeight="bold",
    ).encode(
        text=alt.condition(
            alt.datum.Categoria == "RECEITA TOTAL",
            alt.Text("Valor_Formatado:N"),
            alt.value("")
        ),
    )
    # Combine o gráfico de linha com o texto
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with econ:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered['R$ Resultado'] = dre_filtered['RESULTADO'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    chart = (
        alt.Chart(dre_filtered)
        .transform_calculate(color_value="if(datum.RESULTADO < 0, 0, 1)")
        .mark_bar()
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "RESULTADO:Q",
                title=None,
                axis=alt.Axis(
                    #ticks=True,
                    grid=False,
                    domain=True,
                    #tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
            color=alt.Color(
                "color_value:O",
                scale=alt.Scale(
                    domain=[0, 1],
                    range=[f"{color_red}", f"{color_green}"],
                ),
                legend=None,
            ),
        )
        .properties(title="RESULTADO")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr(
            "datum.RESULTADO > 0 ? -10 : 10"  # Se o RESULTADO for positivo, coloca o rótulo acima (-10), senão abaixo (+10)
        ),
        # color="#1e6091",
        fontWeight="bold",
        # fontSize=15,
    ).encode(text=alt.Text("R$ Resultado:N"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with econ_perc:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["PERC_RESULTADO"] = (
        dre_filtered["RESULTADO"] / dre_filtered["RECEITA TOTAL"]
    )
    dre_filtered['% Resultado'] = dre_filtered['PERC_RESULTADO'].apply(lambda x: f"{x:,.1%}".replace(".", ","))
    chart = (
        alt.Chart(dre_filtered)
        .transform_calculate(color_value="if(datum.PERC_RESULTADO < 0, 0, 1)")
        .mark_bar()
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "PERC_RESULTADO:Q",
                title=None,
                axis=alt.Axis(
                    #ticks=True,
                    grid=False,
                    domain=True,
                    #tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
            color=alt.Color(
                "color_value:O",
                scale=alt.Scale(
                    domain=[0, 1],
                    range=[f"{color_red}", f"{color_green}"],
                ),
                legend=None,
            ),
        )
        .properties(title="% RESULTADO")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr(
            "datum.PERC_RESULTADO > 0 ? -10 : 10"  # Se o RESULTADO for positivo, coloca o rótulo acima (-10), senão abaixo (+10)
        ),
        # color="#1e6091",
        fontWeight="bold",
        # fontSize=15,
    ).encode(text=alt.Text("% Resultado:N"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

# GRAFICOS DESPESAS ##########################################################################################################################################################
def gastos_barchart(df: pd.DataFrame, col_name: str):
    col = col_name
    dre_filtered = df[
        (df["MES"] <= forward_month) & (dre["MES"] >= thirth_month)
    ]
    dre_filtered[f'R$ {col}'] = dre_filtered[f'{col}'].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    chart = (
        alt.Chart(dre_filtered)
        .mark_bar(color=f"{color_red}")
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                f"{col}:Q",
                title=None,
                axis=alt.Axis(
                    #ticks=True,
                    grid=False,
                    domain=True,
                    #tickColor="gray",
                    domainColor="gray",
                    labels=False,
                ),
            ),
        )
        .properties(title=f"R$ {col}")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        color=f"{color_red}",
        fontWeight="bold",
        # fontSize=15,
    ).encode(text=alt.Text(f'R$ {col}:N'))
    chart = chart + text
    return chart

total_hm = st.container()

total_hm, gastos = st.columns([1, 2])

with total_hm:
    total = gastos_barchart(dre, "DESPESAS TOTAL")
    st.altair_chart(total, use_container_width=True)

    df_long = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= thirth_month)]

    df_long = df_long.melt(
        id_vars=["MES", "MES_STR"],
        value_vars=[
            "DESPESAS TOTAL",
            "MERCADO",
            "DIVERSOS",
            "ASSINATURAS",
            "ROLE",
            "TRANSPORTE",
            "APARTAMENTO",
        ],
        var_name="Categoria",
        value_name="Valor",
    )

    df_long = df_long.sort_values(by=["Categoria", "MES"])

    df_long["Var_perc"] = df_long.groupby(["Categoria"])["Valor"].pct_change()

    df_long['% Variação'] = df_long['Var_perc'].apply(lambda x: f"{x:,.1%}".replace(".", ","))
    
    col_order = [
        "DESPESAS TOTAL",
        "MERCADO",
        "DIVERSOS",
        "ASSINATURAS",
        "ROLE",
        "TRANSPORTE",
        "APARTAMENTO",
    ]

    heatmap = (
        alt.Chart(df_long)
        .mark_rect()
        .encode(
            x=alt.X(
                "Categoria:N",
                title=None,
                sort=col_order,
                axis=alt.Axis(orient="top", labelAngle=0, labelAlign="center"),
            ),
            y=alt.Y(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
            ),
            color=alt.Color(
                "Var_perc:Q",
                scale=alt.Scale(
                    scheme="redyellowgreen",
                    reverse=True,
                    domain=[-0.5, 0.5],
                    clamp=True,
                ),
                title=None,
                legend=None,
            ),
            tooltip=["MES_STR:N", "Categoria:N", "Var_perc:Q"],
        )
        .properties(title="% VARIAÇÃO MENSAL DOS GASTOS", height=350)
    )

    text = heatmap.mark_text(baseline="middle", fontWeight="bold").encode(
        text=alt.Text("% Variação:N"),
        color=alt.condition(
            (alt.datum.Var_perc >= 0.4)
            | (alt.datum.Var_perc <= -0.4),
            alt.value("white"),
            alt.value("black"),
        ),
    )
    chart = heatmap + text
    st.altair_chart(chart, use_container_width=True)

with gastos:
    mercado, diversos, assinaturas = st.columns(3)
    with mercado:
        mercado = gastos_barchart(dre, "MERCADO")
        st.altair_chart(mercado, use_container_width=True)

    with diversos:
        mercado = gastos_barchart(dre, "DIVERSOS")
        st.altair_chart(mercado, use_container_width=True)

    with assinaturas:
        mercado = gastos_barchart(dre, "ASSINATURAS")
        st.altair_chart(mercado, use_container_width=True)

    role, transporte, apartamento = st.columns(3)

    with role:
        mercado = gastos_barchart(dre, "ROLE")
        st.altair_chart(mercado, use_container_width=True)

    with transporte:
        mercado = gastos_barchart(dre, "TRANSPORTE")
        st.altair_chart(mercado, use_container_width=True)
    with apartamento:
        mercado = gastos_barchart(dre, "APARTAMENTO")
        st.altair_chart(mercado, use_container_width=True)

## GRAFICOS DE PATRIMONIO  ##########################################################################################################################################################

patrimonio, investimentos_reserva, dif_rs = st.columns(3)

with patrimonio:
    ativos_filtered = ativos[(ativos["MES"] <= actual_month) & (ativos["MES"] >= thirth_month)]
    ativos_filtered['PATRIMONIO_BRUTO_FORMATADO'] = ativos_filtered['PATRIMONIO_BRUTO'].apply(lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else ""
    )
    print(ativos['PATRIMONIO_BRUTO'])
    chart = (
        alt.Chart(ativos_filtered)
        .mark_bar(color="#00cecb")
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "PATRIMONIO_BRUTO:Q",
                title=None,
                axis=alt.Axis(
                    #ticks=True,
                    grid=False,
                    domain=True,
                    #tickColor="gray",
                    domainColor="gray",
                    labels=False,
                ),
            ),
        )
        .properties(title=f"R$ PATRIMONIO_BRUTO")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        color="#00cecb",
        fontWeight="bold",
        # fontSize=15,
    ).encode(text=alt.Text('PATRIMONIO_BRUTO_FORMATADO:N'))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)


def ativos_charts(df: pd.DataFrame, col_name: str):
    col = col_name
    chart = (
        alt.Chart(ativos_filtered)
        .mark_line(color = '#1dd3b0', strokeWidth=4)
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                f"{col}:Q",
                title=None,
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                ),
            ),
        )
        .properties(title=f"{col}")
    )
    return chart

with investimentos_reserva:
    chart = (
        alt.Chart(ativos_filtered)
        .transform_fold(["INVESTIMENTO", "RESERVAS"], as_=["Categoria", "Valor"])
        .mark_bar(strokeWidth=4)
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["INVESTIMENTO", "RESERVAS"],
                    range=["#1dd3b0", "#086375"],
                ),
                legend=alt.Legend(direction='vertical', columns = 1, title=None, orient='none',legendX=0, legendY=-10),
            ),
        )
        .properties(title="INVESTIMENTOS x RESERVAS")
        )

    # Adiciona o texto ao gráfico

    st.altair_chart(chart, use_container_width=True)

with dif_rs:
    ativos_filtered = ativos[(ativos["MES"] <= actual_month) & (ativos["MES"] >= twelve_month)]
    chart = (
        alt.Chart(ativos_filtered)
        .transform_calculate(color_value="if(datum.DIF_PATRIMONIO < 0, 0, 1)")
        .mark_bar()
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "DIF_PATRIMONIO:Q",
                title=None,
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                ),
            ),
            color=alt.Color(
                "color_value:O",
                scale=alt.Scale(
                    domain=[0, 1],
                    range=[f"{color_red}", "#1dd3b0"],
                ),
                legend=None,
            ),
        )
        .properties(title="RESULTADO PATRIMONIAL")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr(
            "datum.DIF_PATRIMONIO > 0 ? -10 : 10"
        ),
        # color="#1e6091",
        fontWeight="bold",
        # fontSize=15,
    ).encode(text=alt.Text("DIF_PATRIMONIO:Q", format=",.0f"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

# with cresc_real:
#     cr = ativos_charts(ativos,'% CRESCIMENTO REAL')
#     st.altair_chart(cr, use_container_width=True)

# with cresc_real_acum:
#     crum = ativos_charts(ativos,'% CRESCIMENTO REAL')
#     st.altair_chart(crum, use_container_width=True)

## GRAFICOS DA CONTA DE LUZ  ##########################################################################################################################################################
luz_fatura, luz_kwh, preco_kwh = st.columns(3)

with luz_fatura:
    luz_filtered = luz[luz["MES"] >= twelve_month]
    chart = (
        alt.Chart(luz_filtered)
        .transform_fold(["FATURA", "FATURA_PREVISTA"], as_=["Categoria", "Valor"])
        .mark_bar()
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["FATURA", "FATURA_PREVISTA"],
                    range=["#fd3e81", "#adb5bd"],
                ),
                legend=None,
            ),
        )
        .properties(title="LUZ")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        color=f"{color_red}",
        fontWeight="bold",
        # fontSize=15,
    ).encode(
        text=alt.Text("Valor:Q", format=",.0f"),
        color=alt.condition(
            alt.datum.Categoria == "FATURA DA CONTA DE LUZ", 
            alt.value("#fd3e81"),
            alt.value("#adb5bd")
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)
    
with luz_kwh:
    luz_filtered = luz[luz["MES"] >= twelve_month]
    chart = (
        alt.Chart(luz_filtered)
        .transform_fold(["KWH DIA", "KWH_DIA_PREVISTO"], as_=["Categoria", "Valor"])
        .mark_line()
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["KWH DIA", "KWH_DIA_PREVISTO"],
                    range=["#fd3e81", "#adb5bd"],
                ),
                legend=None,
            ),
        )
        .properties(title="CONSUMO KWH POR DIA")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=-10,
        color=f"{color_red}",
        fontWeight="bold",
        # fontSize=15,
    ).encode(
        text=alt.Text("Valor:Q", format=",.1f"),
        color=alt.condition(
            alt.datum.Categoria == "KWH DIA", 
            alt.value("#fd3e81"),
            alt.value("#adb5bd")
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with preco_kwh:
    luz_filtered = luz[(luz["MES"] <= actual_month) & (luz["MES"] >= twelve_month)]
    chart = (
        alt.Chart(luz_filtered)
        .mark_line(color='#fd3e81')
        .encode(
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "PRECO KWH:Q",
                title=None,
                axis=alt.Axis(
                    ticks=True,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                ),
            ),
        )
        .properties(title="PREÇO KWH")
    )
    st.altair_chart(chart, use_container_width=True)
