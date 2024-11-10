import locale
import os
from datetime import datetime

import gspread as gp
import pandas as pd
from dotenv import load_dotenv

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

load_dotenv()

credentials = os.getenv("CREDENTIALS")

pd.set_option("display.max_columns", None)


class GoogleFinance:
    def __init__(self, sheet_dict):
        self.sheet_dict = sheet_dict
        self.credentials = os.getenv("CREDENTIALS")
        self.df_dict = None

    def connect_to_google(self):
        try:
            gc = gp.service_account(filename=self.credentials)
            print("Connection succesful")
        except FileNotFoundError:
            print("Credential file not found")
        except Exception:
            print("Worksheet not found or name has changed")
        return gc

    def get_dataframes(self):
        con = self.connect_to_google()
        self.df_dict = {}
        # O método .items() do dicionário devolve cada par chave-valor na ordem em que os itens foram adicionados
        # (ou seja, a mesma ordem em que você vê no dicionário)
        for sheet_name, sheet_url in self.sheet_dict.items():
            try:
                link = con.open_by_url(sheet_url).worksheet(sheet_name)
                df = pd.DataFrame(link.get_all_values())

                # armazena o DataFrame df no dicionário dataframes usando sheet_name como a chave
                self.df_dict[sheet_name] = df
            except Exception as e:
                print(f"Error fetching {sheet_name}: {e}")
        return self.df_dict

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
        dfs = self.get_dataframes()
        dre = dfs.pop("DRE TT")
        headers = dre.iloc[3]
        headers.name = None
        dre = pd.DataFrame(dre.values[4:], columns=headers)
        dre = dre[
            [
                "Mês.Déb",
                "Salários",
                "Dividendos",
                "Outros",
                "Receita Total",
                "Despesas Total",
                "Resultado",
                "T_Mercado",
                "T_Diversos",
                "T_Assinaturas",
                "T_Rolê",
                "T_Transporte",
                "T_Apartamento",
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
        dfs = self.get_dataframes()
        ativos = dfs.pop("Ativos")
        headers = ativos.iloc[5]
        headers.name = None
        ativos = pd.DataFrame(ativos.values[6:], columns=headers)
        ativos = ativos[
            [
                "Mês",
                "Patrimônio Total",
                "Patrimônio R$",
                "Investimento",
                "Reservas",
                "Dif R$",
                "%Var. R$",
                "Patrimônio L R$",
                "Investimento L",
                "Reservas L",
                "Bradesco",
                "Nuinvest L",
                "Binance",
                "Avenue",
                "Daycoval",
                "Wise",
                "$ Avenue",
                "$ Wise",
                "Cotação USD",
                "Patrimônio J R$",
                "Investimento J",
                "Reservas J",
                "Banco Brasil",
                "Sofisa",
                "ITI",
                "Nubank",
                "Nuinvest J",
                "Carro",
                "IPCA-15",
                "IPCA ACUM",
                "PATRI",
                "PATRI ACUM",
                "CRESCIMENTO REAL",
                "CRESCIMENTO REAL ACUM",
            ]
        ]
        ativos.columns = [x.upper() for x in ativos.columns]
        ativos = ativos.rename(
            columns={
                "MÊS": "MES",
                "PATRIMÔNIO TOTAL": "PATRIMONIO BRUTO",
                "PATRIMÔNIO R$": "PATRIMONIO LIQUIDO",
                "DIF R$": "DIF PATRIMONIO",
                "%VAR. R$": "% VAR PATRIMONIO",
                "PATRIMÔNIO L R$": "PATRIMONIO LUCAS LIQUIDO",
                "INVESTIMENTO L": "INVESTIMENTO LUCAS",
                "RESERVAS L": "RESERVAS LUCAS",
                "NUINVEST L": "NUINVEST LUCAS",
                "$ AVENUE": "AVENUE USD",
                "$ WISE": "WISE USD",
                "COTAÇÃO USD": "COTACAO USD",
                "PATRIMÔNIO J R$": "PATRIMONIO JESSICA",
                "INVESTIMENTO J": "INVESTIMENTO JESSICA",
                "RESERVAS J": "RESERVAS JESSICA",
                "NUINVEST J": "NUINVEST JESSICA",
                "IPCA-15": "% IPCA",
                "IPCA ACUM": "% IPCA ACUM",
                "PATRI": "% PATRIMONIO",
                "PATRI ACUM": "% PATRIMONIO ACUM",
                "CRESCIMENTO REAL": "% CRESCIMENTO REAL",
                "CRESCIMENTO REAL ACUM": "% CRESCIMENTO REAL ACUM",
            }
        )
        ativos = self.clean_months(ativos, "MES")
        ativos = ativos.replace("#N/A", pd.NA)
        ativos = ativos.dropna()
        ativos = ativos.map(
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
        ativos["MES_STR"] = ativos["MES"].dt.strftime("%b/%y")
        return ativos

    def luz_df_transformation(self) -> pd.DataFrame:
        dfs = self.get_dataframes()
        luz = dfs.pop("Luz")
        headers = luz.iloc[0]
        headers.name = None
        luz = pd.DataFrame(luz.values[1:], columns=headers)
        luz = luz[["mês", "Fatura", "kWh", "Dias", "kWh Dia", "Preço kWh"]]
        luz.columns = [x.upper() for x in luz.columns]
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
        luz["MES_STR"] = luz["MES"].dt.strftime("%b/%y")
        return luz

    def cartao_df_transformation(self) -> pd.DataFrame:
        dfs = self.get_dataframes()
        cartao = dfs.pop("Credit Card")
        headers = cartao.iloc[29]
        headers.name = None
        cartao = pd.DataFrame(cartao.values[30:], columns=headers)
        cartao = cartao[["Mes/Ano Gráfico", "Fatura", "Renda", "% Renda"]]
        cartao.columns = [x.upper() for x in cartao.columns]
        cartao = cartao.rename(
            columns={"MES/ANO GRÁFICO": "MES", "PREÇO KWH": "PRECO KWH"}
        )
        cartao = self.clean_months(cartao, "MES")
        cartao = cartao.replace("#N/A", pd.NA)
        cartao = cartao.dropna()
        cartao = cartao.map(
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
        cartao = cartao.fillna("#N/A")
        cartao["MES_STR"] = cartao["MES"].dt.strftime("%b/%y")
        return cartao


if __name__ == "__main__":
    sheet_dict = {
        "DRE TT": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=885613319#gid=885613319",
        "Ativos": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=2055342803#gid=2055342803",
        "Luz": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=1179918927#gid=1179918927",
        "Credit Card": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=1853911625#gid=1853911625",
    }

    plans = GoogleFinance(sheet_dict=sheet_dict)
    #dre = plans.dre_df_transformation()
    atv = plans.ativos_df_transformation()
    print(atv.columns)
    # luz = plans.luz_df_transformation()
    # print(luz)