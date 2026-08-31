import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* Metric Cards: Adjust the size of the metric value */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important; 
    }
    
    /* Metric Cards: Adjust the size of the metric label */
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }

    /* Sidebar: Change multiselect tag background to brown */
    span[data-baseweb="tag"] {
        background-color: #553020 !important;
    }
    
    /* Sidebar: Change multiselect tag text color to white */
    span[data-baseweb="tag"] span {
        color: white !important;
    }
    
    /* Sidebar: Change the 'x' close button color to white */
    span[data-baseweb="tag"] svg {
        fill: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

### Construindo o filtro das ações
def  build_sidebar():
    st.image("imagens/RebecaBatista-logo.svg")
    ticker_df = pd.read_csv("acoes-b3-20260830.csv")
    ticker_list = sorted(ticker_df.iloc[:, 0].astype(str).tolist())
    tickers = st.multiselect(label="Selecione as Empresas", options=ticker_list, placeholder="Ticker")
    tickers = [t+".SA" for t in tickers]
    start_date = st.date_input("De",format="DD/MM/YYYY",value=datetime(2025,8,30))
    end_date = st.date_input("Até",format="DD/MM/YYYY",value="today")
    st.write("DISCLAIMER: Este material é um portfolio de análise quant com a ferramenta python, não constitui recomendação de investimento.")

    if tickers:
        prices = yf.download(tickers,start=start_date, end=end_date)["Close"]
        #if len(tickers) == 1:
        #     prices= prices.to_frame()
        #     prices.columns = [tickers[0].rstrip(".SA")]

        prices.columns = prices.columns.str.rstrip(".SA")
        prices['IBOV']= yf.download("^BVSP", start=start_date, end=end_date)["Close"]
        return tickers, prices
    return None, None

###################################### Construindo o resultado das ações

def build_main(ticker, prices):
    weights = np.ones (len(tickers))/len(tickers) ###REVISAR ISSO PRA FICAR NA LATERAL
    prices['Portfolio']= prices.drop("IBOV", axis=1) @ weights
    norm_prices = 100 * prices / prices.iloc[0]
    returns = prices.pct_change()[1:]
    vols = returns.std()*np.sqrt(252)
    rets = (norm_prices.iloc[-1] - 100) / 100

    mygrid = grid(5,5,5,5,5,5, vertical_align="top")
    for t in prices.columns:
        c = mygrid.container(border=True)
        c.subheader(t, divider="yellow")
        colA, colB = c.columns(2)
        colA.metric(label="Retorno", value=f"{rets[t]:.0%}")
        colB.metric(label="Volatilidade", value=f"{vols[t]:.0%}")
    style_metric_cards(background_color='rgba(255,255,255,0)',border_left_color="#553020", border_size_px=1)

    col1, col2 = st.columns(2, gap="small")
    with col1:
            st.subheader("Desempenho Relativo")
            st.line_chart(norm_prices,height=800)

    with col2:
            st.subheader("Risco-Retorno")
            fig = px.scatter(
                 x=vols,
                 y=rets,
                 text=vols.index,
                 color=(rets-0.14)/vols,
                 color_continuous_scale=["#553020", "#FFCC3A"])
            fig.update_traces(
                 textfont_color="white",
                 marker=dict(size=25),
                 textfont_size=10)
            fig.add_hline(y=0.14, line_dash="dot", line_width=1, line_color="red", annotation_text="Risco Base 14% SELIC")
            fig.layout.yaxis.title = "Retorno Total"
            fig.layout.xaxis.title = "Volatilidade (anualizada)"
            fig.layout.height=800
            fig.layout.yaxis.tickformat = ".0%"
            fig.layout.xaxis.tickformat = ".0%"
            fig.layout.coloraxis.colorbar.title ="Sharpe Ratio"

            st.plotly_chart(fig, use_container_width=True)                    

with st.sidebar:
    tickers, prices=build_sidebar()

st.title("Análise Interativa Ibovespa Risco e Retorno")
st.write("Selecione ações no menu lateral para comparação.")
if tickers:
    build_main(tickers, prices)