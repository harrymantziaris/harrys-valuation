import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
from datetime import datetime
import os, base64, warnings
warnings.filterwarnings("ignore")
np.random.seed(42)

st.set_page_config(page_title="Harrys Valuation", page_icon="H", layout="wide")

# ── Load Data ──
DATA_DIR = "."
bulker    = pd.read_csv(os.path.join(DATA_DIR, "00_bulker_vessel_values.csv"))
tanker    = pd.read_csv(os.path.join(DATA_DIR, "01_tanker_vessel_values.csv"))
container = pd.read_csv(os.path.join(DATA_DIR, "02_container_vessel_values.csv"))
gas       = pd.read_csv(os.path.join(DATA_DIR, "03_gas_vessel_values.csv"))
charter   = pd.read_csv(os.path.join(DATA_DIR, "04_charter_rates.csv"))
opex_df   = pd.read_csv(os.path.join(DATA_DIR, "05_opex_benchmarks.csv"))

# ── Taxonomy ──
VESSEL_TAXONOMY = {
    "Bulker": {
        "Capesize (180k DWT)": {"nb":"bulk_capesize_182k_nb_usdm","resale":"bulk_capesize_182k_resale_usdm","scrap":"bulk_capesize_scrap_usdm","dwt":180000,"ages":{"5":"bulk_capesize_180k_5yr_usdm","10":"bulk_capesize_182k_10yr_usdm","15":"bulk_capesize_180k_15yr_usdm","20":"bulk_capesize_177k_20yr_usdm"},"tc1yr":"tc_bulk_capesize_180k_1yr_atl_usdday","tc3yr":"tc_bulk_capesize_180k_3yr_atl_usdday","tcHist":"tc_bulk_capesize_hist_1yr_usdday","opex":"opex_bulk_capesize_usdday","fuel_noneco":38,"fuel_eco":25,"scrubber_eligible":True},
        "Kamsarmax (82k DWT)": {"nb":"bulk_kamsarmax_82k_nb_usdm","resale":"bulk_kamsarmax_82k_resale_usdm","scrap":"bulk_panamax_scrap_usdm","dwt":82000,"ages":{"5":"bulk_kamsarmax_82k_5yr_usdm","10":"bulk_kamsarmax_82k_10yr_usdm","15":"bulk_kamsarmax_82k_15yr_usdm"},"tc1yr":"tc_bulk_kamsarmax_82k_1yr_atl_usdday","tc3yr":"tc_bulk_kamsarmax_82k_3yr_atl_usdday","tcHist":"tc_bulk_panamax_hist_1yr_usdday","opex":"opex_bulk_panamax_usdday","fuel_noneco":28,"fuel_eco":20,"scrubber_eligible":True},
        "Panamax (76k DWT)": {"nb":"bulk_panamax_76k_nb_usdm","resale":"bulk_panamax_76k_resale_usdm","scrap":"bulk_panamax_scrap_usdm","dwt":76000,"ages":{"5":"bulk_panamax_76k_5yr_usdm","10":"bulk_kamsarmax_82k_10yr_usdm","15":"bulk_kamsarmax_82k_15yr_usdm","20":"bulk_panamax_76k_20yr_usdm"},"tc1yr":"tc_bulk_panamax_76k_1yr_atl_usdday","tc3yr":"tc_bulk_panamax_76k_3yr_atl_usdday","tcHist":"tc_bulk_panamax_hist_1yr_usdday","opex":"opex_bulk_panamax_usdday","fuel_noneco":27,"fuel_eco":19,"scrubber_eligible":True},
        "Ultramax (63k DWT)": {"nb":"bulk_ultramax_63k_nb_usdm","resale":"bulk_ultramax_63k_resale_usdm","scrap":"bulk_handymax_scrap_usdm","dwt":63000,"ages":{"5":"bulk_ultramax_63k_5yr_usdm","10":"bulk_ultramax_61k_10yr_usdm"},"tc1yr":"tc_bulk_ultramax_61k_1yr_atl_usdday","tc3yr":"tc_bulk_ultramax_61k_3yr_pac_usdday","tcHist":"tc_bulk_supramax_hist_1yr_usdday","opex":"opex_bulk_handymax_usdday","fuel_noneco":24,"fuel_eco":17,"scrubber_eligible":True},
        "Handysize (38k DWT)": {"nb":"bulk_handysize_40k_nb_usdm","resale":"bulk_handysize_40k_resale_usdm","scrap":"bulk_handysize_scrap_usdm","dwt":38000,"ages":{"5":"bulk_handysize_38k_5yr_usdm","10":"bulk_handysize_37k_10yr_usdm","15":"bulk_handysize_33k_15yr_usdm","20":"bulk_handysize_32k_20yr_usdm"},"tc1yr":"tc_bulk_handymax_45k_1yr_usdday","tc3yr":"tc_bulk_handymax_45k_3yr_usdday","tcHist":"tc_bulk_supramax_hist_1yr_usdday","opex":"opex_bulk_handysize_usdday","fuel_noneco":18,"fuel_eco":13,"scrubber_eligible":True},
    },
    "Tanker": {
        "VLCC (300k DWT)": {"nb":None,"resale":"tanker_vlcc_300k_resale_usdm","scrap":None,"dwt":300000,"ages":{"5":"tanker_vlcc_300k_5yr_usdm","10":"tanker_vlcc_300k_10yr_usdm","15":"tanker_vlcc_300k_15yr_usdm"},"tc1yr":"tc_tanker_suezmax_150k_1yr_usdday","tc3yr":"tc_tanker_suezmax_150k_3yr_usdday","tcHist":"tc_tanker_suezmax_hist_1yr_usdday","opex":"opex_tanker_vlcc_usdday","fuel_noneco":55,"fuel_eco":38,"scrubber_eligible":True},
        "Suezmax (158k DWT)": {"nb":None,"resale":"tanker_suezmax_160k_resale_usdm","scrap":None,"dwt":158000,"ages":{"5":"tanker_suezmax_160k_5yr_usdm","10":"tanker_suezmax_158k_10yr_usdm","15":"tanker_suezmax_158k_15yr_usdm"},"tc1yr":"tc_tanker_suezmax_150k_1yr_usdday","tc3yr":"tc_tanker_suezmax_150k_3yr_usdday","tcHist":"tc_tanker_suezmax_hist_1yr_usdday","opex":"opex_tanker_suezmax_usdday","fuel_noneco":40,"fuel_eco":28,"scrubber_eligible":True},
        "Aframax/LR2 (115k DWT)": {"nb":None,"resale":"tanker_aframax_115k_resale_usdm","scrap":None,"dwt":115000,"ages":{"5":"tanker_aframax_115k_5yr_usdm","10":"tanker_aframax_115k_10yr_usdm","15":"tanker_aframax_115k_15yr_usdm"},"tc1yr":"tc_tanker_lr2_115k_1yr_usdday","tc3yr":"tc_tanker_lr2_115k_3yr_usdday","tcHist":"tc_tanker_suezmax_hist_1yr_usdday","opex":"opex_tanker_aframax_lr2_usdday","fuel_noneco":32,"fuel_eco":23,"scrubber_eligible":True},
        "MR (50k DWT)": {"nb":None,"resale":"tanker_mr_51k_resale_usdm","scrap":None,"dwt":50000,"ages":{"5":"tanker_mr_51k_5yr_usdm","10":"tanker_mr_50k_10yr_usdm","15":"tanker_mr_50k_15yr_usdm"},"tc1yr":"tc_tanker_mr_48k_1yr_usdday","tc3yr":"tc_tanker_mr_48k_3yr_usdday","tcHist":"tc_tanker_mr_hist_1yr_usdday","opex":"opex_tanker_mr_usdday","fuel_noneco":22,"fuel_eco":16,"scrubber_eligible":True},
        "Handy Tanker (38k DWT)": {"nb":None,"resale":"tanker_handy_38k_resale_usdm","scrap":None,"dwt":38000,"ages":{"5":"tanker_handy_38k_5yr_usdm","10":"tanker_handy_38k_10yr_usdm","15":"tanker_handy_37k_15yr_usdm"},"tc1yr":"tc_tanker_handy_37k_1yr_usdday","tc3yr":"tc_tanker_handy_37k_3yr_usdday","tcHist":"tc_tanker_mr_hist_1yr_usdday","opex":"opex_tanker_handy_usdday","fuel_noneco":18,"fuel_eco":13,"scrubber_eligible":True},
    },
    "Container": {
        "Panamax (9k TEU)": {"nb":"container_panamax_9k_nb_usdm","resale":"container_panamax_9k2_resale_usdm","scrap":None,"teu":9000,"ages":{"5":"container_panamax_9k2_5yr_usdm","10":"container_panamax_9k2_10yr_usdm","15":"container_panamax_8k8_15yr_usdm"},"tc1yr":None,"tc3yr":None,"tcHist":None,"opex":"opex_container_6k_usdday","fuel_noneco":45,"fuel_eco":32,"scrubber_eligible":True},
        "Sub-Panamax (7k TEU)": {"nb":None,"resale":"container_subpanamax_7k_resale_usdm","scrap":None,"teu":7000,"ages":{"5":"container_subpanamax_7k_5yr_usdm","10":"container_subpanamax_7k_10yr_usdm","15":"container_subpanamax_7k_15yr_usdm"},"tc1yr":None,"tc3yr":None,"tcHist":None,"opex":"opex_container_6k_usdday","fuel_noneco":38,"fuel_eco":27,"scrubber_eligible":True},
        "Feeder (3.8k TEU)": {"nb":None,"resale":"container_feeder_3k8_resale_usdm","scrap":None,"teu":3800,"ages":{"5":"container_feeder_3k8_5yr_usdm","10":"container_feeder_3k8_10yr_usdm","15":"container_feeder_4k5_15yr_usdm"},"tc1yr":None,"tc3yr":None,"tcHist":None,"opex":"opex_container_2k_usdday","fuel_noneco":22,"fuel_eco":16,"scrubber_eligible":True},
    },
    "Gas": {
        "LNG 174k CBM": {"nb":"gas_lng_174k_nb_usdm","resale":None,"scrap":None,"cbm":174000,"ages":{"5":"gas_lng_174k_5yr_usdm"},"tc1yr":None,"tc3yr":None,"tcHist":None,"opex":"opex_gas_vlgc_usdday","fuel_noneco":60,"fuel_eco":45,"scrubber_eligible":False},
        "LNG 160k CBM": {"nb":"gas_lng_160k_nb_usdm","resale":None,"scrap":None,"cbm":160000,"ages":{"5":"gas_lng_160k_5yr_usdm","10":"gas_lng_160k_10yr_usdm"},"tc1yr":None,"tc3yr":None,"tcHist":None,"opex":"opex_gas_vlgc_usdday","fuel_noneco":55,"fuel_eco":42,"scrubber_eligible":False},
    },
}

VLSFO_PRICE = 550
HSFO_PRICE = 380
HILO_SPREAD = VLSFO_PRICE - HSFO_PRICE
ECO_TC_PREMIUM = {"Bulker": 2500, "Tanker": 3000, "Container": 3500, "Gas": 2000}
SCRUBBER_TC_PREMIUM = {"Bulker": 1500, "Tanker": 2000, "Container": 2000, "Gas": 0}
SS_COST = {"Bulker": 1.5, "Tanker": 2.0, "Container": 2.5, "Gas": 3.0}

# ── Engine (same as Jupyter v5) ──
def glv(df, col):
    if col is None or col not in df.columns: return None
    v = df[col].dropna()
    return float(v.iloc[-1]) if len(v) > 0 else None

def get_df(vt):
    return {"Bulker":bulker,"Tanker":tanker,"Container":container,"Gas":gas}[vt]

def market_price(vt, vc, age):
    spec = VESSEL_TAXONOMY[vt][vc]; df = get_df(vt)
    if age <= 1:
        v = glv(df, spec.get("nb"))
        if v: return v
    if age <= 2:
        v = glv(df, spec.get("resale"))
        if v: return v
    pts = sorted([(int(k), glv(df,v)) for k,v in spec["ages"].items()], key=lambda x:x[0])
    pts = [(a,v) for a,v in pts if v is not None]
    nb = glv(df, spec.get("nb")); resale = glv(df, spec.get("resale"))
    if nb: pts.insert(0, (0, nb))
    elif resale: pts.insert(0, (1, resale))
    scrap = glv(df, spec.get("scrap"))
    if scrap: pts.append((25, scrap))
    if len(pts) < 2: return (nb or resale or 30) * max(0.15, 1 - age * 0.04)
    al = [p[0] for p in pts]; vl = [p[1] for p in pts]
    if age <= al[0]: return vl[0]
    if age >= al[-1]: return vl[-1]
    for i in range(len(al)-1):
        if al[i] <= age <= al[i+1]:
            f = (age - al[i]) / (al[i+1] - al[i])
            return vl[i] + f * (vl[i+1] - vl[i])
    return 30

def calibrate_ou(vt, vc):
    spec = VESSEL_TAXONOMY[vt][vc]
    hc = spec.get("tcHist")
    if hc is None or hc not in charter.columns: hc = spec.get("tc1yr")
    if hc is None or hc not in charter.columns: return None
    s = charter[hc].dropna().values
    if len(s) < 15: return None
    lr = np.log(s); dt = 0.25; x, y = lr[:-1], lr[1:]
    if np.var(x) == 0: return None
    b = np.cov(x, y, ddof=0)[0,1] / np.var(x)
    a = np.mean(y) - b * np.mean(x)
    se = np.std(y - a - b * x)
    if b <= 0 or b >= 1: b = np.clip(b, 0.01, 0.99)
    k = -np.log(b) / dt; mu = a / (1 - b)
    sig = se * np.sqrt(2*k / (1 - np.exp(-2*k*dt)))
    hl = np.log(2) / k * 0.25
    pk = np.maximum.accumulate(s); dd = (s - pk) / pk
    return {"kappa":k,"mu":mu,"sigma":sig,"hl":hl,
            "rate_bull":np.exp(mu+sig**2/(4*k)),
            "rate_base":np.exp(np.mean(lr[lr<np.percentile(lr,90)])),
            "rate_bear":np.exp(np.median(lr)),
            "n":len(s),"cur":float(s[-1]),
            "sMin":float(np.min(s)),"sMax":float(np.max(s)),
            "sMean":float(np.mean(s)),"sStd":float(np.std(s)),
            "median":float(np.median(s)),
            "mdd":float(np.min(dd)),
            "cp":float((s[-1]-np.mean(s))/np.std(s))}

def intrinsic_value_v5(vt, vc, age, cost_debt, cost_equity, leverage,
                       util, is_eco, has_scrubber, useful_life, ss_status,
                       charter_rate=0, charter_years=0, rate_scenario="base"):
    spec = VESSEL_TAXONOMY[vt][vc]; df = get_df(vt)
    wacc = (cost_debt/100)*(leverage/100) + (cost_equity/100)*(1-leverage/100)
    remaining_life = max(useful_life - age, 1)
    scrap = glv(df, spec.get("scrap")) or 2.0
    base_opex = glv(opex_df, spec.get("opex")) or 6500
    tdc = base_opex + 500 + 300
    eco_tc_adj = ECO_TC_PREMIUM.get(vt, 2500) if is_eco else -ECO_TC_PREMIUM.get(vt, 2500) * 0.5
    scrubber_adj = 0
    if has_scrubber and spec.get("scrubber_eligible", True):
        fuel_cons = spec.get("fuel_eco" if is_eco else "fuel_noneco", 30)
        scrubber_adj = fuel_cons * HILO_SPREAD * 0.85 + SCRUBBER_TC_PREMIUM.get(vt, 1500)
    ss_cost = 0
    if ss_status == "Due this year": ss_cost = SS_COST.get(vt, 2.0)
    elif ss_status == "Due in 1-2 years": ss_cost = SS_COST.get(vt, 2.0) / (1 + wacc)
    ou = calibrate_ou(vt, vc)
    if ou:
        base_stc = ou["rate_%s" % rate_scenario]
        ctc = glv(charter, spec.get("tc1yr")) or glv(charter, spec.get("tc3yr")) or base_stc
        hl = ou["hl"]
    else:
        tc3 = glv(charter, spec.get("tc3yr")); tc1 = glv(charter, spec.get("tc1yr"))
        base_stc = tc3 or tc1 or tdc * 1.3; ctc = tc1 or tc3 or base_stc; hl = 1.0
    stc = base_stc + eco_tc_adj + scrubber_adj
    adj_ctc = ctc + eco_tc_adj + scrubber_adj
    rs = np.log(2) / max(hl, 0.25)
    pve = 0; yd = []
    for yr in range(remaining_life):
        br = stc + (adj_ctc - stc) * np.exp(-rs * yr)
        dn = br * (util/100) - tdc; an = dn * 365
        pv = an / (1+wacc)**(yr+1); pve += pv
        yd.append({"year":yr+1,"rate":br,"earn":an/1e6,"pv":pv/1e6})
    pvs = scrap * 1e6 / (1+wacc)**remaining_life
    hull_iv = max((pve + pvs)/1e6, 0)
    charter_pv = 0
    if charter_rate > 0 and charter_years > 0:
        dp = charter_rate - stc; ap = dp * 365
        for yr in range(int(charter_years)):
            charter_pv += ap / (1+wacc)**(yr+1)
        frac = charter_years - int(charter_years)
        if frac > 0: charter_pv += (ap*frac)/(1+wacc)**(int(charter_years)+1)
    charter_adj_m = charter_pv / 1e6
    iv = hull_iv + charter_adj_m - ss_cost
    mkt = market_price(vt, vc, age)
    dnlr = stc * (util/100) - tdc
    af = sum(1/(1+wacc)**(yr+1) for yr in range(remaining_life))
    tpv = mkt*1e6 - pvs
    itc = max(((tpv/af/365)+tdc)/(util/100), 0) if af > 0 else 0
    pd_pct = (mkt - iv)/iv if iv > 0 else 0
    ey = (dnlr*365)/(iv*1e6) if iv > 0 else 0
    if pd_pct < -0.10: sig, sc = "UNDERVALUED", "green"
    elif pd_pct > 0.10: sig, sc = "OVERVALUED", "red"
    else: sig, sc = "FAIR VALUE", "orange"
    # Scenarios
    scenario_ivs = {}
    if ou:
        for scn in ["bull","base","bear"]:
            scn_stc = ou["rate_%s"%scn] + eco_tc_adj + scrubber_adj
            scn_pv = sum(((scn_stc+(adj_ctc-scn_stc)*np.exp(-rs*yr))*(util/100)-tdc)*365/(1+wacc)**(yr+1) for yr in range(remaining_life))
            scenario_ivs[scn] = max((scn_pv+pvs)/1e6+charter_adj_m-ss_cost, 0)
            scenario_ivs[scn+"_tc"] = scn_stc
    # Sensitivity
    sens = []
    for ra in [-0.20, -0.10, 0, 0.10, 0.20]:
        row = {"Rate": "%+.0f%%" % (ra*100)}
        for w in [wacc-0.02, wacc, wacc+0.02]:
            ar = stc*(1+ra); dn2 = ar*(util/100)-tdc; an2 = dn2*365
            af2 = sum(1/(1+w)**(yr+1) for yr in range(remaining_life))
            ps2 = scrap*1e6/(1+w)**remaining_life
            row["WACC %.1f%%" % (w*100)] = max((an2*af2+ps2)/1e6+charter_adj_m-ss_cost, 0)
        sens.append(row)
    return {"iv":iv,"hull_iv":hull_iv,"mkt":mkt,"pd":pd_pct,"sig":sig,"sc":sc,
            "wacc":wacc,"wacc_pct":wacc*100,"stc":stc,"base_stc":base_stc,"ctc":adj_ctc,
            "itc":itc,"dnlr":dnlr,"ey":ey,"rl":remaining_life,"scrap":scrap,"opex":base_opex,"tdc":tdc,
            "pve":pve/1e6,"pvs":pvs/1e6,"charter_adj":charter_adj_m,"ss_cost":ss_cost,
            "eco_tc_adj":eco_tc_adj,"scrubber_adj":scrubber_adj,
            "yd":yd,"sens":sens,"ou":ou,"hl":hl,"scenarios":scenario_ivs}

# ════════════════════════════════════════════════════════
# STREAMLIT UI
# ════════════════════════════════════════════════════════

st.markdown("# Harrys Valuation")
st.markdown("*Intrinsic Value Engine | Backtested to 17% MAE*")

page = st.sidebar.radio("Module", ["Valuation", "Fleet Scanner"])

# Sidebar inputs
st.sidebar.markdown("---")
st.sidebar.markdown("### Vessel")
sector = st.sidebar.selectbox("Sector", list(VESSEL_TAXONOMY.keys()))
vc = st.sidebar.selectbox("Class", list(VESSEL_TAXONOMY[sector].keys()))
by = st.sidebar.number_input("Build Year", 1995, 2026, 2018)
eco = st.sidebar.selectbox("Eco Design", ["No", "Yes"]) == "Yes"
scrubber = st.sidebar.selectbox("Scrubber", ["No", "Yes"]) == "Yes"
useful_life = st.sidebar.slider("Useful Life (yr)", 20, 30, 25)
ss = st.sidebar.selectbox("Special Survey", ["Just completed", "Due in 1-2 years", "Due this year"])
scenario = st.sidebar.selectbox("Rate Scenario", ["base", "bull", "bear"])

st.sidebar.markdown("### Cost of Capital")
cod = st.sidebar.slider("Cost of Debt (%)", 2.0, 12.0, 6.5, 0.25)
coe = st.sidebar.slider("Cost of Equity (%)", 8.0, 25.0, 15.0, 0.5)
lev = st.sidebar.slider("Leverage (%)", 0, 80, 60)
util = st.sidebar.slider("Utilization (%)", 70, 100, 95)

st.sidebar.markdown("### Charter (optional)")
cr = st.sidebar.number_input("Charter Rate ($/day)", 0, 200000, 0, 500)
cy = st.sidebar.number_input("Remaining Years", 0.0, 15.0, 0.0, 0.5)

age = 2026 - by

if page == "Valuation":
    v = intrinsic_value_v5(sector, vc, age, cod, coe, lev, util, eco, scrubber,
                            useful_life, ss, cr, cy, scenario)
    spec = VESSEL_TAXONOMY[sector][vc]
    sz = ""
    if "dwt" in spec: sz = "%dk DWT" % (spec["dwt"]//1000)
    elif "teu" in spec: sz = "%dk TEU" % (spec["teu"]//1000)
    elif "cbm" in spec: sz = "%dk CBM" % (spec["cbm"]//1000)

    # Hero
    c1, c2 = st.columns([3, 1])
    with c1:
        tags = []
        if eco: tags.append("ECO")
        if scrubber: tags.append("SCRUBBER")
        if cr > 0: tags.append("CHARTERED")
        tag_str = " | ".join(tags) if tags else "Standard"
        st.markdown("### INTRINSIC VALUE")
        st.markdown("# ${:.1f}M".format(v["iv"]))
        st.markdown("{} | {} | Built {} | Age {} | {}".format(vc, sz, by, age, tag_str))
    with c2:
        if v["sig"] == "UNDERVALUED":
            st.success(v["sig"])
        elif v["sig"] == "OVERVALUED":
            st.error(v["sig"])
        else:
            st.warning(v["sig"])
        st.metric("WACC", "{:.2f}%".format(v["wacc_pct"]))

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Market Price", "${:.1f}M".format(v["mkt"]))
    k2.metric("Premium/Discount", "{:+.1f}%".format(v["pd"]*100))
    k3.metric("Earnings Yield", "{:.1f}%".format(v["ey"]*100))
    k4.metric("Implied TC (Mkt)", "${:,}/d".format(int(v["itc"])))

    # Scenarios
    if v["scenarios"]:
        st.markdown("### Three Scenarios (Backtested)")
        s1, s2, s3 = st.columns(3)
        for col, sn, label, desc in [(s1,"bear","BEAR","Median rate"),
                                      (s2,"base","BASE","Trimmed mean (17% MAE)"),
                                      (s3,"bull","BULL","OU mean (includes supercycle)")]:
            with col:
                siv = v["scenarios"].get(sn, 0)
                stc_v = v["scenarios"].get(sn+"_tc", 0)
                is_sel = scenario == sn
                if is_sel: st.info("**{}: ${:.1f}M** | TC: ${:,}/d".format(label, siv, int(stc_v)))
                else: st.markdown("{}: ${:.1f}M | TC: ${:,}/d".format(label, siv, int(stc_v)))

    # Earnings model
    st.markdown("### Earnings Model")
    e1, e2, e3, e4, e5, e6 = st.columns(6)
    e1.metric("Base Sust. TC", "${:,}/d".format(int(v["base_stc"])))
    e2.metric("Eco Adj", "${:,}/d".format(int(v["eco_tc_adj"])))
    e3.metric("Scrubber Adj", "${:,}/d".format(int(v["scrubber_adj"])))
    e4.metric("Sust. TC", "${:,}/d".format(int(v["stc"])))
    e5.metric("Daily Costs", "${:,}/d".format(int(v["tdc"])))
    e6.metric("Daily Net", "${:,}/d".format(int(v["dnlr"])))

    # Value bridge
    st.markdown("### Value Bridge")
    bridge_data = [{"Component": "Hull IV (PV earnings + scrap)", "Value": v["hull_iv"]}]
    if v["charter_adj"] != 0:
        bridge_data.append({"Component": "Charter Adjustment", "Value": v["charter_adj"]})
    if v["ss_cost"] > 0:
        bridge_data.append({"Component": "Special Survey Cost", "Value": -v["ss_cost"]})
    bridge_data.append({"Component": "TOTAL INTRINSIC VALUE", "Value": v["iv"]})
    bdf = pd.DataFrame(bridge_data)
    bdf["Value"] = bdf["Value"].apply(lambda x: "${:.1f}M".format(x))
    st.dataframe(bdf, hide_index=True, use_container_width=True)

    # Sensitivity
    st.markdown("### Sensitivity Table ($M)")
    st.dataframe(pd.DataFrame(v["sens"]).set_index("Rate").applymap(lambda x: "${:.1f}M".format(x) if isinstance(x, float) else x),
                 use_container_width=True)

    # Chart
    st.markdown("### Projected Earnings")
    yd = v["yd"][:20]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=[d["year"] for d in yd], y=[d["pv"] for d in yd],
        name="PV of FCF ($M)", marker_color="rgba(201,168,76,0.5)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=[d["year"] for d in yd], y=[d["rate"] for d in yd],
        name="Blended TC ($/d)", line=dict(color="#2563eb", width=2), mode="lines"), secondary_y=True)
    fig.add_trace(go.Scatter(x=[d["year"] for d in yd], y=[v["stc"]]*len(yd), name="Sustainable TC",
        line=dict(color="#22c55e", width=1, dash="dot"), mode="lines"), secondary_y=True)
    fig.update_layout(height=350, template="plotly_white", margin=dict(t=20,b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02))
    fig.update_yaxes(title_text="$M", secondary_y=False)
    fig.update_yaxes(title_text="$/day", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    # OU info
    if v["ou"]:
        st.markdown("### Rate Cycle (OU Model)")
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Long-Run Mean", "${:,}/d".format(int(v["ou"]["rate_base"])))
        o2.metric("Current Rate", "${:,}/d".format(int(v["ou"]["cur"])))
        o3.metric("Cycle Position", "{:+.1f} std".format(v["ou"]["cp"]))
        o4.metric("Half-Life", "{:.1f} yr".format(v["ou"]["hl"]))

elif page == "Fleet Scanner":
    st.markdown("### Fleet Scanner")
    st.markdown("*Intrinsic value vs market across all classes (BASE scenario, non-eco, no scrubber)*")

    rows = []
    for sn in VESSEL_TAXONOMY:
        for cn in VESSEL_TAXONOMY[sn]:
            for a in [5, 10, 15]:
                try:
                    v = intrinsic_value_v5(sn, cn, a, cod, coe, lev, util,
                                            False, False, 25, "Just completed", 0, 0, "base")
                    ou = v["ou"]
                    dq = "High" if ou and ou["n"] > 50 else "Med" if ou else "Low"
                    rows.append({"Sector":sn,"Class":cn,"Age":a,
                                "IV":"${:.1f}M".format(v["iv"]),"Market":"${:.1f}M".format(v["mkt"]),
                                "P/D":"{:+.0f}%".format(v["pd"]*100),"Signal":v["sig"],
                                "Sust TC":"${:,}/d".format(int(v["stc"])),"Data":dq})
                except:
                    pass

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, hide_index=True, use_container_width=True, height=600)

st.markdown("---")
st.markdown("*Harrys Valuation | Q1 2026 Market Data | Backtested BASE scenario: 17% MAE, OVERVALUED signal correct 79-84% of time*")
