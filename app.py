import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px # Pour des graphiques plus pro

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ZenJournal | Pro Trading Dashboard", page_icon="📈", layout="wide")

# --- SYSTÈME DE TRADUCTION ---
LANG = {
    "Français": {
        "title": "ZENJOURNAL",
        "tagline": "L'alternative épurée à TradeZella • Accès à vie",
        "stats_header": "PERFORMANCES GLOBALES",
        "chart_equity": "COURBE DE CROISSANCE ($)",
        "chart_dist": "DISTRIBUTION DES TRADES",
        "stat_profit": "Profit Net",
        "stat_winrate": "Taux de Victoire",
        "stat_factor": "Profit Factor",
        "stat_avg_win": "Gain Moyen",
        "stat_avg_loss": "Perte Moyenne",
        "stat_max_dd": "Max Drawdown",
        "pro_banner": "PASSER EN VERSION PRO (8.99$ UNUNIQUE)",
        "drop_zone": "Importer votre CSV (Tradovate / Rithmic / Apex)",
        "footer": "📩 Support Premium : proppayoutprotector@gmail.com"
    },
    "English": {
        "title": "ZENJOURNAL",
        "tagline": "The sleek TradeZella alternative • Lifetime Access",
        "stats_header": "OVERALL PERFORMANCE",
        "chart_equity": "EQUITY GROWTH ($)",
        "chart_dist": "TRADE DISTRIBUTION",
        "stat_profit": "Net Profit",
        "stat_winrate": "Win Rate",
        "stat_factor": "Profit Factor",
        "stat_avg_win": "Avg Win",
        "stat_avg_loss": "Avg Loss",
        "stat_max_dd": "Max Drawdown",
        "pro_banner": "UPGRADE TO PRO ($8.99 ONCE)",
        "drop_zone": "Import your CSV (Tradovate / Rithmic / Apex)",
        "footer": "📩 Premium Support: proppayoutprotector@gmail.com"
    }
}

# --- BARRE LATÉRALE ---
lang = st.sidebar.selectbox("🌐 Language", ["English", "Français"])
t = LANG[lang]
st.sidebar.divider()
license_key = st.sidebar.text_input("🔑 License Key", type="password")
is_pro = (license_key == "PAYOUT-MASTER-2026")

# --- DESIGN CSS "TRADEZELLA STYLE" ---
st.markdown(f"""
    <style>
    /* Fond noir profond */
    [data-testid="stAppViewContainer"] {{ background-color: #050505; color: #ffffff; }}
    [data-testid="stSidebar"] {{ background-color: #0a0a0a; border-right: 1px solid #1a1a1a; }}
    
    /* Titre stylé */
    .main-title {{
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -2px;
        background: -webkit-linear-gradient(#fff, #555);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0px;
    }}
    
    /* Cartes de Metrics */
    div[data-testid="stMetric"] {{
        background-color: #0f0f0f;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        transition: transform 0.2s;
    }}
    div[data-testid="stMetric"]:hover {{
        border: 1px solid #00FF41;
        transform: translateY(-5px);
    }}
    
    /* Boutons */
    .stButton>button {{
        background: linear-gradient(90deg, #00FF41, #00A329);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 25px;
        width: 100%;
    }}
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{
        color: #555;
        font-weight: bold;
    }}
    .stTabs [aria-selected="true"] {{
        color: #00FF41 !important;
        border-bottom-color: #00FF41 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"<h1 class='main-title'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #666; margin-top:-10px;'>{t['tagline']}</p>", unsafe_allow_html=True)

# --- NAVIGATION ---
if is_pro:
    tab_list = ["📊 Analytics"]
else:
    tab_list = ["📊 Analytics", "👑 Upgrade"]
tabs = st.tabs(tab_list)

# --- ONGLET ANALYTICS ---
with tabs[0]:
    uploaded_file = st.file_uploader(t["drop_zone"], type="csv")
    
    if uploaded_file:
        # Logique de limite gratuite
        if not is_pro:
            if 'first_file' not in st.session_state:
                st.session_state.first_file = uploaded_file.name
            elif st.session_state.first_file != uploaded_file.name:
                st.error("✨ Limit reached. Upgrade to PRO for unlimited analysis.")
                st.stop()

        # Lecture des données
        df = pd.read_csv(uploaded_file)
        col_pnl = [c for c in df.columns if 'profit' in c.lower() or 'pnl' in c.lower()][0]
        
        # --- CALCULS AVANCÉS ---
        total_pnl = df[col_pnl].sum()
        win_trades = df[df[col_pnl] > 0][col_pnl]
        loss_trades = df[df[col_pnl] < 0][col_pnl]
        
        win_rate = (len(win_trades) / len(df)) * 100 if len(df) > 0 else 0
        p_factor = abs(win_trades.sum() / loss_trades.sum()) if loss_trades.sum() != 0 else 0
        avg_win = win_trades.mean() if not win_trades.empty else 0
        avg_loss = loss_trades.mean() if not loss_trades.empty else 0
        
        # Calcul Drawdown
        equity = df[col_pnl].cumsum()
        peak = equity.cummax()
        drawdown = (equity - peak).min()

        # --- AFFICHAGE DES METRICS (Style TradeZella) ---
        st.write(f"### {t['stats_header']}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(t["stat_profit"], f"${total_pnl:,.0f}", delta=f"{total_pnl:,.0f}", delta_color="normal")
        m2.metric(t["stat_winrate"], f"{win_rate:.1f}%")
        m3.metric(t["stat_factor"], f"{p_factor:.2f}")
        m4.metric(t["stat_max_dd"], f"${drawdown:,.0f}", delta_color="inverse")
        
        st.write("")
        m5, m6, m7, m8 = st.columns(4)
        m5.metric(t["stat_avg_win"], f"${avg_win:,.0f}")
        m6.metric(t["stat_avg_loss"], f"${avg_loss:,.0f}")
        m7.metric("Total Trades", len(df))
        m8.metric("Ratio R:R", f"{abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "0")

        # --- GRAPHIQUES ---
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.write(f"#### {t['chart_equity']}")
            df['equity_curve'] = df[col_pnl].cumsum()
            st.area_chart(df['equity_curve'], color="#00FF41")

        with col_right:
            st.write(f"#### {t['chart_dist']}")
            # Petit histogramme stylé
            fig = px.histogram(df, x=col_pnl, nbins=20, color_discrete_sequence=['#00FF41'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False, height=250)
            st.plotly_chart(fig, use_container_width=True)

# --- ONGLET UPGRADE ---
if not is_pro:
    with tabs[1]:
        st.markdown(f"""
            <div style="text-align: center; padding: 50px; border: 1px solid #222; border-radius: 20px; background: #0a0a0a;">
                <h2 style="color: #00FF41;">ZENJOURNAL PRO</h2>
                <p style="font-size: 1.2rem; color: #888;">Owned by you. No subscriptions. No limits.</p>
                <div style="margin: 40px 0;">
                    <span style="font-size: 3rem; font-weight: bold;">$8.99</span>
                    <span style="color: gray;"> / one-time</span>
                </div>
                <ul style="text-align: left; display: inline-block; list-style: none; padding: 0; color: #ccc; line-height: 2;">
                    <li>✅ <b>Unlimited</b> CSV Analysis</li>
                    <li>✅ <b>Multi-Account</b> Support</li>
                    <li>✅ <b>Advanced</b> Risk Metrics (Drawdown, R:R)</li>
                    <li>✅ <b>Priority</b> Feature Requests</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🔥 GET LIFETIME ACCESS", "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", type="primary")

# --- FOOTER ---
st.sidebar.markdown(f"<div style='margin-top: 150px; text-align: center; color: #444; font-size: 0.8rem;'>{t['footer']}</div>", unsafe_allow_html=True)
