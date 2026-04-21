import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="ZenJournal | Pro Trading Dashboard", page_icon="📈", layout="wide")

# --- TRADUCTION ---
LANG = {
    "Français": {
        "title": "ZENJOURNAL",
        "tagline": "L'alternative épurée à TradeZella • Accès à vie",
        "tab_dash": "📊 Dashboard",
        "tab_log": "📓 Journal & Log",
        "tab_pro": "👑 Upgrade",
        "stat_profit": "Profit Net",
        "stat_winrate": "Win Rate",
        "stat_factor": "Profit Factor",
        "stat_max_dd": "Max Drawdown",
        "journal_title": "Journal de Session",
        "journal_placeholder": "Quelles étaient tes émotions ? As-tu respecté tes règles ? Quelles leçons pour demain ?",
        "drop_zone": "Importer votre CSV Apex / Tradovate",
    },
    "English": {
        "title": "ZENJOURNAL",
        "tagline": "The sleek TradeZella alternative • Lifetime Access",
        "tab_dash": "📊 Dashboard",
        "tab_log": "📓 Journal & Log",
        "tab_pro": "👑 Upgrade",
        "stat_profit": "Net Profit",
        "stat_winrate": "Win Rate",
        "stat_factor": "Profit Factor",
        "stat_max_dd": "Max Drawdown",
        "journal_title": "Session Journal",
        "journal_placeholder": "How did you feel? Did you follow your rules? What are the lessons for tomorrow?",
        "drop_zone": "Import your Apex / Tradovate CSV",
    }
}

# --- SIDEBAR ---
lang = st.sidebar.selectbox("🌐 Language", ["English", "Français"])
t = LANG[lang]
st.sidebar.divider()
license_key = st.sidebar.text_input("🔑 License Key", type="password")
is_pro = (license_key == "PAYOUT-MASTER-2026")

# --- DESIGN CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #030303; color: #ffffff; }
    .kpi-card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .session-badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .ny { background-color: #1e3a8a; color: #60a5fa; }
    .ldn { background-color: #365314; color: #a3e635; }
    .asia { background-color: #4c1d95; color: #c084fc; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS UTILES ---
def get_session(hour):
    if 8 <= hour < 14: return "London 🇬🇧"
    elif 14 <= hour < 21: return "New York 🇺🇸"
    else: return "Asia/After 🇯🇵"

# --- HEADER ---
st.markdown(f"<h1 style='font-weight:800; font-size:3rem; margin:0;'>{t['title']}</h1>", unsafe_allow_html=True)
st.write(f"*{t['tagline']}*")

# --- TABS ---
tabs = st.tabs([t['tab_dash'], t['tab_log'], t['tab_pro']] if not is_pro else [t['tab_dash'], t['tab_log']])

# --- CHARGEMENT DATA ---
uploaded_file = st.file_uploader(t["drop_zone"], type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # Nettoyage colonnes
    col_pnl = [c for c in df.columns if 'profit' in c.lower() or 'pnl' in c.lower()][0]
    col_time = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()][0]
    
    df[col_time] = pd.to_datetime(df[col_time])
    df['hour'] = df[col_time].dt.hour
    df['session'] = df['hour'].apply(get_session)

    # --- TAB 1: DASHBOARD ---
    with tabs[0]:
        total_pnl = df[col_pnl].sum()
        win_rate = (len(df[df[col_pnl] > 0]) / len(df)) * 100
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t["stat_profit"], f"${total_pnl:,.2f}")
        c2.metric(t["stat_winrate"], f"{win_rate:.1f}%")
        c3.metric("Trades", len(df))
        c4.metric("Session Mode", df['session'].mode()[0])

        # Courbe d'équité Glow
        df['equity'] = df[col_pnl].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df['equity'], fill='tozeroy', line=dict(color='#00FF41', width=3), fillcolor='rgba(0,255,65,0.1)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False))
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: JOURNAL & LOG ---
    with tabs[1]:
        st.write(f"### {t['journal_title']}")
        
        # Zone de notes
        col_notes, col_rules = st.columns([2, 1])
        with col_notes:
            notes = st.text_area("Trading Notes", placeholder=t['journal_placeholder'], height=150)
        with col_rules:
            st.write("**Checklist**")
            st.checkbox("Respect du Stop Loss")
            st.checkbox("Attendu le Signal")
            st.checkbox("Pas d'Overtrading")

        st.divider()
        st.write("### 📝 Trade Log Detail")
        
        # Affichage du tableau propre
        display_df = df[[col_time, 'session', col_pnl]].copy()
        display_df.columns = ['Time', 'Session', 'P&L ($)']
        
        # Coloration stylée du tableau
        st.dataframe(display_df.style.format({'P&L ($)': '{:.2f}'}).applymap(
            lambda x: 'color: #00FF41' if x > 0 else 'color: #FF3366', subset=['P&L ($)']
        ), use_container_width=True)

# --- TAB PRO ---
if not is_pro:
    with tabs[2]:
        st.markdown("""
        <div style="text-align: center; padding: 40px; border: 1px solid #00FF41; border-radius: 20px;">
            <h2>DÉBLOQUER ZENJOURNAL PRO</h2>
            <p>Sauvegarde automatique • Multi-Comptes • Statistiques par Session</p>
            <h1 style="font-size: 3rem;">8.99$</h1>
            <p><i>Payez une fois, utilisez pour toujours.</i></p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🔥 DEVENIR PRO MAINTENANT", "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", type="primary", use_container_width=True)
