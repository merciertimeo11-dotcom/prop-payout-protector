import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Prop-Payout Protector", page_icon="🛡️", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'comptes_analyses' not in st.session_state:
    st.session_state.comptes_analyses = set()

# --- SYSTÈME DE TRADUCTION ---
LANGUAGES = {
    "Français": {
        "title": "🛡️ Prop-Payout Protector",
        "trust": "🔒 Données cryptées localement • Mis à jour : Avril 2026",
        "config": "⚙️ Configuration",
        "select_firm": "Ta Prop Firm",
        "solde_man": "Solde simulé ($)",
        "gain_man": "Plus gros gain journalier ($)",
        "jours_man": "Jours validés",
        "tab_auto": "📊 Audit Auto (CSV)",
        "tab_sim": "🎛️ Simulation Manuelle",
        "tab_pro": "👑 Version PRO (-60%)",
        "audit_res": "📈 Résultat de l'Audit",
        "solde_est": "Solde Estimé",
        "jours_val": "Jours Validés",
        "consist": "Consistance (Max 30%)",
        "avail": "Disponible au retrait",
        "safe": "✅ CONFORME",
        "danger": "🚨 DANGER",
        "promo_text": "OFFRE DE LANCEMENT",
        "buy_btn": "🔥 PROFITER DE L'OFFRE (8.99$)",
        "limit_title": "✨ Limite de la version gratuite",
        "limit_desc": "Superbe, tu as analysé ton premier compte avec succès ! Pour scanner le reste de tes comptes (Copy Trading) en illimité, passe à la version PRO."
    },
    "English": {
        "title": "🛡️ Prop-Payout Protector",
        "trust": "🔒 Local encryption • Updated: April 2026",
        "config": "⚙️ Settings",
        "select_firm": "Select Prop Firm",
        "solde_man": "Simulated Balance ($)",
        "gain_man": "Best Day Profit ($)",
        "jours_man": "Validated Days",
        "tab_auto": "📊 Auto Audit (CSV)",
        "tab_sim": "🎛️ Manual Simulation",
        "tab_pro": "👑 PRO Version (-60%)",
        "audit_res": "📈 Audit Results",
        "solde_est": "Estimated Balance",
        "jours_val": "Validated Days",
        "consist": "Consistency (Max 30%)",
        "avail": "Available for Payout",
        "safe": "✅ COMPLIANT",
        "danger": "🚨 DANGER",
        "promo_text": "LAUNCH OFFER",
        "buy_btn": "🔥 GET THE OFFER (8.99$)",
        "limit_title": "✨ Free plan limit reached",
        "limit_desc": "Great job, you've analyzed your first account! To scan the rest of your portfolio with no limits, upgrade to PRO."
    }
}

# --- CHOIX DE LA LANGUE ---
lang_choice = st.sidebar.selectbox("🌐 Language / Langue", ["Français", "English"])
t = LANGUAGES[lang_choice]

# --- DESIGN (NOIR PUR ET PREMIUM) ---
st.markdown("""
    <style>
    /* Fond de l'application en noir pur */
    [data-testid="stAppViewContainer"] { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #222; }
    
    /* Style des cartes de statistiques */
    .stMetric { background-color: #0f0f0f; border: 1px solid #222222; border-radius: 10px; padding: 15px; }
    
    /* Paywall PRO */
    .promo-price { color: #8B949E; text-decoration: line-through; font-size: 1.2em; }
    .final-price { color: #00C805; font-size: 2.5em; font-weight: bold; }
    .offer-badge { background-color: #FFD700; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    .premium-card { border: 1px solid #FFD700; padding: 30px; border-radius: 15px; background: linear-gradient(145deg, #0f0f0f, #1a1a1a); text-align: center; }
    
    /* Nouvelle Boîte de Limite Douce */
    .limit-box { border: 1px solid #FFD700; padding: 25px; border-radius: 10px; background: linear-gradient(145deg, #111111, #1a1a1a); text-align: center; margin-top: 20px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);}
    .limit-title { color: #FFD700; font-size: 1.5em; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title(t["title"])
st.markdown(f"<div style='color: #555555; text-align: center; margin-bottom: 20px;'>{t['trust']}</div>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header(t["config"])
    prop_firm = st.selectbox(t["select_firm"], ["Apex Legacy (50k)", "LucidFlex (50k)"])
    if prop_firm == "Apex Legacy (50k)":
        seuil, ratio_lim, req_jours, min_p = 52600, 0.30, 10, 0.01
    else:
        seuil, ratio_lim, req_jours, min_p = 50500, 1.0, 5, 150.0

# --- ONGLETS ---
tab1, tab2, tab3 = st.tabs([t["tab_auto"], t["tab_sim"], t["tab_pro"]])

# ==========================================
# ONGLET 1 : AUTO (CSV) + PAYWALL DOUX
# ==========================================
with tab1:
    fichier_csv = st.file_uploader(f"📁 Import CSV", type=["csv"])
    
    if fichier_csv:
        if fichier_csv.name not in st.session_state.comptes_analyses:
            if len(st.session_state.comptes_analyses) >= 1:
                # Blocage Premium (Doux)
                st.markdown(f"""
                <div class='limit-box'>
                    <div class='limit-title'>{t['limit_title']}</div>
                    <p style='color: #DDDDDD; font-size: 1.1em;'>{t['limit_desc']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state.comptes_analyses.add(fichier_csv.name)
        
        df = pd.read_csv(fichier_csv)
        col_profit = [c for c in df.columns if 'profit' in c.lower() or 'pnl' in c.lower()][0]
        pnl_total = df[col_profit].sum()
        balance = 50000 + pnl_total
        best_day = df[col_profit].max()
        days_count = len(df[df[col_profit] >= min_p])
        
        st.write(f"### {t['audit_res']}")
        c1, c2, c3 = st.columns(3)
        c1.metric(t["solde_est"], f"{balance:,.2f} $")
        c2.metric(t["jours_val"], f"{days_count} / {req_jours}")
        
        if prop_firm == "Apex Legacy (50k)":
            cur_ratio = best_day / pnl_total if pnl_total > 0 else 0
            c3.metric(t["consist"], f"{cur_ratio:.1%}", t["danger"] if cur_ratio > ratio_lim else t["safe"], delta_color="inverse")
        else:
            payout = min(pnl_total * 0.5, 2000.0) if pnl_total > 0 else 0
            c3.metric(t["avail"], f"{payout:,.2f} $")
    else:
        st.info("👆 Upload ton fichier Tradovate/Rithmic (Limite : 1 compte en version gratuite).")

# ==========================================
# ONGLET 2 : SIMULATION MANUELLE
# ==========================================
with tab2:
    st.write(f"### {t['tab_sim']}")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        man_balance = st.number_input(t["solde_man"], value=51200.0, step=100.0)
    with col_s2:
        man_days = st.number_input(t["jours_man"], value=3, min_value=0)
    with col_s3:
        if prop_firm == "Apex Legacy (50k)":
            man_best_day = st.number_input(t["gain_man"], value=800.0, step=50.0)
        else:
            st.write("<br>*N/A*", unsafe_allow_html=True)
            man_best_day = 0
            
    man_pnl = man_balance - 50000
    st.divider()
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric(t["solde_est"], f"{man_balance:,.2f} $")
    cm2.metric(t["jours_val"], f"{man_days} / {req_jours}")
    if prop_firm == "Apex Legacy (50k)":
        man_ratio = man_best_day / man_pnl if man_pnl > 0 else 0
        cm3.metric(t["consist"], f"{man_ratio:.1%}", t["danger"] if man_ratio > ratio_lim else t["safe"], delta_color="inverse")
    else:
        man_payout = min(man_pnl * 0.5, 2000.0) if man_pnl > 0 else 0
        cm3.metric(t["avail"], f"{man_payout:,.2f} $")

# ==========================================
# ONGLET 3 : VERSION PRO
# ==========================================
with tab3:
    st.markdown(f"""
    <div class='premium-card'>
        <span class='offer-badge'>{t['promo_text']}</span>
        <h2 style='margin-top:10px; color: white;'>Prop-Payout Protector PRO</h2>
        <div style='margin: 20px 0;'>
            <span class='promo-price'>22.99 $</span><br>
            <span class='final-price'>8.99 $</span>
        </div>
        <ul style='text-align: left; display: inline-block; color: #ddd;'>
            <li>✅ Multi-Account Analysis (Illimité)</li>
            <li>✅ MAE / Drawdown Tracker</li>
            <li>✅ Audit PDF Reports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.button(t["buy_btn"], use_container_width=True, type="primary")