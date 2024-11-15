import os
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import locale
import altair as alt
import pandas as pd
import streamlit as st
from datetime import datetime as dt
from src.get_data import GoogleFinance
import logging

logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv
load_dotenv()
##################################################################################################################################
## CONFIGURACOES INICIAIS ########################################################################################################
st.set_page_config("FINANCES", layout="wide", page_icon="📊")
st.header("FINANCES")

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

##################################################################################################################################
## OBTER DADOS DE PLANILHAS ######################################################################################################
# @st.cache_data
# @st.cache_resource
def get_plans():
    plans = GoogleFinance()
    if plans is None:
        raise ValueError("plans retornou None")
    return plans

##################################################################################################################################
## FILTROS DE MES PARA BIG NUMBERS ###############################################################################################
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


##################################################################################################################################
## INSTANCIAR ####################################################################################################################
plans = get_plans()
dre = plans.dre_df_transformation()
if dre is None:
    raise ValueError("dre_df_transformation retornou None")
ativos = plans.ativos_df_transformation()
if ativos is None:
    raise ValueError("ativos_df_transformation retornou None")
luz = plans.luz_df_transformation()
if luz is None:
    raise ValueError("luz_df_transformation")
##################################################################################################################################
## GERAR DATAS ###################################################################################################################
dre_today = filter_latest_month(dre)
ativos_previous = filter_previous_month(ativos)
actual_month = pd.to_datetime("today").to_period("M").start_time
previous_month = actual_month + pd.DateOffset(months=-1)  # mes anterior
forward_month = actual_month + pd.DateOffset(months=1)  # mes posterior
twelve_month = actual_month + pd.DateOffset(months=-11)  # 12 meses para tras
thirth_month = actual_month + pd.DateOffset(months=-12)  # 13 meses para tras
fourth_month = actual_month + pd.DateOffset(months=-13)  # 14 meses para tras
fourth_month_forward = actual_month + pd.DateOffset(months=13)  # 14 meses para frente
today = pd.to_datetime("today").to_period("M").start_time.strftime("%Y-%m-%d")
today_year = pd.to_datetime("today").year
today_month = pd.to_datetime("today").month
##################################################################################################################################
## CORES #########################################################################################################################
color_green = "#07ED41"
color_green2 = "#39F969"
color_green3 = "#88FBA5"
color_red = "#ff5e5b"
stroke = 2.5

##################################################################################################################################
## BIG NUMBERS ###################################################################################################################
data, bn_receita, bn_despesa, bn_dif, bn_meta, bn_pb, bn_pl, bn_carro = st.columns(8)

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

with bn_meta:
    dre_today['% Meta'] = (dre_today["DESPESAS TOTAL"]/10000) 
    meta_formatted = "{:.0%}".format(dre_today['% Meta'].iloc[0])
    st.metric("% Meta", meta_formatted)

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

##################################################################################################################################
## GRAFICOS RECEITA, DESPESA E RESULTADO #########################################################################################
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
                    grid=False,
                    domain=True,
                    domainColor="gray",
                    labels=False,
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
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip("Valor_Formatado:N", title="R$ VALOR")
            ]
        )
        .properties(title="R$ RECEITAS x DESPESAS")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=-10,
        fontWeight="bold",
    ).encode(
        text=alt.condition(
            alt.datum.Categoria == "RECEITA TOTAL",
            alt.Text("Valor_Formatado:N"),
            alt.value(""),
        ),
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with econ:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["Valor_Formatado"] = dre_filtered["RESULTADO"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )
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
                    # ticks=True,
                    grid=False,
                    domain=True,
                    # tickColor="gray",
                    domainColor="gray",
                    labels=False,
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
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Valor_Formatado:N", title="R$ RESULTADO")
            ]
        )
        .properties(title="R$ RESULTADO")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr("datum.RESULTADO > 0 ? -10 : 10"),
        # color="#1e6091",
        fontWeight="bold",
        # fontSize=15,
    ).encode(text=alt.Text("Valor_Formatado:N"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with econ_perc:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["PERC_RESULTADO"] = (
        dre_filtered["RESULTADO"] / dre_filtered["RECEITA TOTAL"]
    )
    dre_filtered["Valor_Formatado"] = dre_filtered["PERC_RESULTADO"].apply(
        lambda x: f"{x:,.1%}".replace(".", ",")
    )
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
                    grid=False,
                    domain=True,
                    domainColor="gray",
                    labels=False,
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
        tooltip=[
            alt.Tooltip("MES_STR:N", title="MÊS"),
            alt.Tooltip("Valor_Formatado:N", title="% RESULTADO"), # Tooltip com o total
        ]
        )
        .properties(title="% RESULTADO")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr("datum.PERC_RESULTADO > 0 ? -10 : 10"),
        fontWeight="bold",
    ).encode(text=alt.Text("Valor_Formatado:N"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)


##################################################################################################################################
# GRAFICOS DESPESAS ##############################################################################################################
def gastos_barchart(
    df: pd.DataFrame, col_name: str, max_month, min_month, intervalo: str = "tras"):
    df["MES_ANO"] = df["MES"].dt.year
    df["MES_NUMERO"] = df["MES"].dt.month
    col = col_name
    if intervalo == "tras":
        dre_filtered = df[(dre["MES"] <= max_month) & (df["MES"] >= min_month)]
    else:
        dre_filtered = df[(dre["MES"] >= max_month) & (df["MES"] <= min_month)]
    
    dre_filtered[f"R$ {col}"] = dre_filtered[f"{col}"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )
    chart = (
        alt.Chart(dre_filtered)
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
                f"{col}:Q",
                title=None,
                axis=alt.Axis(
                    grid=False,
                    domain=True,
                    domainColor="gray",
                    labels=False,
                ),
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip(f"R$ {col}:N", title=f"{col}")
            ],
            color=alt.condition(
                            (alt.datum["MES_ANO"] == today_year) & (alt.datum["MES_NUMERO"] == today_month),
                            alt.value(f"{color_red}"),       
                            alt.value('#D57270')        
                        )
        )
        .properties(title=f"R$ {col}")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        color=f"{color_red}",
        fontWeight="bold",
    ).encode(text=alt.Text(f"R$ {col}:N"))
    chart = chart + text
    return chart


total_hm = st.container()

total_hm, gastos = st.columns([1, 2])

with total_hm:
    total = gastos_barchart(dre, "DESPESAS TOTAL", forward_month, thirth_month)
    rule = alt.Chart(dre).mark_rule().encode(strokeDash=alt.value([4, 2]), y=alt.datum(10000), color=alt.value("white"))
    total = total+rule
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
    df_long["Valor_formatado"] = df_long["Var_perc"].apply(
        lambda x: f"{x:,.1%}".replace(".", ",")
    )

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
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="CATEGORIA"),
                alt.Tooltip("Valor_formatado:N", title="% TOTAL")
            ]
        )
        .properties(title="% VARIAÇÃO MENSAL DOS GASTOS", height=350)
    )

    text = heatmap.mark_text(baseline="middle", fontWeight="bold").encode(
        text=alt.Text("Valor_formatado:N"),
        color=alt.condition(
            (alt.datum.Var_perc >= 0.4) | (alt.datum.Var_perc <= -0.4),
            alt.value("white"),
            alt.value("black"),
        ),
    )
    chart = heatmap + text
    st.altair_chart(chart, use_container_width=True)

with gastos:
    mercado, diversos, assinaturas = st.columns(3)
    with mercado:
        mercado = gastos_barchart(dre, "MERCADO", forward_month, thirth_month)
        st.altair_chart(mercado, use_container_width=True)

    with diversos:
        mercado = gastos_barchart(dre, "DIVERSOS", forward_month, thirth_month)
        st.altair_chart(mercado, use_container_width=True)

    with assinaturas:
        mercado = gastos_barchart(dre, "ASSINATURAS", forward_month, thirth_month)
        st.altair_chart(mercado, use_container_width=True)

    role, transporte, apartamento = st.columns(3)

    with role:
        mercado = gastos_barchart(dre, "ROLE", forward_month, thirth_month)
        st.altair_chart(mercado, use_container_width=True)

    with transporte:
        mercado = gastos_barchart(dre, "TRANSPORTE", forward_month, thirth_month)
        st.altair_chart(mercado, use_container_width=True)
    with apartamento:
        mercado = gastos_barchart(dre, "APARTAMENTO", forward_month, thirth_month)
        st.altair_chart(mercado, use_container_width=True)

##################################################################################################################################
## GRAFICOS DE PATRIMONIO  #######################################################################################################

patrimonio, dif_rs, investimentos_reserva = st.columns(3)

with patrimonio:
    ativos_filtered = ativos[
        (ativos["MES"] <= actual_month) & (ativos["MES"] >= thirth_month)
    ]
    ativos_filtered["Valor_formatado"] = ativos_filtered[
        "PATRIMONIO_BRUTO"
    ].apply(lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else "")
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
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "PATRIMONIO_BRUTO:Q",
                title=None,
                axis=alt.Axis(
                    # ticks=True,
                    grid=False,
                    domain=True,
                    # tickColor="gray",
                    domainColor="gray",
                    labels=False,
                ),
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Valor_formatado:N", title="R$ PATRIMÔNIO BRUTO")
            ]
        )
        .properties(title=f"R$ PATRIMÔNIO BRUTO")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        color="#00cecb",
        fontWeight="bold",
    ).encode(text=alt.Text("Valor_formatado:N"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with dif_rs:
    ativos_filtered = ativos[
        (ativos["MES"] <= actual_month) & (ativos["MES"] >= twelve_month)
    ]
    ativos_filtered["Valor_formatado"] = ativos_filtered[
        "DIF_PATRIMONIO"
    ].apply(lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else "")
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
                    ticks=False,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
            color=alt.Color(
                "color_value:O",
                scale=alt.Scale(
                    domain=[0, 1],
                    range=[f"{color_red}", "#00cecb"],
                    ),
                legend=None           
            ),
            tooltip=[
            alt.Tooltip("MES_STR:N", title="MÊS"),
            alt.Tooltip("Valor_formatado:N", title="R$ RESULTADO")
        ]
        )
        .properties(title="R$ RESULTADO PATRIMONIAL BRUTO")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr("datum.DIF_PATRIMONIO > 0 ? -10 : 10"),
        fontWeight="bold",
    ).encode(text=alt.Text("Valor_formatado:N"),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Valor_Formatado:N", title="R$ RESULTADO")
            ])
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with investimentos_reserva:
    # Formatação dos valores em texto formatado
    ativos_filtered["INVESTIMENTO_FORMATADO"] = ativos_filtered[
        "INVESTIMENTO"
    ].apply(lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else "")
    ativos_filtered["RESERVAS_FORMATADO"] = ativos_filtered[
        "RESERVAS"
    ].apply(lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else "")

    # Combinação das colunas formatadas para exibição dinâmica com Altair
    ativos_filtered = ativos_filtered.melt(
        id_vars=["MES_STR", "INVESTIMENTO_FORMATADO", "RESERVAS_FORMATADO"],
        value_vars=["INVESTIMENTO", "RESERVAS"],
        var_name="Categoria",
        value_name="Valor"
    )
    ativos_filtered["Valor_Formatado"] = ativos_filtered.apply(
        lambda row: row["INVESTIMENTO_FORMATADO"] if row["Categoria"] == "INVESTIMENTO" else row["RESERVAS_FORMATADO"],
        axis=1
    )

    # Gráfico principal com linhas
    chart = (
        alt.Chart(ativos_filtered)
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
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    ticks=False,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["INVESTIMENTO", "RESERVAS"],
                    range=["#1dd3b0", "#086375"],
                ),
                legend=alt.Legend(direction='vertical', columns=1, title=None, orient='none', legendX=0, legendY=-10),
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip("Valor_Formatado:N", title="VALOR")
            ]
        )
        .properties(title="R$ INVESTIMENTOS x RESERVAS")
    )

    # Adicionar o texto formatado acima ou abaixo da linha
    text = (
        alt.Chart(ativos_filtered)
        .mark_text(dy=alt.ExprRef("datum.Categoria === 'RESERVAS' ? -10 : 10"), fontWeight="bold",)
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y=alt.Y("Valor:Q"),
            text=alt.Text("Valor_Formatado:N"),
            color=alt.Color("Categoria:N", scale=alt.Scale(domain=["INVESTIMENTO", "RESERVAS"], range=["#1dd3b0", "#086375"])),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip("Valor_Formatado:N", title="VALOR")
            ]
        )
    )

    # Combinar o gráfico principal com os rótulos de texto
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)


##################################################################################################################################
## GRAFICOS DA CONTA DE LUZ  #####################################################################################################
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
                    labelAngle=0,
                    labels=False
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    ticks=False,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labels=False
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
        .properties(title="R$ FATURA")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        color=f"{color_red}",
        fontWeight="bold",
    ).encode(
        text=alt.Text("Valor:Q", format=",.0f"),
        color=alt.condition(
            alt.datum.Categoria == "FATURA DA CONTA DE LUZ",
            alt.value("#fd3e81"),
            alt.value("#adb5bd"),
        ),
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with luz_kwh:
    luz_filtered = luz[luz["MES"] >= twelve_month]
    luz_filtered["KWH DIA_FORMATADO"] = luz_filtered[
        "KWH DIA"
    ].apply(lambda x: f"{x:,.1f}".replace(".", ",") if pd.notnull(x) else "")
    luz_filtered["KWH DIA_PREVISTO_FORMATADO"] = luz_filtered[
        "KWH_DIA_PREVISTO"
    ].apply(lambda x: f"{x:,.1f}".replace(".", ",") if pd.notnull(x) else "")

    luz_filtered = luz_filtered.melt(
        id_vars=["MES_STR", "KWH DIA_FORMATADO", "KWH DIA_PREVISTO_FORMATADO"],
        value_vars=["KWH DIA", "KWH_DIA_PREVISTO"],
        var_name="Categoria",
        value_name="Valor"
    )
    luz_filtered["Valor_Formatado"] = luz_filtered.apply(
        lambda row: row["KWH DIA_FORMATADO"] if row["Categoria"] == "KWH DIA" else row["KWH DIA_PREVISTO_FORMATADO"],
        axis=1
    )

    chart = (
        alt.Chart(luz_filtered)
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
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    ticks=False,
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["KWH DIA", "KWH_DIA_PREVISTO"],
                    range=["#fd3e81", "#adb5bd"],
                ),
            legend=None
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip("Valor_Formatado:N", title="VALOR")
            ]
        )
        .properties(title="KWH CONSUMO DIÁRIO")
    )

    text = (
        alt.Chart(luz_filtered)
        .mark_text(dy=-10, fontWeight="bold",)
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y=alt.Y("Valor:Q"),
            text=alt.Text("Valor_Formatado:N"),
            color=alt.Color("Categoria:N", scale=alt.Scale(domain=["KWH DIA", "KWH DIA_PREVISTO"], range=["#fd3e81", "#adb5bd"])),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip("Valor_Formatado:N", title="VALOR")
            ]
        )
    )

    chart = chart + text
    st.altair_chart(chart, use_container_width=True)


with preco_kwh:
    luz_filtered = luz[(luz["MES"] <= actual_month) & (luz["MES"] >= twelve_month)]
    luz_filtered["PRECO KWH_FORMATADO"] = luz_filtered[
        "PRECO KWH"
    ].apply(lambda x: f"{x:,.2f}".replace(".", ",") if pd.notnull(x) else "")
    chart = (
        alt.Chart(luz_filtered)
        .mark_line(color="#fd3e81")
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
                "PRECO KWH:Q",
                title=None,
                axis=alt.Axis(
                    grid=False,
                    domain=True,
                    tickColor="gray",
                    domainColor="gray",
                    labels=False
                ),
            ),
        )
        .properties(title="R$ CUSTO KWH")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=-10,
        color="#fd3e81",
        fontWeight="bold",
        # fontSize=15,
    ).encode(
        text=alt.Text("PRECO KWH_FORMATADO:N"),
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

##################################################################################################################################
##################################################################################################################################
################################################ ANALISES AVANÇADAS ##############################################################
##################################################################################################################################
##################################################################################################################################

st.divider()
st.subheader("ANÁLISES AVANÇADAS")
##################################################################################################################################
## RECEITAS ###################################################################################################################

salario, dividendos, outros = st.columns(3)

with salario:
    dre['SALARIO_12'] = dre['SALARIO'].rolling(window=12, min_periods=1).sum()
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["Valor_formatado"] = dre_filtered["SALARIO_12"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )

    chart = (
        alt.Chart(dre_filtered)
        .mark_line(strokeWidth=stroke, color=f"{color_green}")
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
                "SALARIO_12:Q",
                title=None,
                axis=alt.Axis(
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ),
        )
        .properties(title="R$ SALÁRIO ACUMULADO 12 MESES")
    )
    text = (
        alt.Chart(dre_filtered)
        .mark_text(
            align="center",
            baseline="middle",
            dy=-10,
            color=f"{color_green}",
            fontWeight='bold'
        )
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y="SALARIO_12:Q",
            text=alt.Text(
                "Valor_formatado:N"
            ),
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with dividendos:
    dre['DIVIDENDOS_12'] = dre['DIVIDENDOS'].rolling(window=12, min_periods=1).sum()
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["Valor_formatado"] = dre_filtered["DIVIDENDOS_12"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )

    chart = (
        alt.Chart(dre_filtered)
        .mark_line(strokeWidth=stroke, color=f"{color_green2}")
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
                "DIVIDENDOS_12:Q",
                title=None,
                axis=alt.Axis(
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ),
        )
        .properties(title="R$ DIVIDENDOS ACUMULADOS 12 MESES")
    )
    text = (
        alt.Chart(dre_filtered)
        .mark_text(
            align="center",
            baseline="middle",
            dy=-10,
            color=f"{color_green2}",
            fontWeight='bold'
        )
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y="DIVIDENDOS_12:Q",
            text=alt.Text(
                "Valor_formatado:N"
            ),
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with outros:
    dre['OUTROS_12'] = dre['OUTROS'].rolling(window=12, min_periods=1).sum()
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["Valor_formatado"] = dre_filtered["OUTROS_12"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )

    chart = (
        alt.Chart(dre_filtered)
        .mark_line(strokeWidth=stroke, color=f"{color_green3}")
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
                "OUTROS_12:Q",
                title=None,
                axis=alt.Axis(
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ),
        )
        .properties(title="R$ OUTROS ACUMULADOS 12 MESES")
    )
    text = (
        alt.Chart(dre_filtered)
        .mark_text(
            align="center",
            baseline="middle",
            dy=-10,
            color=f"{color_green3}",
            fontWeight='bold'
        )
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y="OUTROS_12:Q",
            text=alt.Text(
                "Valor_formatado:N"
            ),
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

## GASTOS FUTUROS ################################################################################################################
gastos_futuros = st.container()
gastos_futuros, endividamento = st.columns(2)

with gastos_futuros:
    total_futuro = gastos_barchart(
        dre, "DESPESAS TOTAL", forward_month, fourth_month_forward, "frente"
    )
    st.altair_chart(total_futuro, use_container_width=True)

    
    dre_filtered = dre[
        (dre["MES"] >= forward_month) & (dre["MES"] <= fourth_month_forward)
    ]
    df_long = dre_filtered.melt(
        id_vars=["MES", "MES_STR"],
        value_vars=[
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
    df_long["Total_Mensal"] = df_long.groupby("MES")["Valor"].transform("sum")
    df_long["Proporcao"] = df_long["Valor"] / df_long["Total_Mensal"]
    chart = (
        alt.Chart(df_long)
        .mark_bar()
        .transform_filter(alt.datum.Proporcao > 0)
        .encode(
            y=alt.Y(
                "Proporcao:Q",
                title=None,
                axis=alt.Axis(
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ).stack("normalize"),
            x=alt.X(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
                axis=alt.Axis(grid=False, domain=True, domainColor="gray", labelAngle=0),
            ),
            color=alt.Color(
                field="Categoria",
                type="nominal",
                sort=alt.SortField(field="Proporcao:Q", order="descending"),
                scale=alt.Scale(
                    domain=[
                        "MERCADO",
                        "DIVERSOS",
                        "ASSINATURAS",
                        "ROLE",
                        "TRANSPORTE",
                        "APARTAMENTO",
                    ],
                    range=[
                        "#e85d04",
                        "#1982c4",
                        "#ae8853",
                        "#666666",
                        "#3fae2a",
                        "#9d4edd",
                    ],
                ),
                legend=alt.Legend(
                    orient="none",
                    direction="horizontal",
                    title=None,
                    legendX=400,
                    legendY=-50,
                ),
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title='MÊS'),
                alt.Tooltip("Categoria:N", title='Categoria'),
                alt.Tooltip("Proporcao:Q", format=".0%", title='% VALOR')
            ],
            order=alt.Order("Categoria:N"),
        )
        .properties(title="% DISTRIBUIÇÃO DOS GASTOS FUTUROS", height=350)
    )
    text = (
        alt.Chart(df_long)
        .mark_text(
            align="center",
            baseline="middle",
            fontWeight="bold",
            color="white",
            dy=10,
        )
        .transform_filter(alt.datum.Proporcao > 0)
        .encode(
            y=alt.Y("sum(Valor):Q").stack(
                "normalize"
            ),
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            detail="Categoria:N",
            text=alt.Text("Proporcao:Q", format=".0%"),
            order=alt.Order("Categoria:N"),
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with endividamento:
    dre["% RENDA"] = dre["DESPESAS TOTAL"] / dre["RECEITA TOTAL"]
    chart = (
        alt.Chart(dre)
        .mark_line(strokeWidth=stroke, color=color_red)
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
                "% RENDA:Q",
                title=None,
                axis=alt.Axis(grid=False, domain=True, domainColor="gray", labels=False),
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title='MÊS'),
                alt.Tooltip("% RENDA:Q", format=".0%", title='% RENDA')
            ],
        )
        .properties(title="% ENDIVIDAMENTO")
    )
    text = (
        alt.Chart(dre)
        .mark_text(
            align="center",
            baseline="middle",
            dy=-10,  
            color=color_red,
            fontWeight='bold'
        )
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y="% RENDA:Q",
            text=alt.Text(
                "% RENDA:Q", format=".0%"
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title='MÊS'),
                alt.Tooltip("% RENDA:Q", format=".0%", title='% RENDA')
            ], 
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)
    
##################################################################################################################################
## CRESCIMENTO ###################################################################################################################
ativos_filtered = ativos[ativos["MES"] >= pd.to_datetime("2023-09-01")]

curva_bruto, curva_liquido, usd = st.columns(3)

with curva_bruto:
    zero = (
        alt.Chart(ativos_filtered)
        .mark_rule()
        .encode(
            y=alt.datum(0),
            size=alt.value(1),
            color=alt.value("white"),
            strokeDash=alt.value([4, 2]),
        )
    )
    chart = (
        alt.Chart(ativos_filtered)
        .transform_fold(
            ["CURVA BRUTO", "CURVA LIQUIDO", "CURVA INFLACAO", "CURVA JUROS"],
            as_=["Categoria", "Valor"],
        )
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
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["CURVA BRUTO", "CURVA INFLACAO", "CURVA JUROS"],
                    range=["#00cecb", "#fb8500", "#fff3b0"],
                ),
                legend=alt.Legend(
                    direction="vertical",
                    columns=1,
                    title=None,
                    orient="none",
                    legendX=0,
                    legendY=-10,
                ),
            ),
        )
        .properties(title="CURVA PATRIMÔNIO BRUTO x IPCA x SELIC")
    )
    chart = chart + zero
    st.altair_chart(chart, use_container_width=True)

with curva_liquido:
    chart = (
        alt.Chart(ativos_filtered)
        .transform_fold(
            ["CURVA LIQUIDO", "CURVA INFLACAO", "CURVA JUROS"],
            as_=["Categoria", "Valor"],
        )
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
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["CURVA LIQUIDO", "CURVA INFLACAO", "CURVA JUROS"],
                    range=["#00cecb", "#fb8500", "#fff3b0"],
                ),
                legend=alt.Legend(
                    direction="vertical",
                    columns=1,
                    title=None,
                    orient="none",
                    legendX=0,
                    legendY=-10,
                ),
            ),
        )
        .properties(title="CURVA PATRIMÔNIO LÍQUIDO x IPCA x SELIC")
    )
    chart = chart + zero
    st.altair_chart(chart, use_container_width=True)

with usd:
    ativos_filtered["usd_share"] = (
        ativos_filtered["WISE"] + ativos_filtered["AVENUE"]
    ) / ativos_filtered["PATRIMONIO_LIQUIDO"]
    ativos_filtered["Valor_formatado"] = ativos_filtered["usd_share"].apply(
        lambda x: f"{x:,.1%}".replace(".", ",")
    )
    chart = (
        alt.Chart(ativos_filtered)
        .mark_line(strokeWidth=stroke, color="#00cecb")
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
                "usd_share:Q",
                title=None,
                axis=alt.Axis(
                    grid=False, domain=True, domainColor="gray", labels=False
                ),
            ),
        )
        .properties(title="% PATRIMÔNIO LÍQUIDO EM USD")
    )
    text = (
        alt.Chart(ativos_filtered)
        .mark_text(
            align="center",
            baseline="middle",
            dy=-10,
            color="#00cecb",
            fontWeight="bold",
        )
        .encode(
            x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
            y="usd_share:Q",
            text=alt.Text(
                "Valor_formatado:N"
            ),  # Formata como percentual com uma casa decimal
        )
    )
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)


dre_filtered = dre[(dre["MES"] <= forward_month) & (dre["MES"] >= thirth_month)]
df_long = dre_filtered.melt(
    id_vars=["MES", "MES_STR"],
    value_vars=[
        "DESPESAS LUCAS",
        "DESPESAS JESSICA",
    ],
    var_name="Categoria",
    value_name="Valor",
)
df_long["Total_Mensal"] = df_long.groupby("MES")["Valor"].transform("sum")
df_long["Proporcao"] = df_long["Valor"] / df_long["Total_Mensal"]
chart = (
    alt.Chart(df_long)
    .mark_bar()
    .transform_filter(alt.datum.Proporcao > 0)
    .encode(
        y=alt.Y(
            "Proporcao:Q",
            title=None,
            axis=alt.Axis(
                grid=False, domain=True, domainColor="gray", labels=False
            ),
        ).stack("normalize"),
        x=alt.X(
            "MES_STR:N",
            title=None,
            sort=alt.SortField(field="date", order="ascending"),
            axis=alt.Axis(grid=False, domain=True, domainColor="gray", labelAngle=0),
        ),
        color=alt.Color(
            field="Categoria",
            type="nominal",
            sort=alt.SortField(field="Proporcao:Q", order="descending"),
            scale=alt.Scale(
                domain=[
                    "DESPESAS JESSICA",
                    "DESPESAS LUCAS",
                ],
                range=[
                    "#ff69eb",
                    "#49b6ff",
                ],
            ),
            legend=alt.Legend(
                orient="none",
                direction="horizontal",
                title=None,
                legendX=400,
                legendY=-50,
            ),
        ),
        tooltip=[
            alt.Tooltip("MES_STR:N", title='MÊS'),
            alt.Tooltip("Categoria:N", title='Categoria'),
            alt.Tooltip("Proporcao:Q", format=".0%", title='% VALOR')
        ],
        order=alt.Order("Categoria:N"),
    )
    .properties(title="% PROPORÇÃO DOS GASTOS", height=350)
)
text = (
    alt.Chart(df_long)
    .mark_text(
        align="center",
        baseline="middle",
        fontWeight="bold",
        color="white",
        dy=10,
    )
    .transform_filter(alt.datum.Proporcao > 0)
    .encode(
        y=alt.Y("sum(Valor):Q").stack(
            "normalize"
        ),
        x=alt.X("MES_STR:N", sort=alt.SortField(field="date", order="ascending")),
        detail="Categoria:N",
        text=alt.Text("Proporcao:Q", format=".0%"),
        order=alt.Order("Categoria:N"),
    )
)
chart = chart + text
st.altair_chart(chart, use_container_width=True)

consumo_kwh, preco_kwh = st.columns(2)

with consumo_kwh:
    chart = (
        alt.Chart(luz)
        .mark_line(color="#fd3e81")
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
                "KWH DIA:Q",
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
        .properties(title="CONSUMO KWH HISTÓRICO")
    )
    st.altair_chart(chart, use_container_width=True)

with preco_kwh:
    chart = (
        alt.Chart(luz)
        .mark_line(color="#fd3e81")
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
        .properties(title="CUSTO KWH HISTÓRICO")
    )
    st.altair_chart(chart, use_container_width=True)
