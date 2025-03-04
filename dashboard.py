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
verde_escuro = "#07ED41"
verde_medio = "#39F969"
verde_claro = "#88FBA5"
vermelho_medio = "#ff5e5b"
vermelho_claro = "#D57270"
azul_medio = "#00cecb"
azul_claro = "#5cfffc"
azul_escuro = "#007a78"
rosa = "#fd3e81"
stroke = 2.5

##################################################################################################################################
## FUNCOES DE GRAFICOS ###########################################################################################################
def barchart_variacao(
    df: pd.DataFrame, col_name: str, max_month, min_month, cor1: str, cor2: str = None, intervalo: str = "tras", numero:str = 'normal', title: str = None):
    """
    df: Algum dataframe
    col_name: Coluna numérica para analisar
    max_month: Máximo mês no final
    min_month: Mínimo mês no final
    intervalo: Passado ou Futuro
    cor1: Cor positiva
    cor2: Cor negativa
    """  
    col = col_name
    cor_1 = cor1
    cor_2 = cor2
    if intervalo == "tras":
        df_filtered = df[(df["MES"] <= max_month) & (df["MES"] >= min_month)]
    else:
        df_filtered = df[(df["MES"] >= max_month) & (df["MES"] <= min_month)]
    if numero == 'normal':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.0f}".replace(",", ".")
        )
    elif numero == 'porcentagem':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.1%}".replace(".", ",")
        )
    elif numero == 'decimal':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.1f}".replace(".", ",")
        )

    chart = (
        alt.Chart(df_filtered)
        .transform_calculate(color_value=f"if(datum.{col} < 0, 0, 1)")
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
            color=alt.Color(
                "color_value:O",
                scale=alt.Scale(
                    domain=[0, 1],
                    range=[f"{cor_2}", f"{cor_1}"],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Valor_formatado:N", title=f"R$ {col}")
            ]
        )
        .properties(title=f"{title}")
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=alt.expr(f"datum.{col} > 0 ? -10 : 10"),
        fontWeight="bold",
    ).encode(text=alt.Text("Valor_formatado:N"))
    chart = chart + text
    return chart

def barchart_simples(
    df: pd.DataFrame, col_name: str, max_month, min_month, cor1: str, cor2: str = None, intervalo: str = "tras", title:str = None):
    """
    df: Algum dataframe
    col_name: Coluna numérica para analisar
    max_month: Máximo mês no final
    min_month: Mínimo mês no final
    intervalo: Passado ou Futuro
    cor1: Cor em destaque
    cor2: Cor secundária
    """
    df["MES_ANO"] = df["MES"].dt.year
    df["MES_NUMERO"] = df["MES"].dt.month
    col = col_name
    cor_1 = cor1
    cor_2 = cor2
    if intervalo == "tras":
        df_filtered = df[(df["MES"] <= max_month) & (df["MES"] >= min_month)]
    else:
        df_filtered = df[(df["MES"] >= max_month) & (df["MES"] <= min_month)]
    
    df_filtered[f"Valor_formatado"] = df_filtered[f"{col}"].apply(
        lambda x: f"{x:,.0f}".replace(",", ".")
    )
    chart = (
        alt.Chart(df_filtered)
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
                alt.Tooltip("Valor_formatado:N", title=f"{col}")
            ],
            color=alt.condition(
                            (alt.datum["MES_ANO"] == today_year) & (alt.datum["MES_NUMERO"] == today_month),
                            alt.value(f"{cor_1}"),       
                            alt.value(f"{cor_2}")        
                        )
        )
        .properties(title=f"{title}")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=0,
        fontWeight="bold",
    ).encode(text=alt.Text(f"Valor_formatado:N"))
    chart = chart + text
    return chart

def linha_dupla(
    df: pd.DataFrame, cols_name: list, max_month, min_month, cor1: str, cor2: str = None, intervalo: str = "tras", title:str = None, rotulo: str ='ambos'
    ):    
    df_filtered = df[(df["MES"] <= max_month) & (df["MES"] >= min_month)]
    for col in cols_name:
        df_filtered[f"{col}_formatado"] = df_filtered[col].apply(
            lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else ""
        )
    chart = (
        alt.Chart(df_filtered)
        .transform_fold(cols_name, as_=["Categoria", "Valor"])
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
                    domain=cols_name,
                    range=[f"{cor1}", f"{cor2}"],
                ),
                legend=alt.Legend(
                    direction="vertical",
                    columns=1,
                    title=None,
                    orient="none",
                    legendX=0,
                    legendY=-10,
                )
                if rotulo == "ambos"  # Mostrar legenda se 'ambos'
                else None,  # Ocultar legenda
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip(f"{col}_formatado:N", title="R$ VALOR")
            ]
        )
        .properties(title=title)
    )
    text = chart.mark_text(
        align="center",
        baseline="middle",
        dy=-10,
        fontWeight="bold",
    ).encode(
        text=alt.condition(
            "true" if rotulo == "ambos" else f"datum.Categoria == '{cols_name[0]}'",
            alt.Text(
                "Valor:Q" if rotulo == "ambos" else f"{cols_name[0]}_formatado:N"
                ),
            alt.value(""),
        ),
    )
    chart = chart + text
    return chart

def linha_simples(
    df: pd.DataFrame, col_name: str, max_month, min_month, cor1: str, intervalo: str = "tras",numero:str = 'normal', title:str = None):
    """
    df: Algum dataframe
    col_name: Coluna numérica para analisar
    max_month: Máximo mês no final
    min_month: Mínimo mês no final
    intervalo: Passado ou Futuro
    cor1: Cor em destaque
    cor2: Cor secundária
    """
    col = col_name
    cor_1 = cor1
    if max_month is not None and min_month is not None:
        if intervalo == "tras":
            df_filtered = df[(df["MES"] <= max_month) & (df["MES"] >= min_month)]
        elif intervalo == "frente":
            df_filtered = df[(df["MES"] >= max_month) & (df["MES"] <= min_month)]
    else:
        # Caso max_month e min_month sejam None, usa o DataFrame completo
        df_filtered = df
    
    if numero == 'normal':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.0f}".replace(",", ".")
        )
    elif numero == 'porcentagem':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.1%}".replace(".", ",")
        )
    elif numero == 'decimal':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.2f}".replace(".", ",")
        )
    chart = (
        alt.Chart(df_filtered)
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
                alt.Tooltip("Valor_formatado:N", title=f"{col}")
            ],
            color=alt.value(f"{cor_1}"),
        )
        .properties(title=f"{title}")
    )
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=-10,
        fontWeight="bold",
    ).encode(text=alt.Text(f"Valor_formatado:N"))
    chart = chart + text
    return chart

def barra_proporcional(
    df: pd.DataFrame, cols_name: list,cols_colors: list ,max_month, min_month, intervalo: str = "tras",numero:str = 'normal' ,title:str = None, altura: int = None):
    if intervalo == "tras":
        df_filtered = df[(df["MES"] <= max_month) & (df["MES"] >= min_month)]
    else:
        df_filtered = df[(df["MES"] >= max_month) & (df["MES"] <= min_month)]
    df_long = df_filtered.melt(
        id_vars=["MES", "MES_STR"],
        value_vars=cols_name,
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
                axis=alt.Axis(grid=False, domain=True, domainColor="gray", labelAngle=0, ticks=True, tickColor="gray"),
            ),
            color=alt.Color(
                field="Categoria",
                type="nominal",
                sort=alt.SortField(field="Proporcao:Q", order="descending"),
                scale=alt.Scale(
                    domain=cols_name,
                    range=cols_colors,
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
        .properties(title=f"{title}")
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
    return chart

def linha_multiplas_sem_rotulo(
    df: pd.DataFrame, cols_name: list, cols_color: list, min_month:str, title:str = None):  
    minimo = pd.to_datetime(min_month)
    df_filtered = df[df["MES"] >= minimo]
    for col in cols_name:
        df_filtered[f"{col}_formatado"] = df_filtered[col].apply(
            lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else ""
        )
    chart = (
        alt.Chart(df_filtered)
        .transform_fold(cols_name, as_=["Categoria", "Valor"])
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
                    domain=cols_name,
                    range=cols_color,
                ),
                legend=alt.Legend(
                    direction="vertical",
                    columns=1,
                    title=None,
                    orient="none",
                    legendX=0,
                    legendY=-10,
                )
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Categoria:N", title="LINHA"),
                alt.Tooltip(f"Valor:Q", title="VALOR")
            ]
        )
        .properties(title=title)
    )
    return chart

def linha_simples_sem_rotulo(
    df: pd.DataFrame, col_name: str, max_month, min_month, cor1: str, intervalo: str = "tras",numero:str = 'normal', title:str = None):
    """
    df: Algum dataframe
    col_name: Coluna numérica para analisar
    max_month: Máximo mês no final
    min_month: Mínimo mês no final
    intervalo: Passado ou Futuro
    cor1: Cor em destaque
    """
    col = col_name
    cor_1 = cor1
    if max_month is not None and min_month is not None:
        if intervalo == "tras":
            df_filtered = df[(df["MES"] <= max_month) & (df["MES"] >= min_month)]
        elif intervalo == "frente":
            df_filtered = df[(df["MES"] >= max_month) & (df["MES"] <= min_month)]
    else:
        # Caso max_month e min_month sejam None, usa o DataFrame completo
        df_filtered = df
    
    if numero == 'normal':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.0f}".replace(",", ".")
        )
    elif numero == 'porcentagem':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.1%}".replace(".", ",")
        )
    elif numero == 'decimal':
        df_filtered["Valor_formatado"] = df_filtered[f"{col}"].apply(
            lambda x: f"{x:,.2f}".replace(".", ",")
        )
    chart = (
        alt.Chart(df_filtered)
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
                    labels=True,
                    ticks=True,
                    tickColor="gray",
                ),
            ),
            tooltip=[
                alt.Tooltip("MES_STR:N", title="MÊS"),
                alt.Tooltip("Valor_formatado:N", title=f"{col}")
            ],
            color=alt.value(f"{cor_1}"),
        )
        .properties(title=f"{title}")
    )
    return chart
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
    lista = ['RECEITA TOTAL', 'DESPESAS TOTAL']
    chart = linha_dupla(df=dre,cols_name=lista,max_month=actual_month,min_month=twelve_month,cor1=verde_escuro,cor2=vermelho_claro,title="R$ RECEITA x DESPESAS", rotulo='primeiro')
    st.altair_chart(chart, use_container_width=True)

with econ:
    chart = barchart_variacao(df=dre,col_name= "RESULTADO",max_month=actual_month,min_month= twelve_month,cor1=verde_escuro,cor2=vermelho_medio, title="R$ RESULTADO")
    st.altair_chart(chart, use_container_width=True)

with econ_perc:
    dre['PERC_RESULTADO'] = (dre['RESULTADO']/dre['RECEITA TOTAL'])
    chart = barchart_variacao(df=dre,col_name="PERC_RESULTADO",max_month=actual_month,min_month= twelve_month,cor1=verde_escuro,cor2= vermelho_medio,numero='porcentagem', title="% RESULTADO")
    st.altair_chart(chart, use_container_width=True)

##################################################################################################################################
# GRAFICOS DESPESAS ##############################################################################################################

total_hm = st.container()

total_hm, gastos = st.columns([1, 2])

with total_hm:
    total = barchart_simples(df=dre, col_name="DESPESAS TOTAL",max_month= forward_month,min_month= thirth_month,cor1=vermelho_medio,cor2= vermelho_claro, intervalo='tras',title="R$ DESPESAS TOTAL")
    rule = alt.Chart(dre).mark_rule().encode(strokeDash=alt.value([4, 2]), y=alt.datum(10000), color=alt.value("white"))
    total = total+rule
    st.altair_chart(total, use_container_width=True)

    # HEATMAP
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
        mercado = barchart_simples(df=dre, col_name="MERCADO",max_month= forward_month,min_month= thirth_month,cor1= vermelho_medio,cor2= vermelho_claro,title="R$ MERCADO")
        st.altair_chart(mercado, use_container_width=True)

    with diversos:
        mercado = barchart_simples(df=dre, col_name= "DIVERSOS",max_month= forward_month,min_month= thirth_month,cor1= vermelho_medio, cor2= vermelho_claro, title="R$ DIVERSOS")
        st.altair_chart(mercado, use_container_width=True)

    with assinaturas:
        mercado = barchart_simples(df=dre,col_name= "ASSINATURAS",max_month= forward_month,min_month= thirth_month,cor1= vermelho_medio,cor2= vermelho_claro, title="R$ ASSINATURAS")
        st.altair_chart(mercado, use_container_width=True)

    role, transporte, apartamento = st.columns(3)

    with role:
        mercado = barchart_simples(df= dre,col_name= "ROLE",max_month= forward_month, min_month= thirth_month,cor1=vermelho_medio,cor2= vermelho_claro, title="R$ ROLÊ")
        st.altair_chart(mercado, use_container_width=True)

    with transporte:
        mercado = barchart_simples(df=dre,col_name="TRANSPORTE",max_month=forward_month,min_month=thirth_month,cor1=vermelho_medio,cor2= vermelho_claro, title="R$ TRANSPORTE")
        st.altair_chart(mercado, use_container_width=True)
    
    with apartamento:
        mercado = barchart_simples(df=dre,col_name= "APARTAMENTO",max_month= forward_month,min_month= thirth_month,cor1= vermelho_medio,cor2= vermelho_claro, title="R$ APARTAMENTO")
        st.altair_chart(mercado, use_container_width=True)

##################################################################################################################################
## GRAFICOS DE PATRIMONIO  #######################################################################################################

patrimonio_bruto, dif_rs, investimentos_reserva = st.columns(3)

with patrimonio_bruto:
    chart = barchart_simples(df=ativos,col_name='PATRIMONIO_BRUTO',max_month= actual_month,min_month= thirth_month,cor1= azul_medio,cor2= azul_medio ,title="R$ PATRIMÔNIO BRUTO")
    st.altair_chart(chart, use_container_width=True)

with dif_rs:
    chart = barchart_variacao(df=ativos,col_name= 'DIF_PATRIMONIO',max_month= actual_month,min_month= thirth_month,cor1= azul_medio,cor2= vermelho_medio, title= "R$ RESULTADO PATRIMONIAL BRUTO")
    st.altair_chart(chart, use_container_width=True)

with investimentos_reserva:
    ativos_filtered = ativos[
        (ativos["MES"] <= actual_month) & (ativos["MES"] >= twelve_month)
    ]
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
                    labels=True
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
        fontWeight="bold",
    ).encode(
        text=alt.Text("Valor:Q", format=",.0f"),
        color=alt.condition(
            alt.datum.Categoria == "FATURA",
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
                    range=[f"{rosa}", "#adb5bd"],
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
    chart = linha_simples(df=luz,col_name='PRECO KWH',max_month= actual_month,min_month= twelve_month,cor1=rosa,numero='decimal',title="R$ CUSTO KWH")
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
    chart = linha_simples(df=dre,col_name='SALARIO_12',max_month= actual_month,min_month= twelve_month,cor1= verde_escuro,title='R$ SALÁRIO ACUMULADO 12 MESES')
    st.altair_chart(chart, use_container_width=True)

with dividendos:
    dre['DIVIDENDOS_12'] = dre['DIVIDENDOS'].rolling(window=12, min_periods=1).sum()
    chart = linha_simples(df=dre,col_name='DIVIDENDOS_12',max_month= actual_month,min_month= twelve_month,cor1= verde_medio,title='R$ DIVIDENDOS ACUMULADO 12 MESES')
    st.altair_chart(chart, use_container_width=True)

with outros:
    dre['OUTROS_12'] = dre['OUTROS'].rolling(window=12, min_periods=1).sum()
    dre_filtered = dre[(dre["MES"] <= actual_month) & (dre["MES"] >= twelve_month)]
    chart = linha_simples(df=dre,col_name='OUTROS_12',max_month= actual_month,min_month= twelve_month,cor1= verde_claro, title='R$ OUTROS ACUMULADO 12 MESES')
    st.altair_chart(chart, use_container_width=True)

# ## GASTOS FUTUROS ################################################################################################################

gastos_futuros, endividamento = st.columns(2)

with gastos_futuros:
    total_futuro = barchart_simples(df=dre,col_name= "DESPESAS TOTAL",max_month= forward_month,min_month= fourth_month_forward,cor1= vermelho_medio,cor2= vermelho_medio, intervalo="frente", title="R$ DESPESAS TOTAL PRÓXIMOS 12 MESES")
    st.altair_chart(total_futuro, use_container_width=True)

with endividamento:
    dre["PERC_RENDA"] = (dre["DESPESAS TOTAL"] / dre["RECEITA TOTAL"])
    chart = linha_simples(df=dre,col_name="PERC_RENDA",max_month=None, min_month=None,  cor1=vermelho_medio, numero='porcentagem', title="ENDIVIDAMENTO")
    limite = (
        alt.Chart(dre)
        .mark_rule()
        .encode(
            y=alt.datum(0.7),
            size=alt.value(1),
            color=alt.value("white"),
            strokeDash=alt.value([4, 2]),
        )
    )
    chart = chart + limite 
    st.altair_chart(chart,use_container_width=True)

gastos_futuros_proporcional, gastos_nois = st.columns(2)

with gastos_futuros_proporcional:
    lista = ["MERCADO","DIVERSOS","ASSINATURAS","ROLE","TRANSPORTE","APARTAMENTO"]
    lista_cores = ["#E63946", "#F4A261", "#2A9D8F", "#9B5DE5","#6D696A" ,"#457B9D"]
    chart = barra_proporcional(df=dre,cols_name=lista,cols_colors= lista_cores,min_month=forward_month,max_month= fourth_month_forward,numero='porcentagem',title="% DISTRIBUIÇÃO DOS GASTOS FUTUROS")
    st.altair_chart(chart, use_container_width=True)

with gastos_nois:
    lista = ["DESPESAS LUCAS","DESPESAS JESSICA",]
    lista_cores = ["#49b6ff","#ff69eb"]
    chart = barra_proporcional(df=dre,cols_name=lista,cols_colors= lista_cores,max_month= actual_month, min_month= twelve_month,numero="porcentagem", title = "PROPORÇÃO DE GASTOS")
    st.altair_chart(chart, use_container_width=True)

##################################################################################################################################
## CRESCIMENTO ###################################################################################################################


curva_bruto, curva_liquido, usd = st.columns(3)
ativos_filtered = ativos[ativos["MES"] >= pd.to_datetime("2023-09-01")]

with curva_bruto:
    lista = ["CURVA BRUTO", "CURVA INFLACAO", "CURVA JUROS"]
    lista_cores = ["#00cecb", "#fb8500", "#fff3b0"]
    chart = linha_multiplas_sem_rotulo(df=ativos,cols_name=lista,cols_color= lista_cores,min_month='2023-09-01', title="CURVA PATRIMÔNIO BRUTO x SELIC x INFLACAO")
    chart = chart
    st.altair_chart(chart, use_container_width=True)

with curva_liquido:
    lista = ["CURVA LIQUIDO", "CURVA INFLACAO", "CURVA JUROS"]
    lista_cores = ["#00cecb", "#fb8500", "#fff3b0"]
    chart = linha_multiplas_sem_rotulo(ativos,lista, lista_cores, '2023-09-01', title="CURVA PATRIMÔNIO LIQUIDO x SELIC x INFLACAO")
    chart = chart
    st.altair_chart(chart, use_container_width=True)

with usd:
    ativos["usd_share"] = (ativos_filtered["WISE"] + ativos_filtered["AVENUE"]) / ativos_filtered["PATRIMONIO_LIQUIDO"]
    chart = linha_simples(ativos, "usd_share", actual_month, thirth_month, azul_claro, numero='porcentagem', title="% PATRIMÔNIO LÍQUIDO EM USD")
    st.altair_chart(chart, use_container_width=True)

consumo_kwh, preco_kwh = st.columns(2)

with consumo_kwh:
    chart = linha_simples_sem_rotulo(df=luz,col_name= "KWH DIA",max_month=None, min_month=None,cor1= rosa, numero='normal', title="CONSUMO KWH DIA HISTÓRICO")
    st.altair_chart(chart, use_container_width=True)

with preco_kwh:
    chart = linha_simples_sem_rotulo(df=luz,col_name= "PRECO KWH",max_month=None, min_month=None, cor1= rosa, numero='decimal', title="CUSTO KWH HISTÓRICO")
    st.altair_chart(chart, use_container_width=True)
