import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.get_data import GoogleFinance
pd.set_option('display.max_columns', None)

def make_luz(sheets: dict) -> pd.DataFrame:
    s = sheets
    plans = GoogleFinance(sheet_dict=s)

    luz_df = plans.luz_df_transformation()
    luz_df.set_index("MES", inplace=True)
    luz_df = luz_df.asfreq("MS")

    modelo = ExponentialSmoothing(
        luz_df["FATURA"],
        trend="add",
        seasonal=None,
        freq="MS",
        initialization_method="estimated",
    )

    ajuste = modelo.fit()

    previsao = ajuste.forecast(steps=3)

    index_futuro = pd.date_range(
        start=luz_df.index[-1] + pd.offsets.MonthBegin(1), periods=3, freq="MS"
    )

    previsoes_df = pd.DataFrame(
        previsao, index=index_futuro, columns=["FATURA_PREVISTA"]
    )

    luz_df_com_previsao = pd.concat([luz_df, previsoes_df])
    luz_df_com_previsao = luz_df_com_previsao.reset_index().rename(
        columns={"index": "MES"}
    )

    luz_df_com_previsao["FATURA_PREVISTA"] = luz_df_com_previsao[
        "FATURA_PREVISTA"
    ].round(2)

    luz_df_com_previsao["MES_STR"] = luz_df_com_previsao["MES"].dt.strftime("%b/%y")
    return luz_df_com_previsao


if __name__ == "__main__":

    sheet_dict = {
        "DRE TT": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=885613319#gid=885613319",
        "Ativos": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=2055342803#gid=2055342803",
        "Luz": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=1179918927#gid=1179918927",
        "Credit Card": "https://docs.google.com/spreadsheets/d/1AenV1BmOYwrO0GM_zv77xVcpGMHWg_ikXL-fnqpbpCA/edit?gid=1853911625#gid=1853911625",
    }
    luz = make_luz(sheet_dict)

    print(luz)
