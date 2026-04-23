import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="ZenJournal | Backtest Engine", page_icon="🧪", layout="wide")

# --- DESIGN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #ffffff; font-family: 'Inter', sans-serif; }
    .kpi-card { background: #0f0f0f; border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; text-align: center; }
    .stat-val { font-size: 1.8rem; font-weight: 800; color: #00FF41; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #555; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #00FF41 !important; border-bottom-color: #00FF41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES DONNÉES EN MÉMOIRE ---
if 'bt_data' not in st.session_state:
    st.session_state.bt_data = pd.DataFrame(columns=['Date', 'Setup', 'PnL ($)', 'Notes'])

st.markdown("<h1 style='font-size: 3rem; letter-spacing: -2px;'>LABORATOIRE DE BACKTEST<span style='color:#00FF41;'>.</span></h1>", unsafe_allow_html=True)
st.write("Identifie tes setups les plus rentables avant de les trader en réel.")
st.write("---")

col1, col2 = st.columns([1, 2])

# --- COLONNE GAUCHE : AJOUT DE TRADES MANUEL ---
with col1:
    st.write("### 📝 Ajouter un Trade")
    with st.form("add_trade_form", clear_on_submit=True):
        date = st.date_input("Date du Trade (Simulée)", datetime.today())
        setup = st.selectbox("Nom du Setup", ["Breakout Open", "Rejet VWAP", "Trendline Bounce", "Cassure Range", "Autre"])
        pnl = st.number_input("P&L du Trade ($)", value=0.0, step=10.0)
        notes = st.text_area("Notes / Capture d'écran (lien)", placeholder="Ex: Belle confirmation volume, mais sorti un peu tôt...")
        
        submitted = st.form_submit_button("➕ Ajouter au Backtest")
        
        if submitted:
            new_trade = pd.DataFrame([{'Date': date, 'Setup': setup, 'PnL ($)': pnl, 'Notes': notes}])
            st.session_state.bt_data = pd.concat([st.session_state.bt_data, new_trade], ignore_index=True)
            st.success("Trade ajouté !")

    # Option pour vider le backtest
    if not st.session_state.bt_data.empty:
        if st.button("🗑️ Effacer le Backtest", type="primary"):
            st.session_state.bt_data = pd.DataFrame(columns=['Date', 'Setup', 'PnL ($)', 'Notes'])
            st.rerun()

# --- COLONNE DROITE : RÉSULTATS & ANALYSE ---
with col2:
    df = st.session_state.bt_data
    
    if df.empty:
        st.info("👈 Commence par ajouter tes trades de backtest à gauche pour voir les statistiques.")
    else:
        # Calculs
        total_pnl = df['PnL ($)'].sum()
        win_trades = df[df['PnL ($)'] > 0]
        loss_trades = df[df['PnL ($)'] <= 0]
        win_rate = (len(win_trades) / len(df)) * 100 if len(df) > 0 else 0
        
        # Affichage KPI
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='kpi-card'><p style='color:#666'>P&L TOTAL</p><p class='stat-val' style='color: {'#00FF41' if total_pnl >= 0 else '#FF3366'}'>${total_pnl:,.2f}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card'><p style='color:#666'>WIN RATE</p><p class='stat-val'>{win_rate:.1f}%</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='kpi-card'><p style='color:#666'>TRADES TESTÉS</p><p class='stat-val'>{len(df)}</p></div>", unsafe_allow_html=True)

        st.write("---")
        
        # Onglets de graphiques
        tab_eq, tab_setup, tab_log = st.tabs(["📈 Courbe d'Équité", "🎯 Performance par Setup", "📓 Journal détaillé"])
        
        with tab_eq:
            df['Cumulative PnL'] = df['PnL ($)'].cumsum()
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(y=df['Cumulative PnL'], mode='lines+markers', line=dict(color='#00FF41', width=3), fill='tozeroy', fillcolor='rgba(0, 255, 65, 0.1)'))
            fig_eq.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Nombre de Trades", yaxis_title="Profit ($)")
            st.plotly_chart(fig_eq, use_container_width=True)
            
        with tab_setup:
            # Graphique très TradeZella : Quel setup rapporte le plus ?
            setup_pnl = df.groupby('Setup')['PnL ($)'].sum().reset_index()
            fig_setup = px.bar(setup_pnl, x='Setup', y='PnL ($)', color='PnL ($)', color_continuous_scale=['#FF3366', '#00FF41'])
            fig_setup.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_setup, use_container_width=True)
            
        with tab_log:
            # Tableau de tous les trades
            st.dataframe(df.style.applymap(lambda x: 'color: #00FF41' if isinstance(x, (int, float)) and x > 0 else ('color: #FF3366' if isinstance(x, (int, float)) and x < 0 else ''), subset=['PnL ($)']), use_container_width=True)

            # Export CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Sauvegarder ce Backtest (CSV)", data=csv, file_name='mon_backtest.csv', mime='text/csv')
