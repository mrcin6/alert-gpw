import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import numpy as np
from streamlit_autorefresh import st_autorefresh
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pytz

# --- Helper Functions (Module-Level) ---

def get_poland_time():
    return datetime.now(pytz.timezone('Europe/Warsaw'))

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    denominator = gain + loss
    # Zgodnie z ANALYSIS_RULES.md, unikanie dzielenia przez zero (RSI = 50 przy braku zmian)
    rsi = np.where(denominator > 0, 100.0 * gain / denominator, 50.0)
    return pd.Series(rsi, index=series.index)

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

@st.cache_data(ttl=300)
def get_market_data(tickers, period="2y", interval="1d"):
    data = yf.download(tickers, period=period, interval=interval, progress=False)
    if 'Close' in data:
        return data['Close']
    return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_lpp_stock_data():
    try:
        df = yf.Ticker("LPP.WA").history(period="5d")
        if not df.empty:
            return df
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_lpp_news():
    urls = [
        "https://news.google.com/rss/search?q=LPP+S.A.+gie%C5%82da+OR+akcje+OR+Reserved&hl=pl&gl=PL&ceid=PL:pl",
        "https://news.google.com/rss/search?q=%24LPP+GPW+OR+wycena&hl=pl&gl=PL&ceid=PL:pl"
    ]
    
    analyzer = SentimentIntensityAnalyzer()
    
    # Rozszerzenie i adaptacja słownika VADER pod kątem polskiego słownictwa finansowego i emoji (ANALYSIS_RULES.md)
    polish_lexicon = {
        "wzrost": 2.0,
        "wzrosty": 2.0,
        "sukces": 2.5,
        "zysk": 2.0,
        "zyski": 2.0,
        "hossa": 2.5,
        "lider": 2.0,
        "optymizm": 2.0,
        "rekord": 2.5,
        "rekordowe": 2.5,
        "ekspansja": 2.0,
        "dywidenda": 1.5,
        "debiut": 1.5,
        "rekomendacja": 1.5,
        "rekomenduje": 1.5,
        "kupuj": 2.0,
        "świetne": 2.5,
        "świetny": 2.5,
        "dobry": 1.5,
        "dobrze": 1.5,
        "ekspansję": 2.0,
        "spadek": -2.0,
        "spadki": -2.0,
        "kryzys": -2.5,
        "strata": -2.0,
        "straty": -2.0,
        "bessa": -2.5,
        "krach": -3.0,
        "panika": -2.5,
        "redukcja": -1.5,
        "pesymizm": -2.0,
        "kara": -2.0,
        "zarzuty": -2.0,
        "problem": -1.5,
        "problemy": -1.5,
        "ostrzeżenie": -1.5,
        "sprzedaj": -2.0,
        "słabe": -2.0,
        "słaby": -2.0,
        "złe": -2.0,
        "źle": -2.0,
        "wyprzedaż": -2.0,
        "załamanie": -2.5,
        "short": -2.0,
        "szort": -2.0,
        "fikcyjne": -1.5,
        "oskarżenia": -2.0,
        "zarzut": -2.0,
        "zatory": -1.5,
        "zaburzenia": -1.5,
        "gwałtowne": -1.0,
        "🚀": 3.0,
        "📈": 2.0,
        "💎": 2.0,
        "🏆": 2.5,
        "🔥": 2.0,
        "📉": -3.0,
        "🔴": -1.5,
        "💥": -2.0,
        "⚠️": -1.5,
        "💔": -2.0
    }
    analyzer.lexicon.update(polish_lexicon)

    articles = []
    seen_titles = set()

    for url in urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.title
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                published = getattr(entry, 'published', 'Brak daty')
                try:
                    parsed_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
                    published = parsed_date.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                    
                link = entry.link
                
                # Sentyment na podstawie zaktualizowanego VADER Analyzer
                vs = analyzer.polarity_scores(title)
                compound = vs['compound']
                
                if compound >= 0.05:
                    sentiment = "🟢 Pozytywny"
                elif compound <= -0.05:
                    sentiment = "🔴 Negatywny"
                else:
                    sentiment = "⚪ Neutralny"

                articles.append({
                    "Data opublikowania": published,
                    "Tytuł / Wzmianka": title,
                    "Ocena Sentymentu": sentiment,
                    "Score (Compound)": round(compound, 2),
                    "Link": link
                })
        except Exception as e:
            pass

    return pd.DataFrame(articles)

# --- Configuration & Styling ---
st.set_page_config(page_title="GPW Early Warning & LPP Dashboard", layout="wide")

# Automatyczne odświeżanie co 5 minut (300 000 ms)
st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    /* Global Typography & Background */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background-color: #131f33 !important;
        color: #ffffff !important;
    }

    /* Sidebar container and content */
    [data-testid="stSidebar"] {
        background-color: #111926 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #ffffff !important;
    }

    /* Tabs Styling Overrides */
    div[data-testid="stTabBar"] {
        background-color: #111926 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 16px 0 16px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-bottom: none !important;
    }
    button[data-testid="stTabBarTab"] {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.6) !important;
        font-size: 15px !important;
    }
    button[data-testid="stTabBarTab"][aria-selected="true"] {
        color: #ecfa64 !important;
        border-bottom-color: #ecfa64 !important;
        font-weight: 600 !important;
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
        background: linear-gradient(135deg, #1f2b40 0%, #172030 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px !important;
        border-left: 6px solid #DCDCDC !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .uxr-metric-card-positive { border-left-color: #2ecc71 !important; }
    .uxr-metric-card-informative { border-left-color: #5B8DEF !important; }
    .uxr-metric-card-negative { border-left-color: #FF5C5C !important; }
    .uxr-metric-card-alert { border-left-color: #FF9F43 !important; }
    .uxr-metric-card-neutral { border-left-color: #A0A0A0 !important; }

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
    .uxr-metric-delta-positive { color: #2ecc71 !important; }
    .uxr-metric-delta-negative { color: #FF5C5C !important; }
    .uxr-metric-delta-neutral { color: #A0A0A0 !important; }

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
        border-left-color: #2ecc71 !important;
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
        background-color: #ecfa64;
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
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        border-bottom: 2px solid rgba(255,255,255,0.05) !important;
        font-size: 14px !important;
    }
    div[data-testid="stTable"] td {
        color: rgba(255,255,255,0.9) !important;
        padding: 14px 18px !important;
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
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
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
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
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
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
            padding: 4px 6px !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Global Streamlit widget bottom margin reduction */
        [data-testid="element-container"] {
            margin-bottom: 4px !important;
        }
        
        /* Column gap and margin reduction */
        div[data-testid="column"] {
            margin-bottom: 4px !important;
        }
        
        /* Header Group Styles */
        .cxr-header-group {
            flex-direction: column !important;
            text-align: center !important;
            padding: 8px 10px !important;
            gap: 4px !important;
            margin-bottom: 8px !important;
        }
        .cxr-emojicon {
            width: 30px !important;
            height: 30px !important;
            font-size: 16px !important;
        }
        .cxr-title {
            font-size: 18px !important;
        }
        .cxr-neon-highlight {
            margin-left: 0 !important;
            margin-top: 2px !important;
            font-size: 10px !important;
            padding: 1px 4px !important;
        }
        .cxr-subtitle {
            font-size: 11px !important;
            margin-top: 2px !important;
        }

        /* Metric Cards Optimization */
        .uxr-metric-card {
            padding: 8px 12px !important;
            min-height: 80px !important;
            margin-bottom: 4px !important;
        }
        .uxr-metric-value {
            font-size: 18px !important;
        }
        .uxr-metric-title {
            font-size: 11px !important;
            margin-bottom: 2px !important;
        }
        .uxr-metric-delta {
            font-size: 9px !important;
            margin-top: 1px !important;
        }

        /* Alert Banner Optimization */
        .cxr-alert {
            padding: 8px 10px !important;
            font-size: 10px !important;
            margin-bottom: 8px !important;
        }

        /* Subheader Optimization */
        .cxr-subheader-text {
            font-size: 12px !important;
        }
        .cxr-subheader-bar {
            height: 10px !important;
        }

        /* Tables Responsive behavior */
        div[data-testid="stTable"] {
            overflow-x: auto !important;
            display: block !important;
            width: 100% !important;
        }
        div[data-testid="stTable"] th, div[data-testid="stTable"] td {
            padding: 6px 8px !important;
            font-size: 12px !important;
        }

        /* Expander overrides */
        div[data-testid="stExpander"] summary {
            padding: 8px 12px !important;
            font-size: 11px !important;
        }
        div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            padding: 12px !important;
        }

        /* Column-nested expanders overrides */
        div[data-testid="column"] div[data-testid="stExpander"] {
            margin-bottom: 4px !important;
        }
        div[data-testid="column"] div[data-testid="stExpander"] summary {
            padding: 6px 10px !important;
            font-size: 10px !important;
        }
        div[data-testid="column"] div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            padding: 8px 10px !important;
            font-size: 10px !important;
        }

        /* Guide Card inside Expander */
        .cxr-guide-box {
            min-height: auto !important;
            margin-bottom: 12px !important;
            padding: 10px !important;
        }

        /* Responsive spacer helper */
        .st-spacer-mobile {
            display: none !important;
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

# --- Global Data Preparation ---

# Pobieranie RSS News globalnie, aby ułatwić integrację z panelem bocznym (sidebar)
try:
    df_lpp_news_global = fetch_lpp_news()
except Exception:
    df_lpp_news_global = pd.DataFrame()

# ==========================================
# PANEL BOCZNY (st.sidebar)
# ==========================================
st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px; padding-top: 10px;">
        <h2 style="color: #ecfa64; font-size: 20px; font-weight: 600; margin-bottom: 4px; font-family: 'Poppins', sans-serif;">Alert GPW</h2>
        <p style="color: rgba(255,255,255,0.6); font-size: 11px; margin: 0; font-family: 'Poppins', sans-serif;">System Wczesnego Ostrzegania</p>
    </div>
    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
""", unsafe_allow_html=True)

if not df_lpp_news_global.empty:
    st.sidebar.markdown("""
        <p style="font-size: 11px; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; color: rgba(255,255,255,0.6); margin-bottom: 12px; font-family: 'Poppins', sans-serif;">
            🛍️ Wzmianki LPP S.A.
        </p>
    """, unsafe_allow_html=True)
    
    # Wyświetlamy do 8 najnowszych nagłówków ze wskaźnikami wizualnymi
    for _, row in df_lpp_news_global.head(8).iterrows():
        emoji = "🟢" if "Pozytywny" in row["Ocena Sentymentu"] else ("🔴" if "Negatywny" in row["Ocena Sentymentu"] else "⚪")
        border_color = '#2ecc71' if 'Pozytywny' in row['Ocena Sentymentu'] else ('#FF5C5C' if 'Negatywny' in row['Ocena Sentymentu'] else '#A0A0A0')
        
        st.sidebar.markdown(f"""
            <div style="background-color: #1f2b40; padding: 10px; border-radius: 6px; border-left: 4px solid {border_color}; margin-bottom: 8px;">
                <div style="font-size: 10px; color: rgba(255,255,255,0.4); margin-bottom: 4px; font-family: 'Poppins', sans-serif;">{row['Data opublikowania']}</div>
                <div style="font-size: 12px; color: #ffffff; line-height: 1.4; font-family: 'Poppins', sans-serif;">{emoji} {row['Tytuł / Wzmianka']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
        <p style="font-size: 12px; color: rgba(255,255,255,0.5); font-family: 'Poppins', sans-serif; text-align: center;">
            Brak nowych wzmianek dla LPP S.A.
        </p>
    """, unsafe_allow_html=True)


# ==========================================
# GŁÓWNA STRONA - STRUKTURA ZAKŁADEK
# ==========================================

tab_risk, tab_lpp = st.tabs(["📊 Globalny Risk-Off (GPW)", "🛍️ LPP S.A. - Sentyment & News"])


# ==========================================
# ZAKŁADKA 1: GLOBALNY RISK-OFF
# ==========================================
with tab_risk:
    # --- UI Rendering Nagłówek (Serial Position Effect) ---
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
                ⏱️ {get_poland_time().strftime('%H:%M:%S')}
            </div>
        """, unsafe_allow_html=True)

    # --- App Logic & Controls (Fitts's & Hick's Law) ---
    ctrl_cols = st.columns([3, 1])
    with ctrl_cols[0]:
        time_range = st.radio(
            "Przedział czasowy analizy",
            ["Ostatnie 72 godziny (Widok godzinowy)", "Ostatnie 30 dni (Widok dzienny)"],
            horizontal=True,
            label_visibility="visible"
        )
    with ctrl_cols[1]:
        st.markdown("<div style='height: 10px;' class='st-spacer-mobile'></div>", unsafe_allow_html=True)
        if st.button("🔄 Odśwież dane", use_container_width=True, key="refresh_risk"):
            st.cache_data.clear()
            st.toast("Notowania i sentyment zostały zaktualizowane!", icon="🔄")
            st.rerun()
        st.caption(f"Aktualizacja: {get_poland_time().strftime('%H:%M:%S')}")

    if "Ostatnie 72 godziny" in time_range:
        fetch_period = "1mo"
        interval = "1h"
        display_rows = 72
    else:
        fetch_period = "2y"
        interval = "1d"
        display_rows = 30

    tickers_map = {
        "WIG20.WA": "WIG20",
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

    # Obliczenie wskaźników z uwzględnieniem zasad matematycznych (ANALYSIS_RULES.md)
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
            
            change_24h = 0.0
            change_72h = 0.0
            if len(series) >= abs(idx_24):
                val_24 = series.iloc[idx_24]
                if val_24 > 0:
                    change_24h = ((current_price / val_24) - 1) * 100
            if len(series) >= abs(idx_72):
                val_72 = series.iloc[idx_72]
                if val_72 > 0:
                    change_72h = ((current_price / val_72) - 1) * 100
            
            indicators[t_id] = {
                "name": name,
                "current": current_price,
                "rsi": rsi_val,
                "ema20_dist": ((current_price / ema20) - 1) * 100 if ema20 > 0 else 0.0,
                # Zabezpieczenie przed zerowaniem i NaN dla SMA-200 (ANALYSIS_RULES.md)
                "sma200_dist": ((current_price / sma200) - 1) * 100 if (not np.isnan(sma200) and sma200 > 0) else 0.0,
                "change_24h": change_24h,
                "change_72h": change_72h
            }

    # --- UI Rendering ---

    # Sentyment & Alerty rynkowe zgodnie z regułami polityki ryzyka (strategy.json)
    cnn_score, cnn_rating = fetch_sentiment_cnn()
    crypto_score, crypto_rating = fetch_sentiment_crypto()

    sp500_ch_24 = indicators.get("^GSPC", {}).get("change_24h", 0.0)
    sp500_ch_72 = indicators.get("^GSPC", {}).get("change_72h", 0.0)
    btc_ch_72 = indicators.get("BTC-USD", {}).get("change_72h", 0.0)
    wig20_ch_24 = indicators.get("WIG20.WA", {}).get("change_24h", 0.0)
    usdpln_ch_24 = indicators.get("USDPLN=X", {}).get("change_24h", 0.0)
    gold_ch_24 = indicators.get("GC=F", {}).get("change_24h", 0.0)

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

    # Kafle KPI z zachowaniem kolorów obramowania i stylów UXR
    cols = st.columns(4)

    # 1. Kafel CNN Fear & Greed
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

    # 2. Kafel Crypto Fear & Greed
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

    # 3. Kafel WIG20
    wig_val = indicators.get("WIG20.WA", {"current": 0.0, "change_24h": 0.0})
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

    # 4. Kafel USD/PLN
    usd_val = indicators.get("USDPLN=X", {"current": 0.0, "change_24h": 0.0})
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

    # --- Educational Legend & Guide (Consolidated / Law of Proximity) ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ Przewodnik: Jak interpretować wskaźniki, sentyment i czytać wykres?"):
        # Podział na sekcje edukacyjne
        edu_tabs = st.tabs(["📊 Sentyment i Aktywa", "🚨 System Alertów", "📈 Jak czytać wykres?", "🔍 Wskaźniki Techniczne"])
        
        with edu_tabs[0]:
            st.markdown("""
            ### 📊 Interpretacja Kluczowych Wskaźników Sentymentu i Rynku:
            
            1. **Sentyment S&P 500 (CNN Fear & Greed Index)**
               - **0-25 (Ekstremalny strach)**: Okazja zakupowa, rynek nadmiernie wyprzedany.
               - **25-45 (Strach)**: Niepokój i podwyższone ryzyko korekty.
               - **45-55 (Neutralny)**: Brak wyraźnego kierunku rynkowego.
               - **55-75 (Chciwość)**: Silny optymizm rynkowy, ostrożne zakupy.
               - **75-100 (Ekstremalna chciwość)**: Wysokie ryzyko przegrzania rynku i nagłej korekty spadkowej.
            
            2. **Sentyment Kryptowalut (Crypto Fear & Greed Index)**
               - Mierzy zmienność, wolumen, media społecznościowe i dominację Bitcoina. Zakresy interpretujemy analogicznie do indeksu CNN, przy czym rynek krypto charakteryzuje się znacznie wyższą dynamiką nagłych zwrotów akcji.
            
            3. **Indeks WIG20 (Polski rynek)**
               - Reprezentuje 20 największych i najbardziej płynnych spółek na GPW. Wzrost oznacza napływ kapitału (hossa), spadek to schłodzenie nastrojów inwestycyjnych (bessa).
            
            4. **Kurs USD/PLN (Wskaźnik Risk-Off)**
               - Główny barometr przepływu kapitału zagranicznego na rynki wschodzące. 
               - **Wzrost kursu (osłabienie PLN)**: Kapitał ucieka z Polski (złe wieści dla GPW, ryzyko wyprzedaży akcji).
               - **Spadek kursu (umocnienie PLN)**: Kapitał napływa do Polski (bardze dobre wieści dla notowań GPW).
            """)
            
        with edu_tabs[1]:
            st.markdown("""
            ### 🚨 Metodologia Wyznaczania Alertów Rynkowych (Risk Engine)
            
            Ogólny stan systemu (werdykt ostrzegawczy na samej górze strony) wyznaczany jest automatycznie na podstawie korelacji rynków globalnych, lokalnych wskaźników płynności i indeksów behawioralnych.
            
            - **🟢 Poziom 0: Stabilne Otoczenie (Green - Normal/Stable)**
              - **Kryterium**: Wszystkie rynki bazowe i lokalne zachowują się stabilnie, mieszcząc się w granicach standardowej zmienności. Brak sygnałów odpływu kapitału.
            
            - **⚠️ Poziom 1: Ostrzeżenie Globalne (Yellow - Warning)**
              - **Kryteria (dowolne z nich)**:
                1. Spadek amerykańskiego indeksu **S&P 500** o ponad **-1.5%** w ciągu 24 godzin.
                2. Sentyment **CNN Fear & Greed** spada poniżej **30 pkt** (strefa silnego strachu na Wall Street).
                3. Cena bezpiecznego aktywa (**Złoto**) rośnie o ponad **+1.5%** w 24h, przy jednoczesnych spadkach na S&P 500.
              - **Uzasadnienie**: Redukcja ryzyka (de-risking) przez globalne instytucje w USA z opóźnieniem uderza w rynki wschodzące, w tym GPW.
            
            - **🟠 Poziom 2: Ryzyko Lokalne / Odpływ Kapitału (Orange - Local Risk)**
              - **Kryterium (zajście jednoczesne)**:
                - Polski indeks **WIG20** spada o ponad **-1.5%** w 24h, **oraz**
                - Kurs dolara do złotego (**USD/PLN**) rośnie o ponad **+1.0%** w 24h.
              - **Uzasadnienie**: Klasyczny symptom wycofywania funduszy przez kapitał zagraniczny. Wyprzedaż polskich akcji (spadek WIG20) i jednoczesna zamiana złotówek na dolary (wzrost USD/PLN).
            
            - **🔴 Poziom 3: Krytyczne Ryzyko / Globalny Risk-Off (Red - Critical Risk)**
              - **Kryteria (dowolne z nich)**:
                1. Jednoczesny, głęboki spadek indeksu **S&P 500** oraz **Bitcoina** o ponad **-2.5%** w ciągu ostatnich 72 godzin.
                2. Sentyment **CNN Fear & Greed** spada poniżej **20 pkt** (skrajna panika na Wall Street).
                3. Sentyment kryptowalut (**Crypto Fear & Greed**) spada poniżej **20 pkt**.
              - **Uzasadnienie**: Masowa, międzyaktywowa kapitulacja rynkowa (cross-asset liquidation). Brak płynności na rynkach wywołuje spadki na GPW niezależnie od lokalnych fundamentów spółek.
            """)
            
        with edu_tabs[2]:
            st.markdown("""
            ### 📈 Jak czytać wykres znormalizowany?
            
            Wykres domyślnie pokazuje ceny w **skali znormalizowanej (%)**. Oznacza to, że wszystkie aktywa zaczynają z tego samego punktu odniesienia (**100%** na początku wybranego okresu).
            
            Dzięki temu możesz bezpośrednio porównywać dynamikę wzrostów i spadków np. Bitcoina, indeksu S&P 500 oraz WIG20, ignorując fakt, że jedno kosztuje tysiące dolarów, a drugie kilka złotych.
            
            *Przykład: Wartość 105% oznacza wzrost o 5% od początku okresu, a 95% oznacza spadek o 5%. Odznaczenie pola wyboru pod wykresem przywróci ceny nominalne.*
            """)
            
        with edu_tabs[3]:
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
                    '<div class="cxr-guide-box" style="background-color: #131f33; padding: 18px; border-radius: 6px; border-left: 4px solid #2ecc71;">'
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

    # Sekcja Wykresu Głównego
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
            
            # Normalizacja ceny chronologicznie do punktu startowego 100% (ANALYSIS_RULES.md)
            if norm_chart:
                y_data = (y_data / (y_data.iloc[0] if y_data.iloc[0] > 0 else 1.0)) * 100
            
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
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#ffffff")
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Sekcja Tabeli Wskaźników Technicznych
    if indicators:
        render_subheader("Wskaźniki techniczne aktywów")
        ind_df = pd.DataFrame.from_dict(indicators, orient='index')
        
        # Dynamiczne formatowanie ceny w zależności od klasy aktywa
        ind_df['Cena'] = ind_df.apply(lambda row: f"{row['current']:.4f}" if "USD/PLN" in row['name'] else f"{row['current']:.2f}", axis=1)
        
        ind_df = ind_df[['name', 'Cena', 'rsi', 'ema20_dist', 'sma200_dist']]
        ind_df.columns = ['Aktywo', 'Cena', 'RSI', 'EMA-20 %', 'SMA-200 %']

        def style_rsi(v):
            if v < 30: return 'background-color: #1a2e21; color: #2ecc71; font-weight: bold;'
            if v > 70: return 'background-color: #311414; color: #FF5C5C; font-weight: bold;'
            return 'color: rgba(255,255,255,0.9);'

        st.table(ind_df.style.format({
            'RSI': '{:.1f}',
            'EMA-20 %': '{:+.2f}%',
            'SMA-200 %': '{:+.2f}%'
        }).map(style_rsi, subset=['RSI']))

        # Legenda Tabeli
        st.markdown(
            '<div style="margin-top: 12px; margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 20px; font-size: 13px; color: rgba(255,255,255,0.6); font-family: \'Poppins\', sans-serif;">'
            '<span style="font-weight: 500; color: #ffffff;">Legenda kolorów (RSI):</span>'
            '<span><span style="background-color: #1a2e21; color: #2ecc71; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 6px;">■</span> RSI &lt; 30 (Wyprzedanie - atrakcyjna cena zakupu)</span>'
            '<span><span style="background-color: #311414; color: #FF5C5C; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 6px;">■</span> RSI &gt; 70 (Wykupienie - wysokie ryzyko korekty spadkowej)</span>'
            '</div>',
            unsafe_allow_html=True
        )


# ==========================================
# ZAKŁADKA 2: LPP S.A. - SENTYMENT & NEWS
# ==========================================
with tab_lpp:
    # Header Group dla LPP S.A. (Symmetrical Layout / Law of Similarity)
    header_col1_lpp, header_col2_lpp = st.columns([4, 1])
    with header_col1_lpp:
        st.markdown(f"""
            <div class="cxr-header-group">
                <div class="cxr-emojicon">🛍️</div>
                <div class="cxr-header-text">
                    <h1 class="cxr-title">Monitor Sentymentu <span class="cxr-neon-highlight">LPP S.A.</span></h1>
                    <p class="cxr-subtitle">Analiza NLP wzmianek prasowych i nagłówków giełdowych ($LPP)</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with header_col2_lpp:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 24px; color: rgba(255,255,255,0.6); font-size: 14px; font-weight: 500;">
                ⏱️ {get_poland_time().strftime('%H:%M:%S')}
            </div>
        """, unsafe_allow_html=True)

    # Pasek kontrolny dla LPP S.A.
    ctrl_cols_lpp = st.columns([3, 1])
    with ctrl_cols_lpp[0]:
        st.markdown("<p style='color: rgba(255,255,255,0.6); font-size: 14px; margin-top: 6px; font-family: \"Poppins\", sans-serif;'>Automatyczny skan RSS prasowy i giełdowy (Google News)</p>", unsafe_allow_html=True)
    with ctrl_cols_lpp[1]:
        if st.button("🔄 Odśwież LPP", use_container_width=True, key="refresh_lpp"):
            st.cache_data.clear()
            st.toast("Wiadomości i kurs LPP zostały zaktualizowane!", icon="🔄")
            st.rerun()
        st.caption(f"Aktualizacja: {get_poland_time().strftime('%H:%M:%S')}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Notowania giełdowe LPP S.A. dla kontekstu (z użyciem cachowanej metody)
    try:
        lpp_stock = fetch_lpp_stock_data()
        if not lpp_stock.empty:
            last_lpp_price = lpp_stock['Close'].iloc[-1]
            prev_lpp_price = lpp_stock['Close'].iloc[-2]
            lpp_pct = ((last_lpp_price - prev_lpp_price) / prev_lpp_price) * 100
            
            lpp_border = "positive" if lpp_pct >= 0 else "negative"
            lpp_delta_color = "positive" if lpp_pct >= 0 else "negative"
            lpp_delta_sign = "+" if lpp_pct >= 0 else ""
            
            st.markdown(render_metric_card(
                "Kurs LPP S.A. (GPW)",
                f"{last_lpp_price:,.2f} PLN",
                f"{lpp_delta_sign}{lpp_pct:.2f}% (Sesja dzienna)",
                delta_color=lpp_delta_color,
                border_type=lpp_border
            ), unsafe_allow_html=True)
    except Exception as e:
        st.info("Pobieranie notowań LPP S.A. tymczasowo niedostępne.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Użycie pobranego globalnie zbioru wiadomości LPP
    df_lpp_news = df_lpp_news_global

    if not df_lpp_news.empty:
        # Podsumowanie statystyczne rozkładu sentymentu
        pos_cnt = (df_lpp_news["Ocena Sentymentu"] == "🟢 Pozytywny").sum()
        neu_cnt = (df_lpp_news["Ocena Sentymentu"] == "⚪ Neutralny").sum()
        neg_cnt = (df_lpp_news["Ocena Sentymentu"] == "🔴 Negatywny").sum()
        total_cnt = len(df_lpp_news)

        render_subheader("Podsumowanie sentymentu NLP")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(render_metric_card("Pobrane wpisy", f"{total_cnt}", "Baza nagłówków RSS", "positive", "informative"), unsafe_allow_html=True)
        with col_m2:
            st.markdown(render_metric_card("Pozytywne", f"{pos_cnt}", "Sygnały bycze (NLP)", "positive", "positive"), unsafe_allow_html=True)
        with col_m3:
            st.markdown(render_metric_card("Neutralne", f"{neu_cnt}", "Równowaga informacyjna", "positive", "neutral"), unsafe_allow_html=True)
        with col_m4:
            st.markdown(render_metric_card("Negatywne", f"{neg_cnt}", "Sygnały niedźwiedzie (NLP)", "negative", "negative"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        render_subheader("Najnowsze nagłówki i wzmianki o LPP S.A.")
        
        # Ujednolicona tabela w stylu UXR z aktywnymi hiperłączami (Law of Similarity / Miller's Law)
        df_lpp_display = df_lpp_news.head(15).copy()
        
        # Funkcja do stylizowania wierszy pod kątem sentymentu (zielony dla pozytywnego, czerwony dla negatywnego)
        def style_sentiment(val):
            if "Pozytywny" in val: return "color: #2ecc71; font-weight: 600;"
            if "Negatywny" in val: return "color: #FF5C5C; font-weight: 600;"
            return "color: rgba(255,255,255,0.7);"

        # Przygotowanie hiperłącza w formacie HTML
        df_lpp_display['Odnośnik'] = df_lpp_display['Link'].apply(lambda x: f'<a href="{x}" target="_blank" style="color: #ecfa64; text-decoration: none; font-weight: 500;">Otwórz artykuł ↗</a>')
        
        df_lpp_table = df_lpp_display[["Data opublikowania", "Tytuł / Wzmianka", "Ocena Sentymentu", "Odnośnik"]]
        
        # Generowanie kodu HTML tabeli z zachowaniem klasy stylu
        html_table = df_lpp_table.style.map(style_sentiment, subset=["Ocena Sentymentu"]).to_html(index=False, escape=False)
        
        # Renderowanie wewnątrz stylizowanego bloku Streamlit stTable
        st.markdown(f'<div data-testid="stTable">{html_table}</div>', unsafe_allow_html=True)
    else:
        st.info("Brak nowych wzmianek dla LPP S.A. w tym momencie.")

# --- Global Footer ---
st.markdown(f'<div class="cxr-caption">Dane aktualizowane automatycznie co 5 minut. Ostatni odczyt: {get_poland_time().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
