import locale
import os
from datetime import datetime

import gspread as gp
import pandas as pd
from dotenv import load_dotenv
from statsmodels.tsa.holtwinters import ExponentialSmoothing

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

load_dotenv()
pd.set_option("display.max_columns", None)


class GoogleFinance:
    def __init__(self):
        self.credentials = os.getenv("CREDENTIALS")
        self.df_dict = None
        self.gc = self.connect_to_google()  # conexão é criada uma única vez
        self.sheet_dict = {
            "DRE TT": os.getenv("URL_DRE_TT"),
            "Ativos": os.getenv("URL_ATIVOS"),
            "Luz": os.getenv("URL_LUZ"),
            "Credit Card": os.getenv("URL_CREDIT_CARD"),
        }


    def connect_to_google(self):
        try:
            gc = gp.service_account(filename=self.credentials)
            print("Connection succesful")
            return gc
        except FileNotFoundError as e:
            print(f"Credential file not found: {e}")
        except Exception as e:
            print(f"Worksheet not found or name has changed: {e}")

    def get_dataframes(self, plan_name: str):
        con = self.gc
        try:
            # Verifica se a planilha está no dicionário
            if plan_name in self.sheet_dict:
                # Pega a URL da planilha específica
                sheet_url = self.sheet_dict[plan_name]
                # Acessa a planilha e transforma em DataFrame
                link = con.open_by_url(sheet_url).worksheet(plan_name)
                df = pd.DataFrame(link.get_all_values())
                return df
            else:
                print(f"Planilha '{plan_name}' não encontrada no dicionário.")
                return None
        except Exception as e:
            print(f"Erro ao buscar '{plan_name}': {e}")
            return None

    def clean_months(self, dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
        df = dataframe
        col = column_name
        df[col] = df[col].str.replace(".", "").str.replace("/", "-")
        month = {
            "jan": "1",
            "fev": "2",
            "mar": "3",
            "abr": "4",
            "mai": "5",
            "jun": "6",
            "jul": "7",
            "ago": "8",
            "set": "9",
            "out": "10",
            "nov": "11",
            "dez": "12",
        }
        df[col] = df[col].replace(month, regex=True)

        def convert_to_datetime(value):
            length = len(value)
            if length in range(4, 6):  # Formato '%m-%y'
                return pd.to_datetime(value, format="%m-%y", errors="coerce")
            elif length in range(6, 8):  # Formato '%m-%Y'
                return pd.to_datetime(value, format="%m-%Y", errors="coerce")
            else:
                return pd.NaT

        df[col] = df[col].apply(convert_to_datetime)
        return df

    def dre_df_transformation(self) -> pd.DataFrame:
        dre = self.get_dataframes("DRE TT")
        if dre is None or dre.empty:
            erro = print("Erro: DRE TT DataFrame não carregado ou está vazio")
            return erro
        headers = dre.iloc[3]
        headers.name = None
        dre = pd.DataFrame(dre.values[4:], columns=headers)
        dre.columns = [x.upper() for x in dre.columns]
        dre = dre[
            [
                "MÊS.DÉB",
                "SALÁRIOS",
                "DIVIDENDOS",
                "OUTROS",
                "RECEITA TOTAL",
                "DESPESAS TOTAL",
                "RESULTADO",
                "T_MERCADO",
                "T_DIVERSOS",
                "T_ASSINATURAS",
                "T_ROLÊ",
                "T_TRANSPORTE",
                "T_APARTAMENTO",
                "DESPESAS LUCAS",
                "DESPESAS JESSICA"
            ]
        ]
        dre.columns = [x.upper() for x in dre.columns]
        dre = dre.rename(
            columns={
                "MÊS.DÉB": "MES",
                "SALÁRIOS": "SALARIO",
                "T_MERCADO": "MERCADO",
                "T_DIVERSOS": "DIVERSOS",
                "T_ASSINATURAS": "ASSINATURAS",
                "T_ROLÊ": "ROLE",
                "T_TRANSPORTE": "TRANSPORTE",
                "T_APARTAMENTO": "APARTAMENTO",
            }
        )
        dre = self.clean_months(dre, "MES")
        dre = dre.replace("#N/A", pd.NA)
        dre = dre.dropna()
        dre = dre.map(
            lambda x: (
                str(x).replace("R$ ", "").replace(".", "").replace(",", ".")
                if isinstance(x, str)
                else x
            )
        ).astype(float, errors="ignore")
        dre["MES_STR"] = dre["MES"].dt.strftime("%b/%y")

        return dre

    def ativos_df_transformation(self) -> pd.DataFrame:
        ativos = self.get_dataframes("Ativos")
        if ativos is None or ativos.empty:
            erro = print("Erro: Ativos DataFrame não carregado ou está vazio")
            return erro
        headers = ativos.iloc[5]
        headers.name = None
        ativos = pd.DataFrame(ativos.values[6:], columns=headers)
        ativos.columns = [x.upper() for x in ativos.columns]
        ativos = ativos[
            [
                "MÊS",
                "PATRIMÔNIO TOTAL",
                "PATRIMÔNIO R$",
                "INVESTIMENTO",
                "RESERVAS",
                "DIF R$",
                "%VAR. R$",
                "PATRIMÔNIO L R$",
                "INVESTIMENTO L",
                "RESERVAS L",
                "BRADESCO",
                "NUINVEST L",
                "BITCOIN",
                "AVENUE",
                "DAYCOVAL",
                "WISE",
                "$ AVENUE",
                "$ WISE",
                "COTAÇÃO USD",
                "PATRIMÔNIO J R$",
                "INVESTIMENTO J",
                "RESERVAS J",
                "BANCO BRASIL",
                "SOFISA",
                "ITI",
                "NUBANK",
                "NUINVEST J",
                "CARRO",
                "INFLACAO",
                "SELIC MENSAL",
                "CURVA INFLACAO",
                "CURVA JUROS",
                "AJUSTE BRUTO",
                "CURVA BRUTO",
                "AJUSTE LIQUIDO",
                "CURVA LIQUIDO",
            ]
        ]
        ativos = ativos.rename(
            columns={
                "MÊS": "MES",
                "PATRIMÔNIO TOTAL": "PATRIMONIO_BRUTO",
                "PATRIMÔNIO R$": "PATRIMONIO_LIQUIDO",
                "DIF R$": "DIF_PATRIMONIO",
                "%VAR. R$": "% VAR_PATRIMONIO",
                "PATRIMÔNIO L R$": "PATRIMONIO_LUCAS_LIQUIDO",
                "INVESTIMENTO L": "INVESTIMENTO_LUCAS",
                "RESERVAS L": "RESERVAS_LUCAS",
                "NUINVEST L": "NUINVEST_LUCAS",
                "$ AVENUE": "AVENUE_USD",
                "$ WISE": "WISE_USD",
                "COTAÇÃO USD": "COTACAO_USD",
                "PATRIMÔNIO J R$": "PATRIMONIO_JESSICA",
                "INVESTIMENTO J": "INVESTIMENTO_JESSICA",
                "RESERVAS J": "RESERVAS_JESSICA",
                "NUINVEST J": "NUINVEST_JESSICA",
                "INFLACAO": "PERC_INFLACAO",
                "SELIC MENSAL": "PERC_SELIC",
            }
        )
        ativos = self.clean_months(ativos, "MES")
        ativos = ativos.replace("#N/A", pd.NA)
        ativos = ativos.dropna()
        ativos = (
            ativos.map(
                lambda x: (
                    str(x)
                    .replace("R$ ", "")
                    .replace(".", "")
                    .replace(",", ".")
                    .replace("%", "")
                    .replace("$", "")
                    if isinstance(x, str)
                    else x
                )
            )
            .apply(pd.to_numeric, errors="coerce")
            .astype(float)
        )
        ativos["MES"] = pd.to_datetime(ativos["MES"], errors="ignore")
        ativos["MES_STR"] = ativos["MES"].dt.strftime("%b/%y")
        return ativos

    def luz_df_transformation(self) -> pd.DataFrame:
        luz = self.get_dataframes("Luz")
        if luz is None or luz.empty:
            erro = print("Erro: DRE TT DataFrame não carregado ou está vazio")
            return erro
        headers = luz.iloc[0]
        headers.name = None
        luz = pd.DataFrame(luz.values[1:], columns=headers)
        luz.columns = [x.upper() for x in luz.columns]
        luz = luz[["MÊS", "FATURA", "KWH", "DIAS", "KWH DIA", "PREÇO KWH"]]
        luz = luz.rename(columns={"MÊS": "MES", "PREÇO KWH": "PRECO KWH"})
        luz = self.clean_months(luz, "MES")
        luz = luz.replace("#N/A", pd.NA)
        luz = luz.dropna()
        luz = luz.map(
            lambda x: (
                str(x)
                .replace("R$ ", "")
                .replace(".", "")
                .replace(",", ".")
                .replace("%", "")
                if isinstance(x, str)
                else x
            )
        ).astype(float, errors="ignore")

        luz.set_index("MES", inplace=True)
        luz = luz.asfreq("MS")

        # Modelo e previsão para 'FATURA'
        modelo_fatura = ExponentialSmoothing(
            luz["FATURA"],
            trend="add",
            seasonal="add",
            freq="MS",
            initialization_method="estimated",
        )
        ajuste_fatura = modelo_fatura.fit()
        previsao_fatura = ajuste_fatura.forecast(steps=3)

        # Modelo e previsão para 'KWH DIA'
        modelo_kwh_dia = ExponentialSmoothing(
            luz["KWH DIA"],
            trend="add",
            seasonal="add",
            freq="MS",
            initialization_method="estimated",
        )
        ajuste_kwh_dia = modelo_kwh_dia.fit()
        previsao_kwh_dia = ajuste_kwh_dia.forecast(steps=3)

        # Criar o índice futuro para os próximos 3 meses
        index_futuro = pd.date_range(
            start=luz.index[-1] + pd.offsets.MonthBegin(1), periods=3, freq="MS"
        )

        # DataFrames de previsões
        previsoes_fatura_df = pd.DataFrame(
            previsao_fatura, index=index_futuro, columns=["FATURA_PREVISTA"]
        )
        previsoes_kwh_dia_df = pd.DataFrame(
            previsao_kwh_dia, index=index_futuro, columns=["KWH_DIA_PREVISTO"]
        )

        # Concatenar previsões ao DataFrame original
        luz_com_previsao = pd.concat(
            [luz, previsoes_fatura_df, previsoes_kwh_dia_df], axis=1
        )
        luz_com_previsao = luz_com_previsao.reset_index().rename(
            columns={"index": "MES"}
        )

        # Formatar e arredondar colunas de previsão
        luz_com_previsao["FATURA_PREVISTA"] = luz_com_previsao["FATURA_PREVISTA"].round(
            2
        )
        luz_com_previsao["KWH_DIA_PREVISTO"] = luz_com_previsao[
            "KWH_DIA_PREVISTO"
        ].round(2)

        # Adicionar coluna de rótulo de mês/ano para exibição
        luz_com_previsao["MES_STR"] = luz_com_previsao["MES"].dt.strftime("%b/%y")

        return luz_com_previsao



if __name__ == "__main__":
    plans = GoogleFinance()
    # dre = plans.dre_df_transformation()
    # print(dre)
    #atv = plans.ativos_df_transformation()
    # print(atv)
    #print(atv.tail())
    # print(atv.dtypes)
    # luz = plans.luz_df_transformation()
    # print(luz)
    # print(luz.dtypes)
    # atv.to_csv("atv.csv", sep=';', index=False)
    # dre.to_csv("dre.csv", sep=';', index=False)
