import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Prop-Payout Protector", page_icon="🛡️", layout="wide")

# --- MÉMOIRE & SÉCURITÉ ---
if 'comptes_analyses' not in st.session_state:
    st.session_state.comptes_analyses = set()

# --- SYSTÈME DE TRADUCTION ---
LANGUAGES = {
    "Français": {
        "title": "🛡️ Prop-Payout Protector",
        "trust": "🔒 Données cryptées localement • Mis à jour : Avril 2026",
        "config": "⚙️ Configuration",
        "license_label": "Code PRO (Reçu par email)",
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
        "buy_btn": "🔥 DEVENIR PRO (8.99$)",
        "limit_title": "✨ Limite version gratuite",
        "limit_desc": "Analyse de 1 compte réussie ! Pour débloquer l'accès illimité (Multi-Accounts), passe à la version PRO."
    },
    "English": {
        "title": "🛡️ Prop-Payout Protector",
        "trust": "🔒 Local encryption • Updated: April 2026",
        "config": "⚙️ Settings",
        "license_label": "PRO License Key",
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
        "buy_btn": "🔥 UPGRADE TO PRO (8.99$)",
        "limit_title": "✨ Free tier limit",
        "limit_desc": "First account analyzed! To unlock unlimited Multi-Account analysis, upgrade to PRO."
    }
}

# --- BARRE LATÉRALE ---
lang_choice = st.sidebar.selectbox("🌐 Language", ["Français", "English"])
t = LANGUAGES[lang_choice]

st.sidebar.divider()
license_key = st.sidebar.text_input(t["license_label"], type="password")
is_pro = (license_key == "PAYOUT-MASTER-2026")

# --- DESIGN ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #222; }
    .stMetric { background-color: #0f0f0f; border: 1px solid #222222; border-radius: 10px; padding: 15px; }
    .promo-price { color: #8B949E; text-decoration: line-through; font-size: 1.2em; }
    .final-price { color: #00C805; font-size: 2.5em; font-weight: bold; }
    .offer-badge { background-color: #FFD700; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    .premium-card { border: 1px solid #FFD700; padding: 30px; border-radius: 15px; background: linear-gradient(145deg, #0f0f0f, #1a1a1a); text-align: center; }
    .limit-box { border: 1px solid #FFD700; padding: 25px; border-radius: 10px; background: #0a0a0a; text-align: center; margin-top: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title(t["title"])
st.markdown(f"<div style='color: #444; text-align: center;'>{t['trust']}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header(t["config"])
    prop_firm = st.selectbox(t["select_firm"], ["Apex Legacy (50k)", "LucidFlex (50k)"])
    if prop_firm == "Apex Legacy (50k)":
        seuil, ratio_lim, req_jours, min_p = 52600, 0.30, 10, 0.01
    else:
        seuil, ratio_lim, req_jours, min_p = 50500, 1.0, 5, 150.0

# --- NAVIGATION ---
if is_pro:
    tabs = st.tabs([t["tab_auto"], t["tab_sim"]])
else:
    tabs = st.tabs([t["tab_auto"], t["tab_sim"], t["tab_pro"]])

# --- ONGLET 1 : AUTO ---
with tabs[0]:
    fichier_csv = st.file_uploader(f"📁 Import CSV", type=["csv"])
    if fichier_csv:
        if not is_pro and fichier_csv.name not in st.session_state.comptes_analyses:
            if len(st.session_state.comptes_analyses) >= 1:
                st.markdown(f"<div class='limit-box'><div style='color:#FFD700;font-size:1.5em;'>{t['limit_title']}</div><p>{t['limit_desc']}</p></div>", unsafe_allow_html=True)
                st.link_button(t["buy_btn"], "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", use_container_width=True, type="primary")
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
            ratio = best_day / pnl_total if pnl_total > 0 else 0
            c3.metric(t["consist"], f"{ratio:.1%}", t["danger"] if ratio > ratio_lim else t["safe"], delta_color="inverse")
        else:
            payout = min(pnl_total * 0.5, 2000.0) if pnl_total > 0 else 0
            c3.metric(t["avail"], f"{payout:,.2f} $")

# --- ONGLET 2 : SIMU ---
with tabs[1]:
    st.write(f"### {t['tab_sim']}")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: mb = st.number_input(t["solde_man"], value=51200.0)
    with col_s2: md = st.number_input(t["jours_man"], value=3)
    with col_s3: mbd = st.number_input(t["gain_man"], value=800.0) if prop_firm == "Apex Legacy (50k)" else 0
    
    st.divider()
    mpnl = mb - 50000
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric(t["solde_est"], f"{mb:,.2f} $")
    cm2.metric(t["jours_val"], f"{md} / {req_jours}")
    if prop_firm == "Apex Legacy (50k)":
        mr = mbd / mpnl if mpnl > 0 else 0
        cm3.metric(t["consist"], f"{mr:.1%}", t["danger"] if mr > ratio_lim else t["safe"], delta_color="inverse")
    else:
        ma = min(mpnl * 0.5, 2000.0) if mpnl > 0 else 0
        cm3.metric(t["avail"], f"{ma:,.2f} $")

# --- ONGLET 3 : PRO ---
if not is_pro:
    with tabs[2]:
        st.markdown(f"""
        <div class='premium-card'>
            <span class='offer-badge'>{t['promo_text']}</span>
            <h2 style='color:white;'>Prop-Payout Protector PRO</h2>
            <div style='margin: 20px 0;'>
                <span class='promo-price'>22.99 $</span><br>
                <span class='final-price'>8.99 $</span>
            </div>
            <ul style='text-align: left; display: inline-block; color: #ddd;'>
                <li>✅ Multi-Account Analysis (Unlimited)</li>
                <li>✅ Deep Consistency Audit</li>
                <li>✅ Lifetime Access</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button(t["buy_btn"], "https://buy.stripe.com/28E7sF4LycwD34Vgr7co000", use_container_width=True, type="primary")
