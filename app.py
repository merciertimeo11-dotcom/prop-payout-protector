import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
st.set_page_config(page_title="ZenJournal | Minimalist Trading Log", page_icon="📈", layout="wide")

# --- MÉMOIRE ---
if 'history' not in st.session_state:
    st.session_state.history = None

# --- TRADUCTIONS ---
LANG = {
    "Français": {
        "title": "📈 ZenJournal",
        "subtitle": "L'alternative minimaliste aux abonnements coûteux.",
        "license": "Code d'activation PRO",
        "support": "📩 Support : proppayoutprotector@gmail.com",
        "drop": "Glisse ton CSV Tradovate / Rithmic ici",
        "stat_profit": "Profit Net",
        "stat_winrate": "Win Rate",
        "stat_trades": "Total Trades",
        "stat_factor": "Profit Factor",
        "chart_title": "Courbe d'Équité (Performance)",
        "pro_title": "👑 Passe en ZenJournal PRO",
        "pro_desc": "Marre de payer 30$/mois ? Débloque l'import illimité pour toujours.",
        "buy_btn": "🔥 ACCÈS À VIE (8.99$)",
        "limit_msg": "✨ Version gratuite : 1 import réussi. Passe en PRO pour gérer ton journal quotidiennement."
    },
    "English": {
        "title": "📈 ZenJournal",
        "subtitle": "The minimalist alternative to expensive subscriptions.",
        "license": "PRO Activation Code",
        "support": "📩 Support: proppayoutprotector@gmail.com",
        "drop": "Drop your Tradovate / Rithmic CSV here",
        "stat_profit": "Net Profit",
        "stat_winrate": "Win Rate",
        "stat_trades": "Total Trades",
        "stat_factor": "Profit Factor",
        "chart_title": "Equity Curve (Performance)",
        "pro_title": "👑 Upgrade to ZenJournal PRO",
        "pro_desc": "Tired of $30/month subscriptions? Unlock unlimited imports forever.",
        "buy_btn": "🔥 LIFETIME ACCESS ($8.99)",
        "limit_msg": "✨ Free tier: 1 import successful. Upgrade to PRO to journal your trades daily."
    }
}

# --- SIDEBAR ---
lang = st.sidebar.selectbox("🌐 Language", ["English", "Français"])
t = LANG[lang]

st.sidebar.divider()
license_key = st.sidebar.text_input(t["license"], type="password")
is_pro = (license_key == "PAYOUT-MASTER-2026")

st.sidebar.markdown(f"<div style='font-size:0.8em; color:gray; margin-top:100px;'>{t['support']}</div>", unsafe_allow_html=True)

# --- STYLE CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #050505; }
    .stMetric { background-color: #111; border: 1px solid #222; border-radius: 10px; padding: 15px; }
    .premium-card { border: 1px solid #00C805; padding: 30px; border-radius: 15px; background: linear-gradient(145deg, #0a0a0a, #111); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- MAIN UI ---
st.title(t["title"])
st.markdown(f"<p style='color:gray;'>{t['subtitle']}</p>", unsafe_allow_html=True)

if not is_pro:
    tab1, tab2 = st.tabs(["📊 Dashboard", t["pro_title"]])
else:
    tab1 = st.tabs(["📊 Dashboard"])[0]

with tab1:
    uploaded_file = st.file_uploader(t["drop"], type="csv")
    
    if uploaded_file:
        # Check Limits for Free Users
        if not is_pro:
            if 'last_file' in st.session_state and st.session_state.last_file != uploaded_file.name:
                st.warning(t["limit_msg"])
                st.link_button(t["buy_btn"], "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", type="primary")
                st.stop()
            st.session_state.last_file = uploaded_file.name

        # Process Data
        df = pd.read_csv(uploaded_file)
        col_profit = [c for c in df.columns if 'profit' in c.lower() or 'pnl' in c.lower()][0]
        
        # Stats
        total_pnl = df[col_profit].sum()
        wins = df[df[col_profit] > 0][col_profit]
        losses = df[df[col_profit] < 0][col_profit]
        win_rate = (len(wins) / len(df)) * 100 if len(df) > 0 else 0
        profit_factor = abs(wins.sum() / losses.sum()) if losses.sum() != 0 else 0
        
        # Metrics Row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t["stat_profit"], f"{total_pnl:,.2f} $", delta=None)
        c2.metric(t["stat_winrate"], f"{win_rate:.1f}%")
        c3.metric(t["stat_trades"], len(df))
        c4.metric(t["stat_factor"], f"{profit_factor:.2f}")
        
        # Equity Curve
        st.subheader(t["chart_title"])
        df['equity'] = df[col_profit].cumsum()
        st.area_chart(df['equity'], color="#00C805")

# --- PRO TAB ---
if not is_pro:
    with tab2:
        st.markdown(f"""
        <div class='premium-card'>
            <h2 style='color:white;'>ZenJournal PRO</h2>
            <p style='color:#888;'>Stop paying monthly for your data.</p>
            <div style='margin: 20px 0;'>
                <span style='font-size: 2.5em; font-weight: bold; color: #00C805;'>$8.99</span>
                <span style='color: gray;'> / lifetime</span>
            </div>
            <div style='text-align: left; display: inline-block; color: #ddd; margin-bottom: 20px;'>
                ✅ <b>Unlimited</b> CSV Imports<br>
                ✅ <b>Detailed</b> Performance Metrics<br>
                ✅ <b>Priority</b> Email Support<br>
                ✅ <b>Zero</b> Monthly Fees
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button(t["buy_btn"], "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", use_container_width=True, type="primary")
