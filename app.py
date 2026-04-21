import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ZenJournal | Pro Trading Dashboard", page_icon="📈", layout="wide")

# --- SYSTÈME DE TRADUCTION ---
LANG = {
    "Français": {
        "title": "ZENJOURNAL",
        "tagline": "L'alternative épurée à TradeZella • Accès à vie",
        "stats_header": "PERFORMANCES GLOBALES",
        "chart_equity": "COURBE DE CROISSANCE",
        "chart_dist": "RÉPARTITION",
        "chart_entries": "🎯 CARTE DES TRADES (POINTS D'ENTRÉE)",
        "stat_profit": "Profit Net",
        "stat_winrate": "Win Rate",
        "stat_factor": "Profit Factor",
        "stat_avg_win": "Gain Moyen",
        "stat_avg_loss": "Perte Moyenne",
        "stat_max_dd": "Max Drawdown",
        "drop_zone": "Importer votre CSV (Tradovate / Rithmic / Apex)"
    },
    "English": {
        "title": "ZENJOURNAL",
        "tagline": "The sleek TradeZella alternative • Lifetime Access",
        "stats_header": "OVERALL PERFORMANCE",
        "chart_equity": "EQUITY GROWTH",
        "chart_dist": "DISTRIBUTION",
        "chart_entries": "🎯 TRADE MAP (ENTRY POINTS)",
        "stat_profit": "Net Profit",
        "stat_winrate": "Win Rate",
        "stat_factor": "Profit Factor",
        "stat_avg_win": "Avg Win",
        "stat_avg_loss": "Avg Loss",
        "stat_max_dd": "Max Drawdown",
        "drop_zone": "Import your CSV (Tradovate / Rithmic / Apex)"
    }
}

# --- BARRE LATÉRALE ---
lang = st.sidebar.selectbox("🌐 Language", ["English", "Français"])
t = LANG[lang]
st.sidebar.divider()
license_key = st.sidebar.text_input("🔑 License Key", type="password")
is_pro = (license_key == "PAYOUT-MASTER-2026")

# --- DESIGN CSS ULTRA PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    [data-testid="stAppViewContainer"] { 
        background-color: #030303; 
        color: #ffffff; 
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] { 
        background-color: #080808; 
        border-right: 1px solid #151515; 
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -2px;
        color: #ffffff;
        font-size: 3.5rem;
        margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(0, 255, 65, 0.2);
    }
    
    .kpi-card {
        background: linear-gradient(145deg, #0a0a0a, #111111);
        border: 1px solid #1a1a1a;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        border-color: #00FF41;
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 255, 65, 0.15);
    }
    .kpi-title { color: #666; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    .kpi-value { color: #fff; font-size: 2rem; font-weight: 800; margin: 0; }
    .kpi-value.green { color: #00FF41; }
    .kpi-value.red { color: #FF3366; }
    </style>
    """, unsafe_allow_html=True)

def render_kpi(title, value, color_class=""):
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value {color_class}">{value}</div>
    </div>
    """

# --- HEADER ---
st.markdown(f"<h1 class='main-title'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #888; margin-top:-10px; font-size: 1.1rem;'>{t['tagline']}</p>", unsafe_allow_html=True)
st.write("---")

# --- NAVIGATION ---
if is_pro:
    tab_list = ["📊 Dashboard Analytics"]
else:
    tab_list = ["📊 Dashboard Analytics", "👑 Upgrade to PRO"]
tabs = st.tabs(tab_list)

# --- ONGLET 1 : ANALYTICS ---
with tabs[0]:
    uploaded_file = st.file_uploader(t["drop_zone"], type="csv")
    
    if uploaded_file:
        if not is_pro:
            if 'first_file' not in st.session_state:
                st.session_state.first_file = uploaded_file.name
            elif st.session_state.first_file != uploaded_file.name:
                st.error("✨ Free tier limit reached. Please upgrade to PRO to analyze multiple accounts.")
                st.stop()

        df = pd.read_csv(uploaded_file)
        
        # Identification dynamique des colonnes
        col_pnl = [c for c in df.columns if 'profit' in c.lower() or 'pnl' in c.lower()][0]
        
        # --- CALCULS KPI ---
        total_pnl = df[col_pnl].sum()
        win_trades = df[df[col_pnl] > 0][col_pnl]
        loss_trades = df[df[col_pnl] < 0][col_pnl]
        
        win_rate = (len(win_trades) / len(df)) * 100 if len(df) > 0 else 0
        p_factor = abs(win_trades.sum() / loss_trades.sum()) if loss_trades.sum() != 0 else 0
        avg_win = win_trades.mean() if not win_trades.empty else 0
        avg_loss = loss_trades.mean() if not loss_trades.empty else 0
        
        equity = df[col_pnl].cumsum()
        peak = equity.cummax()
        drawdown = (peak - equity).max()

        color_pnl = "green" if total_pnl >= 0 else "red"
        
        # --- AFFICHAGE KPI ---
        st.markdown(f"<h3 style='color:white; margin-bottom: 20px;'>{t['stats_header']}</h3>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(render_kpi(t["stat_profit"], f"${total_pnl:,.2f}", color_pnl), unsafe_allow_html=True)
        with c2: st.markdown(render_kpi(t["stat_winrate"], f"{win_rate:.1f}%", "green" if win_rate > 50 else ""), unsafe_allow_html=True)
        with c3: st.markdown(render_kpi(t["stat_factor"], f"{p_factor:.2f}", "green" if p_factor > 1 else ""), unsafe_allow_html=True)
        with c4: st.markdown(render_kpi(t["stat_max_dd"], f"${drawdown:,.2f}", "red"), unsafe_allow_html=True)
        
        st.write("") 
        c5, c6, c7, c8 = st.columns(4)
        with c5: st.markdown(render_kpi(t["stat_avg_win"], f"${avg_win:,.2f}", "green"), unsafe_allow_html=True)
        with c6: st.markdown(render_kpi(t["stat_avg_loss"], f"${avg_loss:,.2f}", "red"), unsafe_allow_html=True)
        with c7: st.markdown(render_kpi("Total Trades", len(df)), unsafe_allow_html=True)
        with c8: st.markdown(render_kpi("Ratio R:R", f"{abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "0"), unsafe_allow_html=True)

        st.write("---")

        # --- GRAPHIQUES LIGNE 1 ---
        col_left, col_right = st.columns([2.5, 1])
        
        with col_left:
            st.markdown(f"<h4 style='color:#ccc;'>{t['chart_equity']}</h4>", unsafe_allow_html=True)
            df['equity_curve'] = df[col_pnl].cumsum()
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(y=df['equity_curve'], mode='lines', line=dict(color='#00FF41', width=3), fill='tozeroy', fillcolor='rgba(0, 255, 65, 0.1)'))
            fig_eq.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(visible=False), yaxis=dict(showgrid=True, gridcolor='#111', color="#888"))
            st.plotly_chart(fig_eq, use_container_width=True)

        with col_right:
            st.markdown(f"<h4 style='color:#ccc;'>{t['chart_dist']}</h4>", unsafe_allow_html=True)
            fig_hist = px.histogram(df, x=col_pnl, nbins=25, color_discrete_sequence=['#00FF41'])
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(color="#888"), yaxis=dict(visible=False))
            st.plotly_chart(fig_hist, use_container_width=True)

        st.write("---")

        # --- NOUVEAU GRAPHIQUE : CARTE DES TRADES ---
        st.markdown(f"<h4 style='color:#ccc;'>{t['chart_entries']}</h4>", unsafe_allow_html=True)
        try:
            # Cherche la colonne de temps et de prix
            col_time = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()][0]
            col_price = [c for c in df.columns if 'price' in c.lower()][-1] # Généralement 'Fill Price' ou 'Price'
            
            # Formate le temps pour l'axe X
            df[col_time] = pd.to_datetime(df[col_time])
            
            # Couleurs des points selon gain ou perte
            point_colors = ['#00FF41' if val > 0 else '#FF3366' for val in df[col_pnl]]
            
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=df[col_time],
                y=df[col_price],
                mode='markers',
                marker=dict(size=8, color=point_colors, line=dict(width=1, color='#000')),
                text=df[col_pnl].apply(lambda x: f"PnL: ${x:.2f}"), # Bulle info au survol
                name='Trades'
            ))
            
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#111', color="#888", title="Heure du Trade"),
                yaxis=dict(showgrid=True, gridcolor='#111', color="#888", title="Prix d'exécution", tickformat=".2f"),
                hovermode="closest",
                height=400
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        except Exception as e:
            st.info("💡 Ton fichier CSV ne contient pas de colonne 'Time' ou 'Price' claire pour tracer la carte des trades.")

# --- ONGLET 2 : UPGRADE ---
if not is_pro:
    with tabs[1]:
        st.markdown("""
            <div style="text-align: center; padding: 60px 20px; border: 1px solid #222; border-radius: 20px; background: linear-gradient(180deg, #0a0a0a, #000000);">
                <h1 style="color: #00FF41; margin-bottom: 5px;">ZENJOURNAL PRO</h1>
                <p style="font-size: 1.2rem; color: #888;">Stop renting your data. Own your journal.</p>
                <div style="margin: 30px 0;">
                    <span style="font-size: 4rem; font-weight: 900; color: white;">$8.99</span>
                    <span style="color: #666; font-size: 1.5rem;"> / lifetime</span>
                </div>
                <div style="display: flex; justify-content: center; gap: 40px; color: #bbb; text-align: left; margin-bottom: 40px;">
                    <div><p>✅ <b>Unlimited</b> CSV Imports</p><p>✅ <b>Multi-Account</b> Support</p></div>
                    <div><p>✅ <b>Advanced</b> Risk Metrics</p><p>✅ <b>Zero</b> Monthly Subscriptions</p></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🔥 UNLOCK LIFETIME ACCESS NOW", "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", type="primary", use_container_width=True)
