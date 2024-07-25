from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

import streamlit as st

option = ["愛媛県", "四国中央", "西条", "今治", "松山市", "中予", "八幡浜", "宇和島"]


@st.cache_data
def load_data():
    url = "https://www.pref.ehime.jp/site/kanjyo/39800.html"

    r = requests.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, "html.parser")

    tag_table = soup.find("p", string="患者報告数の週推移").find_parent("table")

    # th colspan 2
    tag_table.select_one('th[colspan="37"]')["colspan"] = "2"

    # td colspan del
    for td in tag_table.select('td[colspan="36"]'):
        del td["colspan"]

    html = tag_table.prettify()

    df0 = pd.read_html(StringIO(html))[0]

    df0.columns = df0.columns.str.replace(r"\s", "", regex=True)
    df0.rename(columns={"保健所名": "月", "保健所名.1": "週"}, inplace=True)

    df0["月"] = pd.to_numeric(df0["月"].str.rstrip("月"), errors="coerce")
    df0["週"] = pd.to_numeric(df0["週"].str.strip("第週"), errors="coerce")

    df_weeks = pd.date_range("2024-01-01", "2025-01-8", freq="W-SUN").isocalendar()
    df_weeks = df_weeks[df_weeks["year"] == 2024]
    df_weeks.index.name = "date"
    df_weeks.reset_index(inplace=True)

    df1 = pd.merge(df0, df_weeks, how="left", left_on="週", right_on="week").set_index("date").sort_index()

    df2 = df1.reindex(columns=option).copy()

    return df2


st.set_page_config(page_title="愛媛県新型コロナウイルス2024")
st.title("新型コロナウイルス")


df = load_data()

# ストリームリットセレクトボックスの作成
chois = st.multiselect("保健所を選択", option, default="今治")

if chois:
    filterd_df = df.reindex(columns=chois)

    st.line_chart(filterd_df)
    st.dataframe(filterd_df, width=700)
