import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import locale
from datetime import datetime as dt
import altair as alt
import pandas as pd
import streamlit as st

from src.get_data import GoogleFinance
from src.luz import make_luz

st.set_page_config("FINANCES", layout="wide", page_icon="📊")
st.header("FINANCES")

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

sheet_dict = {
    "DRE TT": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=885613319#gid=885613319",
    "Ativos": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=2055342803#gid=2055342803",
    "Luz": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=1179918927#gid=1179918927",
    "Credit Card": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=1853911625#gid=1853911625",
}

# @st.cache_data
# @st.cache_resource
def get_plans():
    plans = GoogleFinance(sheet_dict=sheet_dict)
    return plans

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

# INSTANCIAR
plans = get_plans()
dre = plans.dre_df_transformation()
ativos = plans.ativos_df_transformation()
cartao = plans.cartao_df_transformation()

# GERAR DATAS
dre_today = filter_latest_month(dre)
print(dre_today)
ativos_previous = filter_previous_month(ativos)
actual_month = pd.to_datetime("today").to_period("M").start_time
twelve_month = actual_month + pd.DateOffset(months=-11)
thirth_month = actual_month + pd.DateOffset(months=-12)

# CORES
#color_green = '#386150'
color_green = '#39FF14'
#color_red = '#FF4365'
color_red = '#FC440F'

# BIG NUMBERS
data, bn_receita, bn_despesa, bn_dif, bn_pb, bn_pl = st.columns(6)

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
    patri_total = float(ativos_previous["PATRIMONIO BRUTO"])
    patri_total = locale.currency(patri_total, grouping=True)
    patri_total = patri_total.split(",")[0]
    st.metric("Patrimônio Bruto", patri_total)

with bn_pl:
    patri_liq = float(ativos_previous["PATRIMONIO LIQUIDO"])
    patri_liq = locale.currency(patri_liq, grouping=True)
    patri_liq = patri_liq.split(",")[0]
    st.metric("Patrimônio Líquido", patri_liq)

# GRAFICOS RECEITA, DESPESA E RESULTADO
rec_desp, econ, econ_perc = st.columns(3)

with rec_desp:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    chart = (
        alt.Chart(dre_filtered)
        .transform_fold(["RECEITA TOTAL", "DESPESAS TOTAL"], as_=["Categoria", "Valor"])
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
                    format=",.0f"
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
    st.altair_chart(chart, use_container_width=True)

with econ:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
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
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "RESULTADO:Q",
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
        #color="#1e6091",
        fontWeight="bold",
        #fontSize=15,
    ).encode(text=alt.Text("RESULTADO:Q", format=",.0f"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)

with econ_perc:
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    dre_filtered["PERC_RESULTADO"] = (
        dre_filtered["RESULTADO"] / dre_filtered["RECEITA TOTAL"]
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
                    labelAngle=0
                ),
            ),
            y=alt.Y(
                "PERC_RESULTADO:Q",
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
    ).encode(text=alt.Text("PERC_RESULTADO:Q", format=",.1%"))
    chart = chart + text
    st.altair_chart(chart, use_container_width=True)


gastos_hm, gastos = st.columns(2)

with gastos_hm:
    # Filtrar o DataFrame até o mês atual
    df_long = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= thirth_month)]

    # Reformatar o DataFrame para ter as categorias e valores em formato longo
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
    # Calcular a variação percentual mês a mês por categoria
    df_long["Var_perc"] = df_long.groupby(["Categoria"])["Valor"].pct_change()

    col_order = ['DESPESAS TOTAL','MERCADO','DIVERSOS','ASSINATURAS','ROLE','TRANSPORTE','APARTAMENTO']
    
    # Criar o heatmap com Altair
    heatmap = (
        alt.Chart(df_long)
        .mark_rect()
        .encode(
            x=alt.X(
                "Categoria:N", title=None,sort=col_order ,axis=alt.Axis(orient="top", labelAngle=0, labelAlign='center')
            ),
            y=alt.Y(
                "MES_STR:N",
                title=None,
                sort=alt.SortField(field="date", order="ascending"),
            ),
            color=alt.Color(
                "Var_perc:Q",
                scale=alt.Scale(
                    scheme='redyellowgreen', reverse=True, domain=[-0.5, 0.5], clamp=True
                ),
                title=None,
                legend=None,
            ),
            tooltip=["MES_STR:N", "Categoria:N", "Var_perc:Q"],
        )
        .properties(title="% VARIAÇÃO MENSAL", height=600)
    )
    # Adicionar os valores percentuais como texto no heatmap
    text = heatmap.mark_text(baseline="middle").encode(
        text=alt.Text("Var_perc:Q", format=",.1%"), color=alt.condition(
            (alt.datum.Var_perc >= 40) | (alt.datum.Var_perc <= -40),  # Se a variação for positiva
            alt.value("white"),      # Texto preto
            alt.value("black"),
        fontWeight="bold"
        )
    )
    # Combinar o heatmap e o texto
    chart = heatmap + text
    st.altair_chart(chart, use_container_width=True)

# def gastos_barchart(df: pd.DataFrame, col_name: str):
#     col = col_name
#     dre_filtered = df[df["MES"] <= actual_month + pd.DateOffset(months=1)]  # Ajustando o filtro do DataFrame
#     chart = (
#         alt.Chart(dre_filtered)
#         .mark_bar()
#         .encode(
#             x=alt.X(
#                 "MES_STR:N",
#                 title=None,
#                 sort=alt.SortField(field="date", order="ascending"),
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#             y=alt.Y(
#                 f"{col}:Q",
#                 title=None,
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#         )
#         .properties(title=f"GASTOS {col}")
#     )

#     # Adicionar texto ao gráfico (valores das barras)
#     text = chart.mark_text(
#         align="center",
#         baseline="middle",
#         dy=10,
#         color="red",
#         fontWeight="bold",
#         fontSize=15,
#     ).encode(text=alt.Text(f"{col}:Q", format=",.0f"))
    
#     # Combinar o gráfico com o texto
#     chart = chart + text
#     #st.altair_chart(chart, use_container_width=True)
#     return chart

# with gastos:
#     mercado, diversos, assinaturas = st.columns(3)
#     with mercado:
#         mercado = gastos_barchart(dre,'MERCADO')
#         st.altair_chart(mercado, use_container_width=True)
        
    
#     with diversos:
#         mercado = gastos_barchart(dre,'DIVERSOS')
#         st.altair_chart(mercado, use_container_width=True)
        
#     with assinaturas:
#         mercado = gastos_barchart(dre,'ASSINATURAS')
#         st.altair_chart(mercado, use_container_width=True)
    
#     role, transporte, apartamento = st.columns(3)
    
#     with role:
#         mercado = gastos_barchart(dre,'ROLE')
#         st.altair_chart(mercado, use_container_width=True)
        
#     with transporte:
#         mercado = gastos_barchart(dre,'TRANSPORTE')
#         st.altair_chart(mercado, use_container_width=True)
#     with apartamento:
#         mercado = gastos_barchart(dre,'APARTAMENTO')
#         st.altair_chart(mercado, use_container_width=True)

# patrimonio, investimentos, reserva, dif_rs = st.columns(4)

# with patrimonio:
#     ativos_filtered = ativos[ativos["MES"] <= actual_month]
#     chart = (
#         alt.Chart(ativos_filtered)
#         .transform_fold(["CARRO", "PATRIMONIO LIQUIDO"], as_=["Categoria", "Valor"])
#         .mark_bar()
#         .encode(
#             x=alt.X(
#                 "MES_STR:N",
#                 title=None,
#                 sort=alt.SortField(field="date", order="ascending"),
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#             y=alt.Y(
#                 "Valor:Q",
#                 title=None,
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#             color=alt.Color(
#                 "Categoria:N",
#                 scale=alt.Scale(
#                     domain=["CARRO", "PATRIMONIO LIQUIDO"],
#                     range=["#38b000", "#da2c38"],
#                 ),
#                 legend=None,
#             ),
#         )
#         .properties(title="PATRIMÔNIO")
#     )
#     st.altair_chart(chart, use_container_width=True)

# def ativos_charts(df: pd.DataFrame, col_name: str):
#     col = col_name
#     ativos_filtered = df[df["MES"] <= actual_month]
#     chart = (
#         alt.Chart(ativos_filtered)
#         .mark_line()
#         .encode(
#             x=alt.X(
#                 "MES_STR:N",
#                 title=None,
#                 sort=alt.SortField(field="date", order="ascending"),
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#             y=alt.Y(
#                 f"{col}:Q",
#                 title=None,
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#         )
#         .properties(title=f"{col}")
#     )
#     return chart

# with investimentos:
#     invest = ativos_charts(ativos,'INVESTIMENTO')
#     st.altair_chart(invest, use_container_width=True)  
    
# with reserva:
#     rsv = ativos_charts(ativos, 'RESERVAS')
#     st.altair_chart(rsv, use_container_width=True)  
    
# with dif_rs:
#     dif = ativos_charts(ativos, 'DIF PATRIMONIO')
#     st.altair_chart(dif, use_container_width=True)
        

# bradesco, nuinvest, avenue, wise, daycoval = st.columns(5)

# with bradesco:
#     brad = ativos_charts(ativos,'BRADESCO')
#     st.altair_chart(brad, use_container_width=True)  

# with nuinvest: 
#     nu = ativos_charts(ativos,'NUIVEST LUCAS')
#     st.altair_chart(nu, use_container_width=True)  
    
# with avenue:
#     av = ativos_charts(ativos,'AVENUE')
#     st.altair_chart(av, use_container_width=True) 

# with wise:
#     ws = ativos_charts(ativos,'WISE')
#     st.altair_chart(ws, use_container_width=True)

# with daycoval:
#     day = ativos_charts(ativos,'DAYCOVAL')
#     st.altair_chart(day, use_container_width=True)
    
    
# bancobrasil, sofisa, iti, nubank, nuinvest2 = st.columns(5)

# with bancobrasil:
#     bb = ativos_charts(ativos,'BANCO BRASIL')
#     st.altair_chart(bb, use_container_width=True)
    
# with sofisa:
#     sf = ativos_charts(ativos,'SOFISA')
#     st.altair_chart(sf, use_container_width=True)

# with iti:
#     it = ativos_charts(ativos,'ITI')
#     st.altair_chart(it, use_container_width=True)

# with nubank:
#     nub = ativos_charts(ativos,'NUBANK')
#     st.altair_chart(nub, use_container_width=True)

# with nuinvest2:
#     nu2 = ativos_charts(ativos,'NUINVEST JESSICA')
#     st.altair_chart(nu2, use_container_width=True)

# cresc_real, cresc_real_acum = st.columns(2)

# with cresc_real:
#     cr = ativos_charts(ativos,'% CRESCIMENTO REAL')
#     st.altair_chart(cr, use_container_width=True)

# with cresc_real_acum:
#     crum = ativos_charts(ativos,'% CRESCIMENTO REAL')
#     st.altair_chart(crum, use_container_width=True)

# luzes,cc = st.columns(2)

# with luzes:
#     luz = make_luz(sheet_dict)
#     luz["MES_STR"] = luz["MES"].dt.strftime("%b/%y")
    
#     luz_filtered = luz[luz["MES"] <= actual_month]
#     chart = (
#         alt.Chart(luz_filtered)
#         .transform_fold(["FATURA", "FATURA_PREVISTA"], as_=["Categoria", "Valor"])
#         .mark_bar()
#         .encode(
#             x=alt.X(
#                 "MES_STR:N",
#                 title=None,
#                 sort=alt.SortField(field="date", order="ascending"),
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#             y=alt.Y(
#                 "Valor:Q",
#                 title=None,
#                 axis=alt.Axis(
#                     ticks=True,
#                     grid=False,
#                     domain=True,
#                     tickColor="gray",
#                     domainColor="gray",
#                 ),
#             ),
#             color=alt.Color(
#                 "Categoria:N",
#                 scale=alt.Scale(
#                     domain=["FATURA", "FATURA_PREVISTA"],
#                     range=["#38b000", "#da2c38"],
#                 ),
#                 legend=None,
#             ),
#         )
#         .properties(title="LUZ")
#     )
#     st.altair_chart(chart, use_container_width=True)
    
# with cc:
#     card = make
