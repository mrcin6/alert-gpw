import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import numpy as np
from streamlit_autorefresh import st_autorefresh

# --- Configuration & Styling ---
st.set_page_config(page_title="GPW Early Warning Dashboard", layout="wide")

# Automatyczne odświeżanie co 5 minut (300 000 ms)
st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    /* Global Typography & Background */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Poppins', sans-serif !important;
        background-color: #131f33 !important;
        color: #ffffff !important;
    }

    /* Sidebar container and content */
    [data-testid="stSidebar"] {
        background-color: #111926 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Poppins', sans-serif !important;
        color: #ffffff !important;
    }

    /* Header Group Styles */
    .cxr-header-group {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 32px;
        background-color: #1f2b40;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .cxr-emojicon {
        width: 64px;
        height: 64px;
        background-color: #131f33;
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .cxr-header-text {
        display: flex;
        flex-direction: column;
    }
    .cxr-title {
        font-size: 30px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    .cxr-neon-highlight {
        background-color: #ecfa64;
        color: #171a27 !important;
        padding: 2px 10px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
        margin-left: 8px;
    }
    .cxr-subtitle {
        font-size: 14px !important;
        color: rgba(255,255,255,0.6) !important;
        margin: 6px 0 0 0 !important;
        font-weight: 400 !important;
    }

    /* UXR-style Note Cards / Metrics */
    .uxr-metric-card {
        background-color: #1f2b40 !important;
        border-radius: 8px !important;
        border-left: 8px solid #DCDCDC;
        padding: 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .uxr-metric-card-positive { border-left-color: #cde200 !important; }
    .uxr-metric-card-informative { border-left-color: #5B8DEF !important; }
    .uxr-metric-card-negative { border-left-color: #FF5C5C !important; }
    .uxr-metric-card-alert { border-left-color: #FF9F43 !important; }

    .uxr-metric-title {
        font-size: 11px !important;
        color: rgba(255,255,255,0.6) !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .uxr-metric-value {
        font-size: 26px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        line-height: 1.2;
    }
    .uxr-metric-delta {
        font-size: 13px !important;
        font-weight: 500 !important;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .uxr-metric-delta-positive { color: #cde200 !important; }
    .uxr-metric-delta-negative { color: #FF5C5C !important; }

    /* Alert Banner Styles */
    .cxr-alert {
        padding: 20px !important;
        border-radius: 8px !important;
        margin-bottom: 32px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        border-left: 8px solid !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .cxr-alert-green {
        background-color: #1a2e21 !important;
        color: #e8f5e9 !important;
        border-left-color: #cde200 !important;
    }
    .cxr-alert-yellow {
        background-color: #2e2a14 !important;
        color: #fffde7 !important;
        border-left-color: #ecfa64 !important;
    }
    .cxr-alert-orange {
        background-color: #2e2014 !important;
        color: #fff3e0 !important;
        border-left-color: #FF9F43 !important;
    }
    .cxr-alert-red {
        background-color: #311414 !important;
        color: #ffebee !important;
        border-left-color: #FF5C5C !important;
    }

    /* Subheader component with left accent bar */
    .cxr-subheader-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 24px;
        margin-bottom: 16px;
    }
    .cxr-subheader-bar {
        width: 6px;
        height: 24px;
        background-color: #cde200;
        border-radius: 4px;
    }
    .cxr-subheader-text {
        font-size: 20px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        margin: 0 !important;
    }

    /* Table styling overrides */
    div[data-testid="stTable"] table {
        width: 100% !important;
        background-color: #1f2b40 !important;
        border-collapse: collapse !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        border: none !important;
    }
    div[data-testid="stTable"] th {
        background-color: #111926 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 14px 18px !important;
        font-family: 'Poppins', sans-serif !important;
        border-bottom: 2px solid rgba(255,255,255,0.05) !important;
        font-size: 14px !important;
    }
    div[data-testid="stTable"] td {
        color: rgba(255,255,255,0.9) !important;
        padding: 14px 18px !important;
        font-family: 'Poppins', sans-serif !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        font-size: 14px !important;
    }
    div[data-testid="stTable"] tr:last-child td {
        border-bottom: none !important;
    }

    /* Button and form overrides */
    .stButton>button {
        background-color: #1f2b40 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 6px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #ecfa64 !important;
        color: #171a27 !important;
        border-color: #ecfa64 !important;
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        background-color: #1f2b40 !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        margin-bottom: 24px !important;
    }
    div[data-testid="stExpander"] details {
        border: none !important;
        background: transparent !important;
    }
    div[data-testid="stExpander"] summary {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        padding: 14px 18px !important;
        cursor: pointer !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #ecfa64 !important;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 20px !important;
        background-color: #1f2b40 !important;
        border-top: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Guide Card inside Expander */
    .cxr-guide-box {
        min-height: 160px;
    }

    /* Mobile-first and Responsive Overrides */
    @media (max-width: 640px) {
        /* Container padding reduction to maximize space */
        [data-testid="stAppViewBlockContainer"] {
            padding: 16px 12px !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Header Group Styles */
        .cxr-header-group {
            flex-direction: column !important;
            text-align: center !important;
            padding: 16px !important;
            gap: 12px !important;
            margin-bottom: 20px !important;
        }
        .cxr-emojicon {
            width: 48px !important;
            height: 48px !important;
            font-size: 24px !important;
        }
        .cxr-title {
            font-size: 22px !important;
        }
        .cxr-neon-highlight {
            margin-left: 0 !important;
            margin-top: 6px !important;
            font-size: 14px !important;
            padding: 2px 8px !important;
        }
        .cxr-subtitle {
            font-size: 12px !important;
            margin-top: 4px !important;
        }

        /* Metric Cards Optimization */
        .uxr-metric-card {
            padding: 14px 16px !important;
            min-height: 90px !important;
            margin-bottom: 12px !important;
        }
        .uxr-metric-value {
            font-size: 22px !important;
        }
        .uxr-metric-title {
            font-size: 10px !important;
            margin-bottom: 4px !important;
        }
        .uxr-metric-delta {
            font-size: 11px !important;
            margin-top: 4px !important;
        }

        /* Alert Banner Optimization */
        .cxr-alert {
            padding: 14px 16px !important;
            font-size: 13px !important;
            margin-bottom: 20px !important;
        }

        /* Subheader Optimization */
        .cxr-subheader-text {
            font-size: 16px !important;
        }
        .cxr-subheader-bar {
            height: 18px !important;
        }

        /* Tables Responsive behavior */
        div[data-testid="stTable"] {
            overflow-x: auto !important;
            display: block !important;
            width: 100% !important;
        }
        div[data-testid="stTable"] th, div[data-testid="stTable"] td {
            padding: 10px 12px !important;
            font-size: 12px !important;
        }

        /* Guide Card inside Expander */
        .cxr-guide-box {
            min-height: auto !important;
            margin-bottom: 12px !important;
            padding: 14px !important;
        }
    }

    /* Footer caption */
    .cxr-caption {
        font-size: 12px !important;
        color: rgba(255,255,255,0.4) !important;
        text-align: center;
        margin-top: 32px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Component Helpers ---

def render_subheader(text):
    st.markdown(f"""
    <div class="cxr-subheader-container">
        <div class="cxr-subheader-bar"></div>
        <h2 class="cxr-subheader-text">{text}</h2>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, delta_text, delta_color="positive", border_type="informative"):
    border_class = f"uxr-metric-card-{border_type}"
    delta_class = f"uxr-metric-delta-{delta_color}"
    card_html = f"""
    <div class="uxr-metric-card {border_class}">
        <div class="uxr-metric-title">{title}</div>
        <div class="uxr-metric-value">{value}</div>
        <div class="uxr-metric-delta {delta_class}">{delta_text}</div>
    </div>
    """
    return card_html

# --- Data Fetching Functions ---

@st.cache_data(ttl=300) # Cache na 5 minut
def fetch_sentiment_crypto():
    try:
        url = "https://api.alternative.me/fng/?limit=30"
        response = requests.get(url, timeout=5).json()
        current_value = int(response['data'][0]['value'])
        current_label = response['data'][0]['value_classification']
        return current_value, current_label
    except Exception:
        return 50, "Neutral"

@st.cache_data(ttl=300)
def fetch_sentiment_cnn():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/"
        res = requests.get(url, headers=headers, timeout=5).json()
        score = int(res['fear_and_greed']['score'])
        rating = res['fear_and_greed']['rating']
        return score, rating
    except Exception:
        return 50, "Neutral"

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=300)
def get_market_data(tickers, period="2y", interval="1d"):
    data = yf.download(tickers, period=period, interval=interval, progress=False)
    if 'Close' in data:
        return data['Close']
    return pd.DataFrame()

# --- App Logic ---

# Sidebar: Controls & Manual Refresh
st.sidebar.markdown(f"""
    <div style="margin-bottom: 20px;">
        <h3 style="color: #ffffff; font-weight: 600; margin-bottom: 12px; font-size: 18px;">Ustawienia analizy</h3>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Odśwież notowania"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

time_range = st.sidebar.selectbox(
    "Przedział czasowy",
    ["Ostatnie 72 godziny", "Ostatnie 30 dni"]
)

if time_range == "Ostatnie 72 godziny":
    fetch_period = "1mo"
    interval = "1h"
    display_rows = 72
else:
    fetch_period = "2y"
    interval = "1d"
    display_rows = 30

tickers_map = {
    "^WIG20": "WIG20",
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq",
    "000001.SS": "Shanghai",
    "GC=F": "Złoto",
    "BTC-USD": "Bitcoin",
    "USDPLN=X": "USD/PLN"
}

with st.spinner("Aktualizacja danych rynkowych..."):
    df_raw = get_market_data(list(tickers_map.keys()), period=fetch_period, interval=interval)

if df_raw.empty:
    st.error("Błąd pobierania danych. Spróbuj manualnego odświeżenia.")
    st.stop()

# Indicators calculation
indicators = {}
for t_id, name in tickers_map.items():
    if t_id in df_raw:
        series = df_raw[t_id].dropna()
        if len(series) < 2: continue
        
        rsi_val = calculate_rsi(series).iloc[-1]
        ema20 = series.ewm(span=20, adjust=False).mean().iloc[-1]
        sma200 = series.rolling(window=200).mean().iloc[-1] if len(series) >= 200 else np.nan
        current_price = series.iloc[-1]
        
        idx_24 = -24 if interval == '1h' else -2
        idx_72 = -72 if interval == '1h' else -4
        
        change_24h = ((current_price / series.iloc[idx_24]) - 1) * 100 if len(series) >= abs(idx_24) else 0
        change_72h = ((current_price / series.iloc[idx_72]) - 1) * 100 if len(series) >= abs(idx_72) else 0
        
        indicators[t_id] = {
            "name": name,
            "current": current_price,
            "rsi": rsi_val,
            "ema20_dist": ((current_price / ema20) - 1) * 100,
            "sma200_dist": ((current_price / sma200) - 1) * 100 if not np.isnan(sma200) else 0.0,
            "change_24h": change_24h,
            "change_72h": change_72h
        }

# --- UI Rendering ---

# Header with Last Update
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown(f"""
        <div class="cxr-header-group">
            <div class="cxr-emojicon">📊</div>
            <div class="cxr-header-text">
                <h1 class="cxr-title">System Wczesnego Ostrzegania <span class="cxr-neon-highlight">GPW</span></h1>
                <p class="cxr-subtitle">Analiza sentymentu globalnego i dynamiki rynku polskiego</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
with header_col2:
    st.markdown(f"""
        <div style="text-align: right; padding-top: 24px; color: rgba(255,255,255,0.6); font-size: 14px; font-weight: 500;">
            ⏱️ {datetime.now().strftime('%H:%M:%S')}
        </div>
    """, unsafe_allow_html=True)

# Sentiment & Alerts
cnn_score, cnn_rating = fetch_sentiment_cnn()
crypto_score, crypto_rating = fetch_sentiment_crypto()

sp500_ch_24 = indicators.get("^GSPC", {}).get("change_24h", 0)
sp500_ch_72 = indicators.get("^GSPC", {}).get("change_72h", 0)
btc_ch_72 = indicators.get("BTC-USD", {}).get("change_72h", 0)
wig20_ch_24 = indicators.get("^WIG20", {}).get("change_24h", 0)
usdpln_ch_24 = indicators.get("USDPLN=X", {}).get("change_24h", 0)
gold_ch_24 = indicators.get("GC=F", {}).get("change_24h", 0)

alert_level = 0
alert_msg = "🟢 Stabilne otoczenie: Rynek zachowuje się w normie. Brak istotnych sygnałów alarmowych."
alert_class = "cxr-alert-green"

if (sp500_ch_72 < -2.5 and btc_ch_72 < -2.5) or cnn_score < 20 or crypto_score < 20:
    alert_level = 3
    alert_msg = "🔴 Krytyczne ryzyko: Globalna wyprzedaż na rynkach akcji. Wysokie prawdopodobieństwo głębszych spadków na GPW."
    alert_class = "cxr-alert-red"
elif (wig20_ch_24 < -1.5 and usdpln_ch_24 > 1.0):
    alert_level = 2
    alert_msg = "🟠 Ryzyko lokalne: Odpływ kapitału z polskiego rynku. Kurs USD/PLN rośnie przy spadkach indeksu WIG20."
    alert_class = "cxr-alert-orange"
elif (sp500_ch_24 < -1.5) or (cnn_score < 30) or (gold_ch_24 > 1.5 and sp500_ch_24 < 0):
    alert_level = 1
    alert_msg = "⚠️ Ostrzeżenie: Pogorszenie nastrojów globalnych. Zweryfikuj poziomy zabezpieczające (Stop-Loss)."
    alert_class = "cxr-alert-yellow"

st.markdown(f'<div class="cxr-alert {alert_class}">{alert_msg}</div>', unsafe_allow_html=True)

# KPI Tiles / Custom Note Cards
cols = st.columns(4)

# 1. CNN Fear & Greed Card
cnn_border = "negative" if cnn_score < 25 else ("alert" if cnn_score < 45 else ("informative" if cnn_score < 60 else "positive"))
cnn_delta_color = "negative" if cnn_score < 45 else "positive"
with cols[0]:
    st.markdown(render_metric_card(
        "Sentyment S&P 500 (CNN)", 
        f"{cnn_score}", 
        f"Klasyfikacja: {cnn_rating}", 
        delta_color=cnn_delta_color, 
        border_type=cnn_border
    ), unsafe_allow_html=True)

# 2. Crypto Fear & Greed Card
crypto_border = "negative" if crypto_score < 25 else ("alert" if crypto_score < 45 else ("informative" if crypto_score < 60 else "positive"))
crypto_delta_color = "negative" if crypto_score < 45 else "positive"
with cols[1]:
    st.markdown(render_metric_card(
        "Sentyment Krypto (F&G)", 
        f"{crypto_score}", 
        f"Klasyfikacja: {crypto_rating}", 
        delta_color=crypto_delta_color, 
        border_type=crypto_border
    ), unsafe_allow_html=True)

# 3. WIG20 Card
wig_val = indicators.get("^WIG20", {"current": 0, "change_24h": 0})
wig_border = "positive" if wig_val['change_24h'] >= 0 else "negative"
wig_delta_sign = "+" if wig_val['change_24h'] >= 0 else ""
with cols[2]:
    st.markdown(render_metric_card(
        "Indeks WIG20", 
        f"{wig_val['current']:.0f} pkt", 
        f"{wig_delta_sign}{wig_val['change_24h']:.2f}% (24h)", 
        delta_color="positive" if wig_val['change_24h'] >= 0 else "negative", 
        border_type=wig_border
    ), unsafe_allow_html=True)

# 4. USD/PLN Card
usd_val = indicators.get("USDPLN=X", {"current": 0, "change_24h": 0})
usd_is_negative = usd_val['change_24h'] >= 0
usd_border = "negative" if usd_is_negative else "positive"
usd_delta_sign = "+" if usd_val['change_24h'] >= 0 else ""
with cols[3]:
    st.markdown(render_metric_card(
        "Kurs USD/PLN", 
        f"{usd_val['current']:.4f} zł", 
        f"{usd_delta_sign}{usd_val['change_24h']:.2f}% (24h)", 
        delta_color="negative" if usd_is_negative else "positive", 
        border_type=usd_border
    ), unsafe_allow_html=True)

# --- Educational Legend & Guide ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("ℹ️ Przewodnik: Jak interpretować wskaźniki i czytać wykres?"):
    st.markdown("### 📈 Jak czytać wykres znormalizowany?")
    st.markdown(
        "Wykres domyślnie pokazuje ceny w **skali znormalizowanej (%)**. Oznacza to, że wszystkie aktywa zaczynają z tego samego punktu odniesienia (**100%** na początku wybranego okresu).\n\n"
        "Dzięki temu możesz bezpośrednio porównywać dynamikę wzrostów i spadków np. Bitcoina, indeksu S&P 500 oraz WIG20, ignorując fakt, że jedno kosztuje tysiące dolarów, a drugie kilka złotych.\n\n"
        "*Przykład: Wartość 105% oznacza wzrost o 5% od początku okresu, a 95% oznacza spadek o 5%. Odznaczenie pola wyboru pod wykresem przywróci ceny nominalne.*"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Jak interpretować wskaźniki techniczne?")
    
    g_cols = st.columns(3)
    with g_cols[0]:
        st.markdown(
'<div class="cxr-guide-box" style="background-color: #131f33; padding: 18px; border-radius: 6px; border-left: 4px solid #5B8DEF;">'
'<strong style="color: #ffffff; font-size: 14px; display: block; margin-bottom: 8px; font-family: \'Poppins\', sans-serif;">RSI (Relative Strength Index)</strong>'
'<p style="color: rgba(255,255,255,0.7); font-size: 13px; line-height: 1.5; margin: 0; font-family: \'Poppins\', sans-serif;">'
'Mierzy pęd ceny w skali 0-100:<br>'
'🟢 <strong>RSI &lt; 30 (Wyprzedanie)</strong>: Rynek może być nadmiernie pesymistyczny (szansa na odbicie w górę).<br>'
'🔴 <strong>RSI &gt; 70 (Wykupienie)</strong>: Rynek może być zbyt optymistyczny (ryzyko korekty w dół).'
'</p>'
'</div>',
            unsafe_allow_html=True
        )
    with g_cols[1]:
        st.markdown(
'<div class="cxr-guide-box" style="background-color: #131f33; padding: 18px; border-radius: 6px; border-left: 4px solid #cde200;">'
'<strong style="color: #ffffff; font-size: 14px; display: block; margin-bottom: 8px; font-family: \'Poppins\', sans-serif;">EMA-20 % (Średnia Krótkoterminowa)</strong>'
'<p style="color: rgba(255,255,255,0.7); font-size: 13px; line-height: 1.5; margin: 0; font-family: \'Poppins\', sans-serif;">'
'Odchylenie ceny od 20-okresowej średniej wykładniczej:<br>'
'📈 <strong>Wartość dodatnia</strong>: Cena jest powyżej średniej (krótkoterminowy trend wzrostowy).<br>'
'📉 <strong>Wartość ujemna</strong>: Cena spadła poniżej średniej (krótkoterminowe schłodzenie).'
'</p>'
'</div>',
            unsafe_allow_html=True
        )
    with g_cols[2]:
        st.markdown(
'<div class="cxr-guide-box" style="background-color: #131f33; padding: 18px; border-radius: 6px; border-left: 4px solid #FF9F43;">'
'<strong style="color: #ffffff; font-size: 14px; display: block; margin-bottom: 8px; font-family: \'Poppins\', sans-serif;">SMA-200 % (Trend Długoterminowy)</strong>'
'<p style="color: rgba(255,255,255,0.7); font-size: 13px; line-height: 1.5; margin: 0; font-family: \'Poppins\', sans-serif;">'
'Odchylenie ceny od 200-okresowej średniej prostej:<br>'
'🚀 <strong>Powyżej 0%</strong>: Długoterminowa hossa (rynek byka, silny trend wzrostowy).<br>'
'⚠️ <strong>Poniżej 0%</strong>: Długoterminowa bessa (rynek niedźwiedzia, ryzyko głębszych spadków).'
'</p>'
'</div>',
            unsafe_allow_html=True
        )

# Main Chart Section
df_display = df_raw.tail(display_rows)
render_subheader("Analiza dynamiki głównych rynków")
norm_chart = st.checkbox("Pokaż w skali znormalizowanej (%)", value=True)

fig = go.Figure()

color_map = {
    "WIG20": "#ecfa64",     # Signature Neon
    "S&P 500": "#5B8DEF",   # UXR Blue
    "Nasdaq": "#00D2C4",    # Teal
    "Shanghai": "#FF9F43",  # Orange
    "Złoto": "#FFE15D",     # Gold
    "Bitcoin": "#FF5C5C",   # Red
    "USD/PLN": "#FF78F0"    # Pink
}

for t_id, name in tickers_map.items():
    if t_id in df_display:
        y_data = df_display[t_id].dropna()
        if len(y_data) == 0: continue
        if norm_chart:
            y_data = (y_data / y_data.iloc[0]) * 100
        
        color = color_map.get(name, "#ffffff")
        fig.add_trace(go.Scatter(
            x=y_data.index, 
            y=y_data, 
            name=name, 
            mode='lines',
            line=dict(color=color, width=2)
        ))

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#1f2b40",
    plot_bgcolor="#131f33",
    font=dict(family="Poppins, sans-serif", size=12, color="#ffffff"),
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="rgba(255,255,255,0.6)")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="rgba(255,255,255,0.6)")
    ),
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11, color="#ffffff")
    )
)

st.plotly_chart(fig, use_container_width=True)

# Indicator Table Section
if indicators:
    render_subheader("Wskaźniki techniczne aktywów")
    ind_df = pd.DataFrame.from_dict(indicators, orient='index')
    
    # Format current price dynamically
    ind_df['Cena'] = ind_df.apply(lambda row: f"{row['current']:.4f}" if "USD/PLN" in row['name'] else f"{row['current']:.2f}", axis=1)
    
    ind_df = ind_df[['name', 'Cena', 'rsi', 'ema20_dist', 'sma200_dist']]
    ind_df.columns = ['Aktywo', 'Cena', 'RSI', 'EMA-20 %', 'SMA-200 %']

    def style_rsi(v):
        if v < 30: return 'background-color: #1a2e21; color: #cde200; font-weight: bold;'
        if v > 70: return 'background-color: #311414; color: #FF5C5C; font-weight: bold;'
        return 'color: rgba(255,255,255,0.9);'

    st.table(ind_df.style.format({
        'RSI': '{:.1f}',
        'EMA-20 %': '{:+.2f}%',
        'SMA-200 %': '{:+.2f}%'
    }).map(style_rsi, subset=['RSI']))

    # Table Legend / Oznaczenia kolorów
    st.markdown(
'<div style="margin-top: 12px; margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 20px; font-size: 13px; color: rgba(255,255,255,0.6); font-family: \'Poppins\', sans-serif;">'
'<span style="font-weight: 500; color: #ffffff;">Legenda kolorów (RSI):</span>'
'<span><span style="background-color: #1a2e21; color: #cde200; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 6px;">■</span> RSI &lt; 30 (Wyprzedanie - atrakcyjna cena zakupu)</span>'
'<span><span style="background-color: #311414; color: #FF5C5C; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 6px;">■</span> RSI &gt; 70 (Wykupienie - wysokie ryzyko korekty spadkowej)</span>'
'</div>',
        unsafe_allow_html=True
    )

# Footer
st.markdown(f'<div class="cxr-caption">Dane aktualizowane automatycznie co 5 minut. Ostatni odczyt: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
