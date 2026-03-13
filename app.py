import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import json
import anthropic
import warnings
warnings.filterwarnings('ignore')
import plotly.io as pio
pio.templates.default = "plotly_dark"  # Force dark bg on ALL charts

st.set_page_config(
    page_title="Unseen Creatures — Dashboard",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL STYLES ──────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] {
    background-color: #0f1117 !important;
    height: 0px !important;
    min-height: 0px !important;
    padding: 0px !important;
}
[data-testid="stAppViewContainer"] { background-color: #0f1117; color: #e8eaf0; }
[data-testid="stSidebar"] { background-color: #1a1f2e; border-right: 1px solid #2d3348; }
[data-testid="stSidebar"] * { color: #c8ccd8 !important; }
.main .block-container { padding-top: 0.8rem; padding-bottom: 2rem; max-width: 1400px; }
h1 { color: #ffffff !important; font-weight: 700 !important; letter-spacing: -0.5px !important; }
h2 { color: #e2e8f0 !important; font-weight: 600 !important;
     border-bottom: 1px solid #2d3348; padding-bottom: 0.4rem; margin-top: 1.5rem !important; }
h3 { color: #a8b4c8 !important; font-weight: 500 !important; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e2436 0%, #252b3d 100%);
    border: 1px solid #2d3a52; border-radius: 12px;
    padding: 1rem 1.2rem !important; box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label {
    color: #7888a0 !important; font-size: 0.75rem !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important; font-size: 1.6rem !important; font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; font-weight: 600 !important; }
[data-testid="stTabs"] [role="tablist"] {
    background-color: #1a1f2e; border-radius: 10px;
    padding: 4px; gap: 2px; border-bottom: none !important;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent; color: #7888a0 !important;
    border-radius: 8px; padding: 0.4rem 0.9rem;
    font-size: 0.82rem; font-weight: 500; border: none !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #2d3a52 !important; color: #ffffff !important; font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: #c8d0e0 !important; background: #232940 !important; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #2d3348; }
[data-testid="stDataFrame"] th {
    background-color: #1e2840 !important; color: #a8b8d0 !important;
    font-size: 0.78rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.05em;
}
[data-testid="stDataFrame"] td { color: #d0d8e8 !important; font-size: 0.85rem !important; }
/* Streamlit v1.3+ dataframe overrides */
.dvn-scroller { background-color: #1a1f2e !important; }
.cell-wrapper { background-color: #1a1f2e !important; color: #d0d8e8 !important; }
[data-testid="glideDataEditor"] { background-color: #1a1f2e !important; }
[class*="dvn-"] { background-color: #1a1f2e !important; color: #d0d8e8 !important; }
[class*="cell"] { color: #d0d8e8 !important; }
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important; font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
}
[data-testid="stSelectbox"] > div > div {
    background-color: #1e2436 !important; border: 1px solid #2d3a52 !important;
    border-radius: 8px !important; color: #e0e6f0 !important;
}
[data-testid="stNumberInput"] input {
    background-color: #1e2436 !important; border: 1px solid #2d3a52 !important;
    border-radius: 8px !important; color: #e0e6f0 !important;
}
[data-testid="stAlert"] { border-radius: 10px !important; border-left-width: 4px !important; }
[data-testid="stExpander"] {
    background-color: #1a1f2e !important; border: 1px solid #2d3348 !important;
    border-radius: 10px !important;
}
hr { border-color: #2d3348 !important; margin: 1.2rem 0 !important; }
[data-testid="stCaptionContainer"] { color: #5a6478 !important; font-size: 0.76rem !important; }
[data-testid="stFileUploader"] {
    background-color: #1a1f2e !important; border: 2px dashed #2d3a52 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background-color: #252b3d !important; border-color: #3d4a62 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background-color: #252b3d !important; border-color: #3d4a62 !important;
}
div[data-testid="stDataEditor"] { background-color: #1a1f2e !important; }
/* Plotly chart containers */
.js-plotly-plot, .plot-container, .plotly { background-color: #161b2a !important; }
iframe { background-color: #161b2a !important; }
[data-testid="stArrowVegaLiteChart"] { background-color: #161b2a !important; }
/* Force ALL text elements to be light */
p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #e0e6f0 !important; }
.stMarkdown p { color: #e0e6f0 !important; }
.stMarkdown h5 { color: #ffffff !important; }
/* Selectbox labels */
[data-testid="stWidgetLabel"] { color: #a8b4c8 !important; }
[data-testid="stWidgetLabel"] p { color: #a8b4c8 !important; }
/* Progress bar text */
[data-testid="stProgress"] > div { color: #c8d0e0 !important; }
[data-testid="stProgressBarMessage"] { color: #c8d0e0 !important; }
/* Metric labels already handled but reinforce */
[data-testid="metric-container"] * { color: inherit !important; }
[data-testid="metric-container"] label { color: #7888a0 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; }
/* Caption text */
small, .caption { color: #6b7a94 !important; }
/* Tab content text */
[data-testid="stTab"] p { color: #e0e6f0 !important; }
/* Info/warning/error boxes */
[data-testid="stAlert"] p { color: #e0e6f0 !important; }
/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #c8ccd8 !important; }
/* Header/subheader */
[data-testid="stHeading"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY DARK THEME ──────────────────────────────────────────────────────
BG  = "#161b2a"
BG2 = "#0f1117"
GRID = "#1e2840"
LINE = "#2d3a52"
TXT  = "#c8d0e0"
HOV  = "#1e2840"

PT = dict(
    plot_bgcolor  = BG,
    paper_bgcolor = BG,
    font          = dict(color=TXT, family="Inter, system-ui, sans-serif", size=12),
    xaxis         = dict(gridcolor=GRID, linecolor=LINE, tickcolor=LINE,
                         tickfont=dict(color=TXT), showgrid=True, zeroline=False),
    yaxis         = dict(gridcolor=GRID, linecolor=LINE, tickcolor=LINE,
                         tickfont=dict(color=TXT), showgrid=True, zeroline=False),
    legend        = dict(bgcolor=BG, bordercolor=LINE, borderwidth=1,
                         font=dict(color=TXT, size=11)),
    hoverlabel    = dict(bgcolor=HOV, bordercolor=LINE,
                         font=dict(color="#e0e6f0", size=12)),
    margin        = dict(t=30, b=40, l=10, r=10),
)

def dc(fig, **kwargs):
    """Apply dark theme + any extra layout args. Returns fig."""
    # Separate out nested-dict keys that may conflict if passed twice
    nested_keys = ('legend', 'xaxis', 'yaxis', 'margin', 'hoverlabel', 'font')
    base = {k: v for k, v in PT.items() if k not in nested_keys}
    merged = {**base, **kwargs}

    # Merge nested dicts: PT base + caller overrides
    for key in nested_keys:
        pt_val = PT.get(key, {})
        kw_val = kwargs.get(key, {})
        if pt_val or kw_val:
            merged[key] = {**pt_val, **kw_val}

    # Force backgrounds regardless of plotly template
    merged['plot_bgcolor']  = BG
    merged['paper_bgcolor'] = BG
    # Force all text labels to be light coloured
    merged['uniformtext']   = dict(minsize=10, mode='hide')

    fig.update_layout(**merged)
    # Force annotation & title text colours
    fig.update_annotations(font_color=TXT)

    # Force axis colours (some chart types override these)
    AXIS = dict(gridcolor=GRID, linecolor=LINE, tickcolor=LINE,
                tickfont_color=TXT, showgrid=True, zeroline=False,
                zerolinecolor=GRID)
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    # Force all trace text labels light
    fig.update_traces(textfont_color=TXT, selector=dict(type="bar"))
    fig.update_traces(textfont_color=TXT, selector=dict(type="scatter"))
    return fig

CLR = dict(
    blue="#3b82f6", blue_l="#93c5fd",
    green="#10b981", green_l="#6ee7b7",
    red="#ef4444",  red_l="#fca5a5",
    orange="#f59e0b", purple="#8b5cf6",
    teal="#14b8a6",   gray="#6b7280", white="#f1f5f9",
)
CAT_COLORS = [CLR["blue"],CLR["teal"],CLR["green"],CLR["orange"],
              CLR["purple"],CLR["red"],"#06b6d4","#84cc16",
              "#ec4899","#a78bfa","#fb923c","#34d399"]

# ── AUTH ─────────────────────────────────────────────────────────────────
_CREDENTIALS = {
    "usernames": {
        "UnseenCreatures": {
            "name": "Unseen Creatures",
            "password": "$2b$12$2h9AMWimJI/7JsVOiOCkB.J77HYMpRScD4en0FPhP7LLdIL6svECS"
        }
    }
}
_authenticator = stauth.Authenticate(
    _CREDENTIALS,
    "unseen_dashboard",   # cookie name
    "unseen_key_2025",    # cookie key
    cookie_expiry_days=7
)
_name, _auth_status, _username = _authenticator.login(
    location="main",
    fields={"Form name": "🍺 Unseen Creatures — Acceso",
            "Username": "Usuario",
            "Password": "Contraseña",
            "Login": "Entrar"}
)
if _auth_status is False:
    st.error("Usuario o contraseña incorrectos")
    st.stop()
elif _auth_status is None:
    st.stop()
# If we reach here, user is authenticated — show the full dashboard

# ── PATHS (local) ────────────────────────────────────────────────────────
BASE       = r"C:\brewery_analysis"
SALES_2025 = os.path.join(BASE, "SalesSummary_2025-01-01_2025-12-31")
SALES_2026 = os.path.join(BASE, "SalesSummary_2026-01-01_2026-02-16")
MODELO     = os.path.join(BASE, "modelo_unseen_v4.xlsx")
PAYOUT_25  = os.path.join(BASE, "Payout overview_2025.csv")
PAYOUT_26  = os.path.join(BASE, "Payout overview_2026_Feb16.csv")
CF_25      = os.path.join(BASE, "Unseen - Cash Flow 2025.xlsx")
CF_26      = os.path.join(BASE, "Unseen - Cash Flow 2026.xlsx")

# ── GOOGLE DRIVE (fallback when local files not found) ────────────────────
try:
    from drive_loader import load_csvs as _drive_load_csvs
    from drive_loader import load_excel as _drive_load_excel
    _DRIVE_AVAILABLE = True
except ImportError:
    _DRIVE_AVAILABLE = False

def _local_exists():
    """True if the main model file is present locally."""
    return os.path.exists(MODELO)

USE_DRIVE = _DRIVE_AVAILABLE and not _local_exists()

# Drive folder names (must match exactly what you created in Google Drive)
DRIVE_FOLDER_MODELO   = "modelos"
DRIVE_FOLDER_PAYOUT   = "payout"
DRIVE_FOLDER_SALES_25 = "sales_2025"
DRIVE_FOLDER_SALES_26 = "sales_2026"
DRIVE_FOLDER_CF       = "modelos"   # Cash Flow files live in same folder as modelo

MONTHS_ES  = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
              7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
MONTHS_REV = {v:k for k,v in MONTHS_ES.items()}
ALL_MONTHS = ["Ene 25","Feb 25","Mar 25","Abr 25","May 25","Jun 25",
              "Jul 25","Ago 25","Sep 25","Oct 25","Nov 25","Dic 25",
              "Ene 26","Feb 26","Mar 26","Abr 26","May 26","Jun 26",
              "Jul 26","Ago 26","Sep 26","Oct 26","Nov 26","Dic 26"]

# ── LOADERS ────────────────────────────────────────────────────────────────
@st.cache_data
def load_pl():
    def _parse_xl(xl):
        raw  = xl.parse("P&L Taproom", header=None)
        hdrs = raw.iloc[2].tolist()
        data = raw.iloc[3:].copy()
        data.columns = hdrs
        data = data.rename(columns={hdrs[1]: "line_item"})
        data = data.drop(columns=[hdrs[0]], errors="ignore")
        data["line_item"] = data["line_item"].astype(str).str.strip()
        data = data[data["line_item"].notna()
                    & (data["line_item"] != "")
                    & (data["line_item"] != "nan")
                    & (data["line_item"] != "NaN")]
        month_cols = [c for c in data.columns
                      if c != "line_item"
                      and str(c).strip() not in ("","nan","NaN")
                      and pd.notna(c)]
        for c in month_cols:
            data[c] = pd.to_numeric(
                data[c].astype(str).str.replace(r'[$,]','',regex=True),
                errors="coerce")
        return data[["line_item"]+month_cols].reset_index(drop=True), month_cols

    if not USE_DRIVE and os.path.exists(MODELO):
        return _parse_xl(pd.ExcelFile(MODELO, engine="openpyxl"))
    elif USE_DRIVE:
        xl = _drive_load_excel(DRIVE_FOLDER_MODELO, "modelo_unseen_v4.xlsx")
        if xl: return _parse_xl(xl)
    return pd.DataFrame(columns=["line_item"]), []

@st.cache_data
def load_sales_by_day():
    def _parse_df(df):
        df.columns = df.columns.str.strip()
        date_col = df.columns[0]
        df = df.rename(columns={date_col:"date"})
        df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d", errors="coerce")
        df = df.dropna(subset=["date"])
        net = [c for c in df.columns if "net sales" in c.lower()]
        if net:
            df["Net sales"] = pd.to_numeric(
                df[net[0]].astype(str).str.replace(r'[$,]','',regex=True), errors="coerce")
        ord_ = [c for c in df.columns if "order" in c.lower()]
        if ord_: df["Total orders"] = pd.to_numeric(df[ord_[0]], errors="coerce")
        gst = [c for c in df.columns if "guest" in c.lower()]
        if gst: df["Total guests"] = pd.to_numeric(df[gst[0]], errors="coerce")
        return df

    frames = []
    if not USE_DRIVE:
        for path, fname in [(SALES_2025,"Sales by day_2025.csv"),
                            (SALES_2026,"Sales by day.csv")]:
            f = os.path.join(path, fname)
            if os.path.exists(f):
                frames.append(_parse_df(pd.read_csv(f)))
    else:
        for folder in [DRIVE_FOLDER_SALES_25, DRIVE_FOLDER_SALES_26]:
            for df in _drive_load_csvs(folder):
                try: frames.append(_parse_df(df))
                except Exception: pass

    if not frames: return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True).sort_values("date")
    out["year"]  = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["dow"]   = out["date"].dt.day_name()
    return out

@st.cache_data
def load_sales_category():
    def _parse_cat(df, year):
        df.columns = df.columns.str.strip()
        df["year"] = year
        for c in ["Net sales","Gross sales","Discount amount","Refund amount","Tax amount"]:
            if c in df.columns:
                df[c] = pd.to_numeric(
                    df[c].astype(str).str.replace(r'[$,]','',regex=True), errors="coerce")
        return df

    frames = []
    if not USE_DRIVE:
        for path, year in [(SALES_2025,2025),(SALES_2026,2026)]:
            f = os.path.join(path, "Sales category summary.csv")
            if os.path.exists(f):
                frames.append(_parse_cat(pd.read_csv(f), year))
    else:
        for folder, year in [(DRIVE_FOLDER_SALES_25,2025),(DRIVE_FOLDER_SALES_26,2026)]:
            for df in _drive_load_csvs(folder):
                try: frames.append(_parse_cat(df, year))
                except Exception: pass

    if not frames: return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

@st.cache_data
def load_payout():
    def _parse_pay(df):
        df.columns = df.columns.str.strip()
        df["Sales date"] = pd.to_datetime(df["Sales date"], errors="coerce")
        for c in ["Payments","Refunds","Fees","Withholdings","Payouts"]:
            if c in df.columns:
                df[c] = pd.to_numeric(
                    df[c].astype(str).str.replace(r'[$,]','',regex=True), errors="coerce")
        return df

    frames = []
    if not USE_DRIVE:
        for f in [PAYOUT_25, PAYOUT_26]:
            if os.path.exists(f):
                frames.append(_parse_pay(pd.read_csv(f)))
    else:
        for df in _drive_load_csvs(DRIVE_FOLDER_PAYOUT):
            try: frames.append(_parse_pay(df))
            except Exception: pass

    if not frames: return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True).dropna(subset=["Sales date"])
    out["year"]  = out["Sales date"].dt.year
    out["month"] = out["Sales date"].dt.month
    return out

@st.cache_data
def load_cashflow():
    """Load and aggregate monthly cash flow data from both xlsx files."""
    MONTH_SHEET_MAP = {
        'Febrero': 'Feb 25', 'Marzo': 'Mar 25', 'Abril': 'Abr 25',
        'Mayo': 'May 25', 'June': 'Jun 25', 'July': 'Jul 25',
        'August': 'Ago 25', 'September': 'Sep 25', 'Octubre': 'Oct 25',
        'November': 'Nov 25', 'December': 'Dic 25',
        'January': 'Ene 26', 'February': 'Feb 26', 'March': 'Mar 26'
    }
    # Summary sheet "2025" has Ene 25 data (row format: label | Ene2024 | Ene2025 | Feb2024 ...)
    MONTHS_ES_LIST = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

    def row_sum(df, label_substr):
        labels = df.iloc[:, 0].astype(str).str.strip().str.lower()
        mask = labels.str.contains(label_substr.lower(), na=False)
        rows = df[mask]
        if rows.empty: return 0.0
        vals = pd.to_numeric(rows.iloc[0].iloc[1:], errors='coerce').dropna()
        return float(vals.sum())

    def parse_month_df(df):
        d = {}
        d['sales_summary']   = row_sum(df, 'sales summary')
        d['total_ingresos']  = row_sum(df, 'ingresos')
        d['aporte_afuera']   = row_sum(df, 'aporte de afuera')
        d['total_egresos']   = row_sum(df, 'egresos')
        d['food_cost']       = row_sum(df, 'food cost')
        d['bebida_taproom']  = row_sum(df, 'bebida taproom')
        d['payroll']         = row_sum(df, 'payrool') + row_sum(df, '^payroll')
        d['tips']            = row_sum(df, '^tips')
        d['taxes']           = row_sum(df, '^taxes')
        d['contractors']     = row_sum(df, 'employees en negro') + row_sum(df, 'contractor')
        d['bands']           = row_sum(df, 'expenses band')
        d['apps']            = row_sum(df, '^apps')
        d['ice_machine']     = row_sum(df, 'ice machine')
        d['facebook']        = row_sum(df, 'facebook')
        d['amazon']          = row_sum(df, '^amazon')
        d['renta']           = row_sum(df, '^renta')
        d['transfer_fee']    = row_sum(df, 'transfer/monthly fee')
        d['inversion']       = row_sum(df, '^inversion')
        d['gastos_prod']     = row_sum(df, 'gastos de produccion')
        d['gas_ft']          = row_sum(df, 'gas food truck')
        d['limpieza']        = row_sum(df, 'limpieza')
        # Saldo final = last numeric in SALDO FINAL row
        labels = df.iloc[:, 0].astype(str).str.strip().str.lower()
        for keyword in ['saldo final']:
            mask = labels.str.contains(keyword, na=False)
            rows_sf = df[mask]
            if not rows_sf.empty:
                vals = pd.to_numeric(rows_sf.iloc[0].iloc[1:], errors='coerce').dropna()
                d['saldo_final'] = float(vals.iloc[-1]) if len(vals) > 0 else None
        for keyword in ['saldo inicial']:
            mask = labels.str.contains(keyword, na=False)
            rows_si = df[mask]
            if not rows_si.empty:
                vals = pd.to_numeric(rows_si.iloc[0].iloc[1:], errors='coerce').dropna()
                d['saldo_inicial'] = float(vals.iloc[0]) if len(vals) > 0 else None
        return d

    all_months = {}

    cf_sources = []
    if not USE_DRIVE:
        for fpath in [CF_25, CF_26]:
            if os.path.exists(fpath):
                try:
                    cf_sources.append(pd.ExcelFile(fpath, engine='openpyxl'))
                except Exception:
                    pass
    else:
        for fname in ["Unseen - Cash Flow 2025.xlsx", "Unseen - Cash Flow 2026.xlsx"]:
            xl = _drive_load_excel(DRIVE_FOLDER_CF, fname)
            if xl: cf_sources.append(xl)

    for xl in cf_sources:
        try:
            _ = xl.sheet_names  # validate
        except Exception:
            continue
        # Monthly sheets
        for sheet in xl.sheet_names:
            if sheet in MONTH_SHEET_MAP:
                try:
                    df = xl.parse(sheet, header=None)
                    if df.empty: continue
                    all_months[MONTH_SHEET_MAP[sheet]] = parse_month_df(df)
                except Exception:
                    continue
        # Summary sheet "2025" — Ene 25 taproom breakdown (2024 vs 2025 cols)
        if '2025' in xl.sheet_names:
            try:
                df_sum = xl.parse('2025', header=None)
                rows_data = {
                    3: 'ingresos_taproom', 4: 'bottle_beer', 5: 'draft_beer',
                    6: 'food_sales', 7: 'happy_hour', 8: 'na_bev',
                    9: 'retail', 10: 'uber', 11: 'wine',
                    12: 'total_guests', 13: 'avg_guest', 14: 'variacion_yoy'
                }
                for i, month in enumerate(MONTHS_ES_LIST):
                    col_25 = 2 + i * 2  # 2025 column for each month
                    key = f"{month} 25"
                    if key not in all_months:
                        all_months[key] = {}
                    for row_idx, field in rows_data.items():
                        if row_idx < len(df_sum) and col_25 < len(df_sum.columns):
                            v = df_sum.iloc[row_idx, col_25]
                            if pd.notna(v):
                                all_months[key][field] = float(v)
            except Exception:
                pass

    return all_months

# ── HELPERS ─────────────────────────────────────

def html_table(df, highlight_rows=None):
    """Render a DataFrame as a styled dark HTML table."""
    highlight_rows = highlight_rows or []
    rows_html = ""
    for idx, row in df.iterrows():
        is_hl = str(idx) in [str(h) for h in highlight_rows]
        bg   = "#1e2840" if is_hl else "transparent"
        fw   = "700"     if is_hl else "400"
        fc   = "#ffffff" if is_hl else "#c8d0e0"
        cells = f'<td style="padding:6px 12px;color:{fc};font-weight:{fw};border-bottom:1px solid #2d3a52;">{idx}</td>'
        for val in row:
            color = "#ef4444" if str(val).startswith("-$") else fc
            cells += f'<td style="padding:6px 12px;color:{color};font-weight:{fw};text-align:right;border-bottom:1px solid #2d3a52;">{val}</td>'
        rows_html += f'<tr style="background:{bg};">{cells}</tr>'
    # Header
    header = '<th style="padding:6px 12px;color:#7888a0;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #2d3a52;text-align:left;">Línea</th>'
    for col in df.columns:
        header += f'<th style="padding:6px 12px;color:#7888a0;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #2d3a52;text-align:right;">{col}</th>'
    html = f"""<div style="overflow-x:auto;border-radius:8px;border:1px solid #2d3a52;margin-bottom:1rem;">
<table style="width:100%;border-collapse:collapse;background:#161b2a;font-size:0.875rem;">
<thead><tr>{header}</tr></thead>
<tbody>{rows_html}</tbody>
</table></div>"""
    return html


def fmt_usd(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return "—"
    return f"${v:,.0f}" if v >= 0 else f"(${abs(v):,.0f})"

def fmt_pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return "—"
    return f"{v:.1f}%"

def get_row(pl, keyword):
    import re as _re
    safe_kw = _re.escape(keyword.lower())
    mask = pl["line_item"].str.lower().str.contains(safe_kw, na=False)
    rows = pl[mask]
    return rows.iloc[0] if not rows.empty else None

def col_for_month(month_cols, mes, year):
    target = f"{MONTHS_ES[mes]} {str(year)[-2:]}"
    for c in month_cols:
        if str(c).strip() == target: return c
    return None

def safe_val(row, col):
    if row is None or col is None: return None
    v = row[col]
    return None if pd.isna(v) else float(v)

def apr_from_factor(factor, months=12):
    total_cost = (factor - 1.0)
    daily_rate = total_cost / (months * 30)
    return daily_rate * 365 * 100

# ── LOAD DATA ──────────────────────────────────────────────────────────────
try:
    pl_base, month_cols = load_pl()
    pl_ok = True
except Exception as e:
    pl_ok    = False
    pl_error = str(e)
    pl_base  = pd.DataFrame()
    month_cols = []

sales_day  = load_sales_by_day()
sales_cat  = load_sales_category()
payout     = load_payout()
cf_data    = load_cashflow()   # monthly cash flow dict

# ── SESSION STATE ──────────────────────────────────────────────────────────
if "overrides" not in st.session_state:
    st.session_state.overrides = {}
if "manual_entries" not in st.session_state:
    st.session_state.manual_entries = []
if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

# Category allocation splits (% to Taproom)
CAT_DEFAULTS = {
    "Gastos fijos (alq+serv+cont)": 50,
    "Payroll W2":                   70,
    "Contractors/Emp Negro":        60,
    "Toast Fees":                  100,
    "Limpieza/Basura":              60,
    "Facebook/Marketing":           80,
    "Amazon (compras varias)":      60,
    "Inversion (mejoras/equipo)":   50,
    "Otros":                        60,
}
CAT_PL_MAP = {
    "Gastos fijos (alq+serv+cont)": "gastos fijos",
    "Payroll W2":                   "payroll w2",
    "Contractors/Emp Negro":        "contractor",
    "Toast Fees":                   "toast fees",
    "Limpieza/Basura":              "limpieza",
    "Facebook/Marketing":           "facebook",
    "Amazon (compras varias)":      "amazon",
    "Inversion (mejoras/equipo)":   "inversion",
    "Otros":                        "otros",
}
if "cat_splits" not in st.session_state:
    st.session_state.cat_splits = dict(CAT_DEFAULTS)

# Beer cost per month — dict keyed by column label e.g. "Ene 25"
if "beer_costs" not in st.session_state:
    st.session_state.beer_costs = {m: 0.0 for m in ALL_MONTHS}

# ── GET P&L with all adjustments applied ───────────────────────────────────
def get_pl():
    if pl_base.empty:
        return pl_base, month_cols
    pl = pl_base.copy()

    # Apply cell overrides
    for (li, col), val in st.session_state.overrides.items():
        mask = pl["line_item"] == li
        if mask.any() and col in pl.columns:
            pl.loc[mask, col] = val

    # Apply manual entries
    for entry in st.session_state.manual_entries:
        col = entry["col"]
        cat = entry["categoria"]
        amt = entry["monto"]
        if col not in pl.columns: continue
        mask = pl["line_item"].str.lower().str.contains(cat.lower(), na=False)
        if mask.any():
            pl.loc[mask, col] = pl.loc[mask, col].fillna(0) + amt
        else:
            new_row = {"line_item": cat}
            for c in month_cols: new_row[c] = amt if c == col else 0
            pl = pd.concat([pl, pd.DataFrame([new_row])], ignore_index=True)

    # Apply beer costs per month from session state
    mask_beer = pl["line_item"].str.lower().str.contains("costo cerveza", na=False)
    if mask_beer.any():
        for c in month_cols:
            beer_v = st.session_state.beer_costs.get(c, 0.0)
            if beer_v and beer_v > 0:
                pl.loc[mask_beer, c] = -abs(beer_v)

    # Apply category splits from session state
    splits = st.session_state.cat_splits
    for cat_label, kw in CAT_PL_MAP.items():
        pct = splits.get(cat_label, 50) / 100.0
        mask_cat = pl["line_item"].str.lower().str.contains(kw.lower(), na=False)
        if not mask_cat.any(): continue
        # Get original values from pl_base
        orig_mask = pl_base["line_item"].str.lower().str.contains(kw.lower(), na=False)
        if not orig_mask.any(): continue
        orig_row = pl_base[orig_mask].iloc[0]
        for c in month_cols:
            orig_v = orig_row.get(c, None)
            if orig_v is not None and pd.notna(orig_v):
                pl.loc[mask_cat, c] = orig_v * pct

    return pl, month_cols

def get_val(line_item_kw, col):
    """Get value for a P&L row + month col. Returns float or None."""
    pl, mc = get_pl()
    if pl.empty or col not in pl.columns: return None
    row = get_row(pl, line_item_kw)
    return safe_val(row, col)

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem 0;text-align:center;">
        <div style="font-size:1.1rem;font-weight:800;color:#ffffff;letter-spacing:0.02em;">
            🍺 UNSEEN CREATURES</div>
        <div style="font-size:0.68rem;color:#4a5568;font-weight:600;
                    letter-spacing:0.12em;margin-top:2px;">BREWING & BLENDING</div>
        <div style="width:40px;height:2px;background:linear-gradient(90deg,#2563eb,#10b981);
            margin:0.6rem auto 0 auto;border-radius:2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.subheader("➕ Agregar Transacción Manual")
    with st.expander("Nueva entrada"):
        m_desc  = st.text_input("Descripción", key="m_desc")
        m_cat   = st.selectbox("Categoría P&L", [
            "Ventas Netas","Food Cost","Bebida Taproom",
            "Payroll W2","Contractors/Emp Negro","Bandas",
            "Apps/Software","Toast Fees","Limpieza/Basura",
            "Facebook/Marketing","Amazon (compras varias)",
            "Inversion (mejoras/equipo)","Otros"
        ], key="m_cat")
        m_monto = st.number_input("Monto ($, negativo = gasto)",
                                  value=0.0, step=50.0, key="m_monto")
        m_mes   = st.selectbox("Mes", month_cols if month_cols else ["—"], key="m_mes")
        if st.button("Agregar entrada"):
            st.session_state.manual_entries.append({
                "descripcion": m_desc, "categoria": m_cat,
                "monto": m_monto, "col": m_mes
            })
            st.success(f"Agregado: {m_desc}")

    if st.session_state.manual_entries:
        st.caption(f"{len(st.session_state.manual_entries)} entradas manuales activas")
        if st.button("Limpiar entradas manuales"):
            st.session_state.manual_entries = []
            st.rerun()

    st.divider()
    if st.session_state.overrides:
        st.caption(f"{len(st.session_state.overrides)} celdas editadas")
        if st.button("Reset todas las ediciones"):
            st.session_state.overrides = {}
            st.rerun()

    st.divider()
    st.subheader("🔑 API Key")
    api_key_input = st.text_input("Anthropic API Key (para Recomendaciones)",
                                   type="password", key="api_key_sidebar")

    st.divider()
    if USE_DRIVE:
        st.markdown("""<div style='background:#1e3a2e;border:1px solid #22c55e;
                    border-radius:6px;padding:6px 10px;text-align:center;
                    font-size:0.72rem;color:#86efac;'>☁️ Google Drive</div>""",
                    unsafe_allow_html=True)
    elif _local_exists():
        st.markdown("""<div style='background:#1e2840;border:1px solid #3b82f6;
                    border-radius:6px;padding:6px 10px;text-align:center;
                    font-size:0.72rem;color:#93c5fd;'>💾 Datos locales</div>""",
                    unsafe_allow_html=True)
    else:
        st.markdown("""<div style='background:#3a1e1e;border:1px solid #ef4444;
                    border-radius:6px;padding:6px 10px;text-align:center;
                    font-size:0.72rem;color:#fca5a5;'>⚠️ Sin datos — agrega archivos</div>""",
                    unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────
col_logo, col_title, col_status = st.columns([0.06, 0.74, 0.20])
with col_logo:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1d4ed8,#2563eb);border-radius:14px;
        width:52px;height:52px;display:flex;align-items:center;justify-content:center;
        font-size:1.5rem;margin-top:4px;box-shadow:0 4px 14px rgba(37,99,235,0.4);">🍺</div>
    """, unsafe_allow_html=True)
with col_title:
    st.markdown("""
    <div style="padding-top:2px;">
        <div style="font-size:1.5rem;font-weight:800;color:#ffffff;letter-spacing:-0.5px;line-height:1.2;">
            Unseen Creatures</div>
        <div style="font-size:0.82rem;color:#6b7a94;font-weight:500;letter-spacing:0.04em;">
            BREWING & BLENDING — TAPROOM FINANCIAL DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)
with col_status:
    if pl_ok:
        st.markdown("""<div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);
            border-radius:8px;padding:0.4rem 0.8rem;margin-top:8px;text-align:center;">
            <span style="color:#10b981;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;">
            ● DATOS CARGADOS</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);
            border-radius:8px;padding:0.4rem 0.8rem;margin-top:8px;text-align:center;">
            <span style="color:#ef4444;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;">
            ● ERROR MODELO</span></div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:0.3rem'></div>", unsafe_allow_html=True)

if not pl_ok:
    st.error(f"Error cargando modelo: {pl_error}")

# ── TABS ───────────────────────────────────────────────────────────────────
tab_ov, tab_annual, tab_pl, tab_sales, tab_cf, tab_exp, tab_adj, tab_costs, tab_rec = st.tabs([
    "📊 Overview",
    "📅 Anual",
    "📋 P&L Detail",
    "🍻 Sales Analytics",
    "💰 Cash Flow",
    "📉 Gastos",
    "⚖️ Asignación",
    "🍺 Costos Cerveza",
    "💡 Recomendaciones"
])

# ══════════════════════════════════════════════════════════════════════════
# TAB: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
with tab_ov:
    st.header("Overview")

    available_months = []
    if not sales_day.empty:
        for yr in [2025, 2026]:
            for mo in range(1, 13):
                sub = sales_day[(sales_day["year"] == yr) & (sales_day["month"] == mo)]
                if not sub.empty:
                    available_months.append(f"{MONTHS_ES[mo]} {str(yr)[-2:]}")

    sel_mon_es = st.selectbox("Mes para Overview",
                               available_months if available_months else ["—"],
                               index=len(available_months)-1 if available_months else 0)
    try:
        mo_parts = sel_mon_es.split()
        sel_mon = MONTHS_REV[mo_parts[0]]
        sel_yr  = 2000 + int(mo_parts[1])
    except:
        sel_mon, sel_yr = 2, 2026

    prior_yr  = sel_yr - 1
    prior_m   = f"{MONTHS_ES[sel_mon]} {str(prior_yr)[-2:]}"
    sel_col   = col_for_month(month_cols, sel_mon, sel_yr)
    prior_col = col_for_month(month_cols, sel_mon, prior_yr)

    # KPIs from adjusted P&L
    pl_data, _ = get_pl()

    def gv(kw, col):
        if pl_data.empty or col is None: return None
        row = get_row(pl_data, kw)
        return safe_val(row, col)

    ventas_v = gv("ventas netas", sel_col)
    gm_v     = gv("margen bruto", sel_col)
    ebitda_v = gv("resultado operativo", sel_col)
    net_v    = gv("resultado neto", sel_col)
    ns_cur   = ventas_v or 0
    ns_py    = gv("ventas netas", prior_col) or 0
    delta    = f"{((ns_cur-ns_py)/abs(ns_py)*100):+.1f}% vs año anterior" if ns_py else None

    # Avg per guest
    avg_g = None
    if not sales_day.empty and ns_cur > 0:
        sub = sales_day[(sales_day["year"] == sel_yr) & (sales_day["month"] == sel_mon)]
        total_guests = sub["Total guests"].sum() if "Total guests" in sub.columns else 0
        if total_guests > 0: avg_g = ns_cur / total_guests

    # Breakeven — uses adjusted splits via get_pl()
    breakeven = None
    if pl_ok and month_cols and sel_col:
        total_fixed = 0
        for kw in ["gastos fijos","payroll","limpieza","facebook","amazon","otros","inversion","contractor"]:
            row = get_row(pl_data, kw)
            if row is not None:
                vals = [abs(row[c]) for c in month_cols if pd.notna(row.get(c))]
                if vals: total_fixed += sum(vals) / len(vals)
        gm_ratio = (gm_v / ventas_v) if (gm_v and ventas_v and ventas_v != 0) else 0.6
        breakeven = abs(total_fixed) / gm_ratio if gm_ratio > 0 else None

    col1,col2,col3,col4,col5 = st.columns(5)
    col1.metric("💵 Ventas Netas",   fmt_usd(ns_cur), delta)
    col2.metric("📈 Margen Bruto",   fmt_usd(gm_v),
                f"{gm_v/ventas_v*100:.1f}%" if gm_v and ventas_v else None)
    col3.metric("⚡ EBITDA",         fmt_usd(ebitda_v))
    col4.metric("💚 Resultado Neto", fmt_usd(net_v))
    col5.metric("🎯 Breakeven/mes",  fmt_usd(breakeven))

    if breakeven and ns_cur > 0:
        pct_be = ns_cur / breakeven * 100
        st.progress(min(pct_be/100, 1.0),
                    text=f"Ventas actuales = {pct_be:.0f}% del breakeven "
                         f"({'✅ sobre' if pct_be>=100 else '⚠️ bajo'} breakeven)")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("##### Tendencia Ventas & EBITDA")
        if pl_ok and month_cols:
            ventas_trend = []
            ebitda_trend = []
            for c in month_cols:
                ventas_trend.append(gv("ventas netas", c) or 0)
                ebitda_trend.append(gv("resultado operativo", c) or 0)
            fig_trend = go.Figure()
            fig_trend.add_bar(name="Ventas Netas", x=month_cols, y=ventas_trend,
                              marker_color=CLR["blue"], opacity=0.7)
            fig_trend.add_scatter(name="EBITDA", x=month_cols, y=ebitda_trend,
                                  mode="lines+markers",
                                  line=dict(color=CLR["green"], width=2.5),
                                  marker=dict(size=7))
            dc(fig_trend, height=260, barmode="overlay",
               yaxis_tickprefix="$", yaxis_tickformat=",.0f",
               legend=dict(**PT["legend"], orientation="h", y=-0.3))
            st.plotly_chart(fig_trend, use_container_width=True)

    with col_r:
        st.markdown("##### Breakeven Calculator")
        if breakeven and ns_cur > 0:
            fig_be = go.Figure(go.Bar(
                x=["Breakeven","Ventas Actuales"],
                y=[breakeven, ns_cur],
                marker_color=[CLR["orange"] if ns_cur < breakeven else CLR["green"],
                              CLR["blue"]],
                text=[fmt_usd(breakeven), fmt_usd(ns_cur)],
                textposition="outside",
                textfont=dict(color=TXT)
            ))
            dc(fig_be, height=260, yaxis_tickprefix="$", yaxis_tickformat=",.0f",
               margin=dict(t=10, b=40, l=10, r=10))
            st.plotly_chart(fig_be, use_container_width=True)
        else:
            st.info("Configura los costos en la tab ⚖️ Asignación y 🍺 Costos Cerveza para ver el breakeven.")

    st.divider()

    if prior_col and available_months:
        st.markdown("##### YoY — mismo mes")
        rows_yoy   = ["Ventas Netas","Total COGS","Resultado Operativo","Resultado Neto Taproom"]
        labels_yoy = ["Ventas","COGS","EBITDA","Neto"]
        fig_yoy = go.Figure()
        for col_yr, yr_label, color in [
            (prior_col, str(prior_yr), CLR["blue_l"]),
            (sel_col,   str(sel_yr),   CLR["blue"])
        ]:
            vals = [gv(r, col_yr) or 0 for r in rows_yoy]
            fig_yoy.add_bar(name=yr_label, x=labels_yoy, y=vals, marker_color=color)
        dc(fig_yoy, barmode="group", height=280,
           yaxis_tickprefix="$", yaxis_tickformat=",.0f",
           legend=dict(**PT["legend"], orientation="h", y=1.1))
        st.plotly_chart(fig_yoy, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2: ANUAL
# ══════════════════════════════════════════════════════════════════════════
with tab_annual:
    st.header("Resumen Anual")

    pl_data, _ = get_pl()

    if pl_ok and month_cols:
        yr_sel = st.selectbox("Año", [2025, 2026], key="yr_annual")
        yr_cols = [c for c in month_cols if str(c).endswith(str(yr_sel)[-2:])]

        kpi_rows = [("Ventas Netas","ventas netas"), ("Margen Bruto","margen bruto"),
                    ("Total COGS","total cogs"), ("EBITDA","resultado operativo"),
                    ("Resultado Neto","resultado neto")]
        kpi_vals = {}
        for label, kw in kpi_rows:
            row = get_row(pl_data, kw)
            if row is not None:
                kpi_vals[label] = sum(row[c] for c in yr_cols if pd.notna(row.get(c, None)) and row.get(c) is not None)

        if kpi_vals:
            cols_k = st.columns(len(kpi_vals))
            for i,(label,val) in enumerate(kpi_vals.items()):
                cols_k[i].metric(label, fmt_usd(val))

        st.divider()

        # Monthly summary table
        st.markdown("##### Tabla Mensual")
        # (keyword, display label, is_highlight)
        summary_kws = [
            ("ventas netas",        "Ventas Netas",           True),
            ("food cost",           "Food Cost",              False),
            ("bebida taproom",      "Bebida Taproom",         False),
            ("total cogs",          "Total COGS",             True),
            ("margen bruto",        "Margen Bruto",           True),
            ("total gastos",        "Total Gastos Operativos",True),
            ("resultado operativo", "EBITDA",                 True),
            ("resultado neto",      "Resultado Neto",         True),
        ]
        tbl = []
        for kw, display, _ in summary_kws:
            row = get_row(pl_data, kw)
            if row is None:
                continue
            entry = {"Línea": display}
            for c in yr_cols:
                v = safe_val(row, c)
                entry[c] = fmt_usd(v) if v is not None else "—"
            tbl.append(entry)
        highlight = ["Ventas Netas","Margen Bruto","EBITDA","Resultado Neto"]
        if tbl:
            tbl_df = pd.DataFrame(tbl).set_index("Línea")
            st.markdown(html_table(tbl_df, highlight_rows=highlight),
                        unsafe_allow_html=True)
        else:
            st.warning("No se encontraron datos del P&L para este año. "
                       "Verifica que modelo_unseen_v4.xlsx esté en C:\\brewery_analysis")

        # Monthly trend chart
        st.markdown("##### Ventas vs EBITDA mensual")
        v_vals = [gv("ventas netas", c) or 0 for c in yr_cols]
        e_vals = [gv("resultado operativo", c) or 0 for c in yr_cols]
        fig_ann = go.Figure()
        fig_ann.add_bar(name="Ventas", x=yr_cols, y=v_vals,
                        marker_color=CLR["blue"], opacity=0.75)
        fig_ann.add_scatter(name="EBITDA", x=yr_cols, y=e_vals,
                            mode="lines+markers",
                            line=dict(color=CLR["green"], width=2.5),
                            marker=dict(size=8, color=CLR["green"]))
        dc(fig_ann, height=300, barmode="overlay",
           yaxis_tickprefix="$", yaxis_tickformat=",.0f",
           legend=dict(**PT["legend"], orientation="h", y=-0.3))
        st.plotly_chart(fig_ann, use_container_width=True)
    else:
        st.info("Carga el modelo para ver el resumen anual.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 3: P&L DETAIL
# ══════════════════════════════════════════════════════════════════════════
with tab_pl:
    st.header("P&L Detail")

    pl_data, _ = get_pl()

    if pl_ok and not pl_data.empty:
        yr_pl = st.selectbox("Año", [2025, 2026], key="yr_pl")
        show_cols = [c for c in month_cols if str(c).endswith(str(yr_pl)[-2:])]

        highlight_rows = {
            "ventas netas": CLR["blue"],
            "margen bruto": CLR["green"],
            "resultado operativo": CLR["teal"],
            "resultado neto": CLR["purple"],
            "total cogs": CLR["orange"],
            "total gastos": CLR["red"],
        }

        display_df = pl_data[["line_item"] + show_cols].copy()
        display_df = display_df.rename(columns={"line_item": "Línea P&L"})
        for c in show_cols:
            display_df[c] = display_df[c].apply(
                lambda v: fmt_usd(v) if pd.notna(v) else "—")

        st.dataframe(display_df.set_index("Línea P&L"),
                     use_container_width=True, height=500)

        st.divider()
        st.markdown("##### % de Ventas Netas")
        ventas_row = get_row(pl_data, "ventas netas")
        if ventas_row is not None:
            pct_rows = ["Total COGS","Total Gastos Operativos",
                        "Resultado Operativo","Resultado Neto Taproom"]
            pct_data = {}
            for row_label in pct_rows:
                import re as _re
                mask = pl_data["line_item"].str.lower().str.contains(
                    _re.escape(row_label[:10].lower()), na=False)
                if mask.any():
                    row = pl_data[mask].iloc[0]
                    entry = {}
                    for c in show_cols:
                        vn = safe_val(ventas_row, c)
                        rv = safe_val(row, c)
                        if vn and vn != 0 and rv is not None:
                            entry[c] = f"{rv/vn*100:.1f}%"
                        else:
                            entry[c] = "—"
                    pct_data[row["line_item"]] = entry
            if pct_data:
                pct_df = pd.DataFrame(pct_data).T.rename_axis("Línea")
                st.markdown(html_table(pct_df), unsafe_allow_html=True)
    else:
        st.info("Carga el modelo para ver el P&L.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 4: SALES ANALYTICS
# ══════════════════════════════════════════════════════════════════════════
with tab_sales:
    st.header("🍻 Sales Analytics")

    if not sales_day.empty:
        sa_yr = st.selectbox("Año", [2025, 2026], key="yr_sales")
        sub   = sales_day[sales_day["year"] == sa_yr]
        prefix_sa = "25" if sa_yr == 2025 else "26"
        MONTHS_ES_SA = ["Ene","Feb","Mar","Abr","May","Jun",
                        "Jul","Ago","Sep","Oct","Nov","Dic"]

        # ── KPIs from CF data ──────────────────────────────────────────
        cf_yr_keys = [f"{m} {prefix_sa}" for m in MONTHS_ES_SA if f"{m} {prefix_sa}" in cf_data]
        total_ventas_cf  = sum(cf_data[m].get("ingresos_taproom", 0) or 0 for m in cf_yr_keys)
        total_guests_cf  = sum(cf_data[m].get("total_guests", 0) or 0 for m in cf_yr_keys)
        avg_guest_cf     = (sum(cf_data[m].get("avg_guest", 0) or 0 for m in cf_yr_keys)
                            / len(cf_yr_keys)) if cf_yr_keys else 0
        yoy_vals         = [cf_data[m].get("variacion_yoy", None) for m in cf_yr_keys]
        yoy_vals         = [v for v in yoy_vals if v is not None]
        avg_yoy          = sum(yoy_vals) / len(yoy_vals) if yoy_vals else None

        # From toast daily data
        total_ventas_toast = sub["Net sales"].sum() if "Net sales" in sub.columns else 0
        total_orders       = sub["Total orders"].sum() if "Total orders" in sub.columns else 0
        total_guests_toast = sub["Total guests"].sum() if "Total guests" in sub.columns else 0

        sk1,sk2,sk3,sk4,sk5 = st.columns(5)
        sk1.metric("💵 Ventas Totales",   fmt_usd(total_ventas_toast or total_ventas_cf))
        sk2.metric("👥 Guests Totales",   f"{int(total_guests_toast or total_guests_cf):,}")
        sk3.metric("🧾 Órdenes Totales",  f"{int(total_orders):,}" if total_orders else "—")
        sk4.metric("🎯 Avg/Guest",        f"${avg_guest_cf:.2f}" if avg_guest_cf else "—")
        sk5.metric("📈 Crecimiento YoY",  f"{avg_yoy*100:+.1f}%" if avg_yoy else "—")

        st.divider()

        # ── Ventas diarias + tendencia ─────────────────────────────────
        st.markdown("##### Ventas Diarias")
        if "Net sales" in sub.columns:
            sub_sorted = sub.sort_values("date")
            # Rolling 7-day avg
            sub_sorted["roll7"] = sub_sorted["Net sales"].rolling(7, min_periods=1).mean()
            fig_daily = go.Figure()
            fig_daily.add_scatter(
                x=sub_sorted["date"], y=sub_sorted["Net sales"],
                name="Ventas diarias",
                fill="tozeroy", fillcolor="rgba(59,130,246,0.10)",
                line=dict(color=CLR["blue"], width=1), mode="lines"
            )
            fig_daily.add_scatter(
                x=sub_sorted["date"], y=sub_sorted["roll7"],
                name="Media 7 días",
                line=dict(color=CLR["orange"], width=2.5, dash="dot"),
                mode="lines"
            )
            dc(fig_daily, height=300,
               xaxis_tickformat="%b %Y",
               yaxis_tickprefix="$", yaxis_tickformat=",.0f",
               legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_daily, use_container_width=True)

        st.divider()

        # ── Revenue mix from CF (monthly stacked) ─────────────────────
        has_cf_mix = any(cf_data.get(m, {}).get("draft_beer") for m in cf_yr_keys)
        if has_cf_mix:
            st.markdown("##### Mix de Ingresos por Categoría — Mensual")
            mix_cats   = ["draft_beer","food_sales","wine","happy_hour",
                          "bottle_beer","uber","retail","na_bev"]
            mix_labels = ["Draft Beer","Food","Wine","Happy Hour",
                          "Bottle Beer","Uber Eats","Retail","NA Beverages"]
            fig_mix = go.Figure()
            for cat, label, color in zip(mix_cats, mix_labels, CAT_COLORS):
                vals = [cf_data[m].get(cat, 0) or 0 for m in cf_yr_keys]
                if any(v > 0 for v in vals):
                    fig_mix.add_bar(name=label, x=cf_yr_keys, y=vals, marker_color=color)
            dc(fig_mix, barmode="stack", height=320,
               yaxis_tickprefix="$", yaxis_tickformat=",.0f",
               legend=dict(orientation="h", y=-0.35))
            st.plotly_chart(fig_mix, use_container_width=True)

            # Revenue mix donut for full year
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Mix de Ventas — Año completo")
                donut_vals = {lbl: sum(cf_data[m].get(cat,0) or 0 for m in cf_yr_keys)
                              for cat, lbl in zip(mix_cats, mix_labels)}
                donut_vals = {k:v for k,v in donut_vals.items() if v > 0}
                fig_donut = go.Figure(go.Pie(
                    labels=list(donut_vals.keys()),
                    values=list(donut_vals.values()),
                    hole=0.55, marker=dict(colors=CAT_COLORS),
                    textinfo="percent+label",
                    textfont=dict(color=TXT, size=11),
                    insidetextfont=dict(color=TXT),
                ))
                dc(fig_donut, height=340, showlegend=False,
                   margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_donut, use_container_width=True)

            with c2:
                st.markdown("##### Draft Beer vs Food vs Wine — Tendencia")
                fig_3cat = go.Figure()
                for cat, label, color in [
                    ("draft_beer","Draft Beer",CLR["blue"]),
                    ("food_sales","Food",CLR["green"]),
                    ("wine","Wine",CLR["purple"]),
                ]:
                    vals = [cf_data[m].get(cat, 0) or 0 for m in cf_yr_keys]
                    fig_3cat.add_scatter(
                        x=cf_yr_keys, y=vals, name=label,
                        mode="lines+markers",
                        line=dict(color=color, width=2.5),
                        marker=dict(size=7)
                    )
                dc(fig_3cat, height=340,
                   yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                   legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig_3cat, use_container_width=True)

        st.divider()

        # ── Guests & ticket promedio ───────────────────────────────────
        st.markdown("##### Guests & Ticket Promedio por Mes")
        has_guests = any(cf_data.get(m, {}).get("total_guests") for m in cf_yr_keys)
        if has_guests:
            gc1, gc2 = st.columns(2)
            with gc1:
                g_vals   = [cf_data[m].get("total_guests", 0) or 0 for m in cf_yr_keys]
                # Compare with prior year if available
                prior_prefix = "24" if sa_yr == 2025 else "25"
                fig_guests = go.Figure()
                fig_guests.add_bar(
                    name=str(sa_yr), x=cf_yr_keys, y=g_vals,
                    marker_color=CLR["blue"],
                    text=[f"{int(v):,}" for v in g_vals],
                    textposition="outside", textfont=dict(color=TXT)
                )
                dc(fig_guests, height=300,
                   yaxis_tickformat=",",
                   margin=dict(t=30, b=40, l=10, r=10))
                st.plotly_chart(fig_guests, use_container_width=True)
            with gc2:
                avg_vals = [cf_data[m].get("avg_guest", 0) or 0 for m in cf_yr_keys]
                fig_avg = go.Figure()
                fig_avg.add_scatter(
                    x=cf_yr_keys, y=avg_vals, name="Avg/Guest",
                    mode="lines+markers",
                    line=dict(color=CLR["teal"], width=2.5),
                    marker=dict(size=8, color=CLR["teal"]),
                    fill="tozeroy", fillcolor="rgba(20,184,166,0.12)"
                )
                # Add target line at $32
                fig_avg.add_hline(y=32, line_dash="dash",
                                  line_color=CLR["orange"],
                                  annotation_text="Target $32",
                                  annotation_font_color=CLR["orange"])
                dc(fig_avg, height=300,
                   yaxis_tickprefix="$", yaxis_tickformat=".2f")
                st.plotly_chart(fig_avg, use_container_width=True)

        st.divider()

        # ── YoY comparison from CF summary ────────────────────────────
        if sa_yr == 2025 and any(cf_data.get(m, {}).get("variacion_yoy") for m in cf_yr_keys):
            st.markdown("##### Crecimiento YoY por Mes (vs 2024)")
            yoy_m = [cf_data[m].get("variacion_yoy", 0) or 0 for m in cf_yr_keys]
            colors_yoy = [CLR["green"] if v >= 0 else CLR["red"] for v in yoy_m]
            fig_yoy = go.Figure(go.Bar(
                x=cf_yr_keys, y=[v*100 for v in yoy_m],
                marker_color=colors_yoy,
                text=[f"{v*100:+.1f}%" for v in yoy_m],
                textposition="outside", textfont=dict(color=TXT)
            ))
            dc(fig_yoy, height=280,
               yaxis_ticksuffix="%", yaxis_tickformat=".1f")
            st.plotly_chart(fig_yoy, use_container_width=True)
            st.divider()

        # ── Day of week analysis ───────────────────────────────────────
        st.markdown("##### Análisis por Día de Semana")
        dow_order  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow_labels = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        if "Net sales" in sub.columns and "dow" in sub.columns:
            dow_agg = sub.groupby("dow").agg(
                avg_sales=("Net sales","mean"),
                total_sales=("Net sales","sum"),
                count=("Net sales","count")
            ).reindex(dow_order).fillna(0)

            da1, da2 = st.columns(2)
            with da1:
                st.markdown("###### Venta Promedio por Día")
                fig_dow = go.Figure(go.Bar(
                    x=dow_labels, y=dow_agg["avg_sales"].values,
                    marker_color=CAT_COLORS[:7],
                    text=[fmt_usd(v) for v in dow_agg["avg_sales"].values],
                    textposition="outside", textfont=dict(color=TXT)
                ))
                dc(fig_dow, height=280,
                   yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                   margin=dict(t=30, b=40, l=10, r=10))
                st.plotly_chart(fig_dow, use_container_width=True)
            with da2:
                st.markdown("###### Días operados por día de semana")
                fig_cnt = go.Figure(go.Bar(
                    x=dow_labels, y=dow_agg["count"].values,
                    marker_color=CAT_COLORS[2:9],
                    text=[str(int(v)) for v in dow_agg["count"].values],
                    textposition="outside", textfont=dict(color=TXT)
                ))
                dc(fig_cnt, height=280,
                   margin=dict(t=30, b=40, l=10, r=10))
                st.plotly_chart(fig_cnt, use_container_width=True)

        st.divider()

        # ── Monthly summary table ──────────────────────────────────────
        if has_cf_mix:
            st.markdown("##### Tabla Resumen de Ventas por Mes")
            mix_table = []
            for m in cf_yr_keys:
                d = cf_data.get(m, {})
                mix_table.append({
                    "Mes":        m,
                    "Draft Beer": fmt_usd(d.get("draft_beer") or 0),
                    "Food":       fmt_usd(d.get("food_sales") or 0),
                    "Wine":       fmt_usd(d.get("wine") or 0),
                    "Happy Hour": fmt_usd(d.get("happy_hour") or 0),
                    "Bottle":     fmt_usd(d.get("bottle_beer") or 0),
                    "Uber":       fmt_usd(d.get("uber") or 0),
                    "Total":      fmt_usd(d.get("ingresos_taproom") or 0),
                    "Guests":     f"{int(d.get('total_guests') or 0):,}",
                    "Avg/Guest":  f"${d.get('avg_guest') or 0:.2f}",
                })
            mix_df = pd.DataFrame(mix_table).set_index("Mes")
            st.markdown(html_table(mix_df), unsafe_allow_html=True)

    else:
        st.info("No se encontraron datos de ventas.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 5: CASH FLOW
# ══════════════════════════════════════════════════════════════════════════
with tab_cf:
    st.header("Cash Flow & Finanzas")

    if not cf_data:
        st.warning("No se encontraron los archivos de Cash Flow. "
                   "Coloca 'Unseen - Cash Flow 2025.xlsx' y 'Unseen - Cash Flow 2026.xlsx' "
                   "en C:\\brewery_analysis")
    else:
        # ── Year selector & month list ──────────────────────────────────
        cf_yr = st.selectbox("Año", [2025, 2026], key="yr_cf")
        prefix = "25" if cf_yr == 2025 else "26"
        MONTHS_LABEL = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        cf_months = [f"{m} {prefix}" for m in MONTHS_LABEL if f"{m} {prefix}" in cf_data]

        if not cf_months:
            st.info(f"No hay datos de Cash Flow para {cf_yr}.")
        else:
            # ── KPI summary row ─────────────────────────────────────────
            total_ing  = sum(cf_data[m].get('total_ingresos', 0) or 0 for m in cf_months)
            total_egr  = sum(cf_data[m].get('total_egresos', 0) or 0 for m in cf_months)
            total_ap   = sum(cf_data[m].get('aporte_afuera', 0) or 0 for m in cf_months)
            net_flow   = total_ing - total_egr
            last_saldo = cf_data[cf_months[-1]].get('saldo_final')

            kc1, kc2, kc3, kc4, kc5 = st.columns(5)
            kc1.metric("💰 Total Ingresos", fmt_usd(total_ing))
            kc2.metric("📤 Total Egresos",  fmt_usd(total_egr))
            kc3.metric("📊 Flujo Neto",     fmt_usd(net_flow),
                       delta="positivo" if net_flow >= 0 else "negativo")
            kc4.metric("🤝 Aportes Externos", fmt_usd(total_ap))
            kc5.metric("🏦 Saldo Final",    fmt_usd(last_saldo))

            st.divider()

            # ── Ingresos vs Egresos monthly bar chart ───────────────────
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("##### Ingresos vs Egresos por Mes")
                ing_vals = [cf_data[m].get('total_ingresos', 0) or 0 for m in cf_months]
                egr_vals = [cf_data[m].get('total_egresos', 0) or 0 for m in cf_months]
                fig_ie = go.Figure()
                fig_ie.add_bar(name="Ingresos", x=cf_months, y=ing_vals,
                               marker_color=CLR["green"], opacity=0.85)
                fig_ie.add_bar(name="Egresos", x=cf_months, y=egr_vals,
                               marker_color=CLR["red"], opacity=0.85)
                dc(fig_ie, barmode="group", height=300,
                   yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                   legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig_ie, use_container_width=True)

            with col_r:
                st.markdown("##### Saldo de Caja por Mes")
                saldo_vals = [cf_data[m].get('saldo_final') for m in cf_months]
                colors_s = [CLR["green"] if (v or 0) >= 0 else CLR["red"] for v in saldo_vals]
                fig_saldo = go.Figure(go.Bar(
                    x=cf_months, y=[v or 0 for v in saldo_vals],
                    marker_color=colors_s,
                    text=[fmt_usd(v) for v in saldo_vals],
                    textposition="outside", textfont=dict(color=TXT)
                ))
                dc(fig_saldo, height=300,
                   yaxis_tickprefix="$", yaxis_tickformat=",.0f")
                st.plotly_chart(fig_saldo, use_container_width=True)

            st.divider()

            # ── Revenue mix from CF summary sheet (2025 only) ───────────
            has_mix = any(cf_data.get(m, {}).get('draft_beer') for m in cf_months)
            if has_mix:
                st.markdown("##### Mix de Ingresos del Taproom por Categoría")
                mix_cats = ['draft_beer','food_sales','wine','happy_hour',
                            'bottle_beer','uber','retail','na_bev']
                mix_labels = ['Draft Beer','Food','Wine','Happy Hour',
                              'Bottle Beer','Uber Eats','Retail','NA Beverages']
                fig_mix = go.Figure()
                for cat, label, color in zip(mix_cats, mix_labels, CAT_COLORS):
                    vals = [cf_data[m].get(cat, 0) or 0 for m in cf_months]
                    if any(v > 0 for v in vals):
                        fig_mix.add_bar(name=label, x=cf_months, y=vals,
                                        marker_color=color)
                dc(fig_mix, barmode="stack", height=320,
                   yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                   legend=dict(orientation="h", y=-0.35))
                st.plotly_chart(fig_mix, use_container_width=True)

                # Guest metrics
                has_guests = any(cf_data.get(m, {}).get('total_guests') for m in cf_months)
                if has_guests:
                    st.markdown("##### Guests & Ticket Promedio")
                    gc1, gc2 = st.columns(2)
                    with gc1:
                        g_vals = [cf_data[m].get('total_guests', 0) or 0 for m in cf_months]
                        fig_g = go.Figure(go.Bar(
                            x=cf_months, y=g_vals, marker_color=CLR["purple"],
                            text=[f"{int(v):,}" for v in g_vals],
                            textposition="outside", textfont=dict(color=TXT)
                        ))
                        dc(fig_g, height=260, yaxis_tickformat=",")
                        st.plotly_chart(fig_g, use_container_width=True)
                    with gc2:
                        avg_vals = [cf_data[m].get('avg_guest', 0) or 0 for m in cf_months]
                        fig_avg = go.Figure(go.Scatter(
                            x=cf_months, y=avg_vals,
                            mode="lines+markers",
                            line=dict(color=CLR["teal"], width=2.5),
                            marker=dict(size=8),
                            fill="tozeroy", fillcolor="rgba(20,184,166,0.12)"
                        ))
                        dc(fig_avg, height=260,
                           yaxis_tickprefix="$", yaxis_tickformat=".2f")
                        st.plotly_chart(fig_avg, use_container_width=True)

                st.divider()

            # ── Expense breakdown ────────────────────────────────────────
            st.markdown("##### Desglose de Egresos por Categoría")
            exp_cats = [
                ('payroll',       'Payroll W2',     CLR["blue"]),
                ('contractors',   'Contractors',    CLR["purple"]),
                ('tips',          'Tips',           CLR["teal"]),
                ('taxes',         'Taxes',          CLR["orange"]),
                ('food_cost',     'Food Cost',      CLR["green"]),
                ('bebida_taproom','Bebida Taproom',  CLR["blue_l"]),
                ('bands',         'Bandas',         CLR["red"]),
                ('renta',         'Renta',          CLR["gray"]),
                ('apps',          'Apps/Software',  "#06b6d4"),
                ('limpieza',      'Limpieza',       "#84cc16"),
                ('amazon',        'Amazon',         "#ec4899"),
                ('facebook',      'Facebook',       "#a78bfa"),
                ('ice_machine',   'Ice Machine',    "#fb923c"),
                ('transfer_fee',  'Transfer Fee',   "#34d399"),
                ('inversion',     'Inversión',      "#f472b6"),
            ]
            fig_exp = go.Figure()
            for key, label, color in exp_cats:
                vals = [cf_data[m].get(key, 0) or 0 for m in cf_months]
                if any(v > 0 for v in vals):
                    fig_exp.add_bar(name=label, x=cf_months, y=vals, marker_color=color)
            dc(fig_exp, barmode="stack", height=380,
               yaxis_tickprefix="$", yaxis_tickformat=",.0f",
               legend=dict(orientation="h", y=-0.45))
            st.plotly_chart(fig_exp, use_container_width=True)

            # Expense table
            st.markdown("##### Tabla de Egresos Detallada")
            exp_tbl = []
            for key, label, _ in exp_cats:
                row_d = {"Categoría": label}
                for m in cf_months:
                    row_d[m] = fmt_usd(cf_data[m].get(key, 0) or 0)
                total_v = sum(cf_data[m].get(key, 0) or 0 for m in cf_months)
                row_d["TOTAL"] = fmt_usd(total_v)
                if total_v > 0:
                    exp_tbl.append(row_d)
            if exp_tbl:
                exp_df = pd.DataFrame(exp_tbl).set_index("Categoría")
                st.markdown(html_table(exp_df), unsafe_allow_html=True)

            st.divider()

            # ── Aportes externos ─────────────────────────────────────────
            ap_months = [(m, cf_data[m].get('aporte_afuera', 0) or 0)
                         for m in cf_months if (cf_data[m].get('aporte_afuera') or 0) > 0]
            if ap_months:
                st.markdown("##### Aportes Externos de Capital")
                st.warning("⚠️ Estos meses tuvieron aportes externos de capital. "
                           "No son ingresos operativos del negocio.")
                ap_labels = [x[0] for x in ap_months]
                ap_vals   = [x[1] for x in ap_months]
                fig_ap = go.Figure(go.Bar(
                    x=ap_labels, y=ap_vals,
                    marker_color=CLR["orange"],
                    text=[fmt_usd(v) for v in ap_vals],
                    textposition="outside", textfont=dict(color=TXT)
                ))
                dc(fig_ap, height=260,
                   yaxis_tickprefix="$", yaxis_tickformat=",.0f")
                st.plotly_chart(fig_ap, use_container_width=True)
                st.divider()

    # ── Toast Capital ─────────────────────────────────────────────────────
    st.markdown("##### Toast Capital — Detalle de Créditos")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("""
        <div style="background:#1e2436;border:1px solid #2d3a52;border-radius:12px;padding:1rem;">
        <div style="color:#7888a0;font-size:0.75rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.5rem;">CRÉDITO 1 — Refinanciado Oct 2025</div>
        <div style="color:#ffffff;font-size:1.3rem;font-weight:700;">$46,200 originales</div>
        <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.3rem;">Factor 1.28x · Total a pagar: ~$59,136</div>
        <div style="color:#f59e0b;font-size:0.85rem;font-weight:600;margin-top:0.5rem;">APR real: ~56%</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div style="background:#1e2436;border:1px solid #2d3a52;border-radius:12px;padding:1rem;">
        <div style="color:#7888a0;font-size:0.75rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.5rem;">CRÉDITO 2 — Activo</div>
        <div style="color:#ffffff;font-size:1.3rem;font-weight:700;">$20,697 neto</div>
        <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.3rem;">Factor 1.25x · Total: ~$25,871 · Holdback: 9.55%</div>
        <div style="color:#ef4444;font-size:0.85rem;font-weight:600;margin-top:0.5rem;">APR real: ~{:.0f}%</div>
        </div>
        """.format(apr_from_factor(1.25, 6)), unsafe_allow_html=True)

    if not payout.empty:
        st.divider()
        st.markdown("##### Cuota Mensual Toast Capital (Holdback sobre ventas brutas)")
        st.info("💡 El holdback es el pago automático de la cuota del crédito Toast. "
                "Toast retiene un % de cada venta bruta diaria hasta saldar la deuda. "
                "Tasa original: ~11% · Tasa renegociada: ~9.5%. "
                "No es un impuesto ni un fee — es amortización del préstamo.")
        pay_m = payout.groupby(["year","month"])["Withholdings"].sum().reset_index()
        pay_m["label"] = pay_m.apply(
            lambda r: f"{MONTHS_ES.get(int(r['month']),str(r['month']))} {str(int(r['year']))[-2:]}",
            axis=1)
        pay_m = pay_m[pay_m["Withholdings"].notna() & (pay_m["Withholdings"] != 0)]
        if not pay_m.empty:
            total_holdback = pay_m["Withholdings"].sum()
            avg_holdback   = pay_m["Withholdings"].mean()
            hk1, hk2, hk3 = st.columns(3)
            hk1.metric("Total pagado (holdback)", fmt_usd(total_holdback))
            hk2.metric("Promedio mensual",        fmt_usd(avg_holdback))
            hk3.metric("Meses con retención",     str(len(pay_m)))
            fig_hb = go.Figure(go.Bar(
                x=pay_m["label"], y=pay_m["Withholdings"],
                marker_color=CLR["orange"],
                text=[fmt_usd(v) for v in pay_m["Withholdings"]],
                textposition="outside", textfont=dict(color=TXT)
            ))
            dc(fig_hb, height=300, yaxis_tickprefix="$", yaxis_tickformat=",.0f")
            st.plotly_chart(fig_hb, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 6: GASTOS
# ══════════════════════════════════════════════════════════════════════════
with tab_exp:
    st.header("Análisis de Gastos")

    pl_data, _ = get_pl()

    if pl_ok and not pl_data.empty:
        yr_e = st.selectbox("Año", [2025, 2026], key="yr_exp")
        exp_cols = [c for c in month_cols if str(c).endswith(str(yr_e)[-2:])]

        opex_rows = [r for r in pl_data["line_item"].tolist()
                     if any(kw in r.lower() for kw in
                            ["payroll","contractor","bandas","apps","toast fees",
                             "tips","ice","cintas","limpieza","facebook","amazon",
                             "inversion","transfer","otros"])]

        if opex_rows:
            st.markdown("##### Gastos Operativos por Mes")
            fig_stack = go.Figure()
            for i, row_name in enumerate(opex_rows[:8]):
                row = get_row(pl_data, row_name[:10])
                if row is None: continue
                vals = [abs(safe_val(row, c) or 0) for c in exp_cols]
                fig_stack.add_bar(name=row_name[:25], x=exp_cols, y=vals,
                                  marker_color=CAT_COLORS[i % len(CAT_COLORS)])
            dc(fig_stack, barmode="stack", height=350,
               yaxis_tickprefix="$", yaxis_tickformat=",.0f",
               legend=dict(**PT["legend"], orientation="h", y=-0.4))
            st.plotly_chart(fig_stack, use_container_width=True)

            # Pie for latest month
            if exp_cols:
                last_col = exp_cols[-1]
                pie_vals = [(r, abs(safe_val(get_row(pl_data, r[:10]), last_col) or 0))
                            for r in opex_rows[:10]]
                pie_vals = [(r, v) for r, v in pie_vals if v > 0]
                if pie_vals:
                    labels_p, vals_p = zip(*pie_vals)
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown(f"##### Mix Gastos — {last_col}")
                        fig_pie = go.Figure(go.Pie(
                            labels=labels_p, values=vals_p,
                            marker=dict(colors=CAT_COLORS),
                            textfont=dict(color=TXT, size=10),
                            insidetextfont=dict(color=TXT),
                            hole=0.4
                        ))
                        dc(fig_pie, height=320, showlegend=False,
                           margin=dict(t=10, b=10, l=10, r=10))
                        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Carga el modelo para ver los gastos.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 7: ASIGNACIÓN — central control, propagates to all other tabs
# ══════════════════════════════════════════════════════════════════════════
with tab_adj:
    st.header("⚖️ Asignación de Gastos: Taproom vs Cervecería")
    st.caption("Los cambios aquí se reflejan automáticamente en Overview, P&L, Breakeven, y todos los demás tabs.")

    st.info("💡 El % Taproom define cuánto del costo absorbe el taproom. "
            "El resto queda en la cervecería. Cambia los sliders y ve el impacto en tiempo real.")

    cats = list(CAT_DEFAULTS.keys())
    mid  = len(cats) // 2 + len(cats) % 2
    col_left, col_right = st.columns(2)

    with col_left:
        for cat in cats[:mid]:
            val = st.slider(
                cat, min_value=0, max_value=100,
                value=st.session_state.cat_splits.get(cat, CAT_DEFAULTS[cat]),
                step=5, format="%d%% Taproom", key=f"split_{cat}"
            )
            st.session_state.cat_splits[cat] = val
            if val == 100:
                st.caption("✅ 100% Taproom")
            elif val == 0:
                st.caption("🏭 100% Cervecería")
            else:
                st.caption(f"Taproom {val}%  |  Cervecería {100-val}%")

    with col_right:
        for cat in cats[mid:]:
            val = st.slider(
                cat, min_value=0, max_value=100,
                value=st.session_state.cat_splits.get(cat, CAT_DEFAULTS[cat]),
                step=5, format="%d%% Taproom", key=f"split_{cat}"
            )
            st.session_state.cat_splits[cat] = val
            if val == 100:
                st.caption("✅ 100% Taproom")
            elif val == 0:
                st.caption("🏭 100% Cervecería")
            else:
                st.caption(f"Taproom {val}%  |  Cervecería {100-val}%")

    st.divider()

    # Impact table
    if pl_ok and month_cols:
        st.markdown("##### Impacto en Gastos por Categoría")
        pl_adj, _ = get_pl()
        impact_rows = []
        for cat_label, kw in CAT_PL_MAP.items():
            pct = st.session_state.cat_splits.get(cat_label, 50)
            orig_row = get_row(pl_base, kw)
            adj_row  = get_row(pl_adj, kw)
            if orig_row is None: continue
            orig_avg = abs(sum(orig_row[c] for c in month_cols if pd.notna(orig_row.get(c,None))) / max(len(month_cols),1))
            adj_avg  = abs(sum(adj_row[c] for c in month_cols if pd.notna(adj_row.get(c,None))) / max(len(month_cols),1)) if adj_row is not None else 0
            impact_rows.append({
                "Categoría": cat_label,
                "% Taproom": f"{pct}%",
                "Costo Original/mes": fmt_usd(orig_avg),
                "Costo Taproom/mes": fmt_usd(adj_avg),
                "Costo Cervecería/mes": fmt_usd(orig_avg - adj_avg),
            })
        if impact_rows:
            imp_df = pd.DataFrame(impact_rows).set_index("Categoría")
            st.markdown(html_table(imp_df), unsafe_allow_html=True)

        # EBITDA comparison chart
        st.markdown("##### EBITDA Ajustado vs Original (promedio mensual)")
        orig_ebitda_vals = []
        adj_ebitda_vals  = []
        for c in month_cols:
            orig_row_e = get_row(pl_base, "resultado operativo")
            adj_row_e  = get_row(pl_adj, "resultado operativo")
            orig_ebitda_vals.append(safe_val(orig_row_e, c) or 0)
            adj_ebitda_vals.append(safe_val(adj_row_e, c) or 0)

        fig_cmp = go.Figure()
        fig_cmp.add_bar(name="EBITDA Original", x=month_cols, y=orig_ebitda_vals,
                        marker_color=CLR["blue_l"], opacity=0.8)
        fig_cmp.add_bar(name="EBITDA Ajustado", x=month_cols, y=adj_ebitda_vals,
                        marker_color=CLR["green"], opacity=0.8)
        dc(fig_cmp, barmode="group", height=320,
           yaxis_tickprefix="$", yaxis_tickformat=",.0f",
           legend=dict(**PT["legend"], orientation="h", y=1.1))
        st.plotly_chart(fig_cmp, use_container_width=True)

    st.divider()
    if st.button("🔄 Resetear a valores default"):
        st.session_state.cat_splits = dict(CAT_DEFAULTS)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# TAB 8: COSTOS CERVEZA — per-month beer cost input
# ══════════════════════════════════════════════════════════════════════════
with tab_costs:
    st.header("🍺 Costos de Cerveza por Mes")
    st.caption("Ingresa el costo de transferencia de producción al taproom para cada mes. "
               "Los valores se aplican automáticamente al P&L, COGS y EBITDA en todos los tabs.")

    yr_bc = st.selectbox("Año", [2025, 2026], key="yr_beercost")
    prefix = "25" if yr_bc == 2025 else "26"
    month_keys = [f"{MONTHS_ES[m]} {prefix}" for m in range(1, 13)]

    st.markdown("##### Costo por mes ($)")
    st.info("💡 Ingresa el costo total de cerveza que se transfiere al taproom ese mes (no por barril, sino el total).")

    col_a, col_b, col_c = st.columns(3)
    cols_cycle = [col_a, col_b, col_c]
    for i, mk in enumerate(month_keys):
        with cols_cycle[i % 3]:
            cur_val = st.session_state.beer_costs.get(mk, 0.0)
            new_val = st.number_input(
                mk,
                min_value=0.0,
                value=float(cur_val),
                step=100.0,
                format="%.0f",
                key=f"beer_{mk}"
            )
            st.session_state.beer_costs[mk] = new_val

    st.divider()

    # Show summary
    active = {k: v for k, v in st.session_state.beer_costs.items()
              if k.endswith(prefix) and v > 0}
    if active:
        st.markdown("##### Resumen — Costo Cerveza Ingresado")
        total_bc = sum(active.values())
        avg_bc   = total_bc / len(active)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total año", fmt_usd(total_bc))
        c2.metric("Promedio mensual", fmt_usd(avg_bc))
        c3.metric("Meses con datos", str(len(active)))

        fig_bc = go.Figure(go.Bar(
            x=list(active.keys()),
            y=list(active.values()),
            marker_color=CLR["teal"],
            text=[fmt_usd(v) for v in active.values()],
            textposition="outside", textfont=dict(color=TXT)
        ))
        dc(fig_bc, height=280,
           yaxis_tickprefix="$", yaxis_tickformat=",.0f",
           margin=dict(t=10, b=40, l=10, r=10))
        st.plotly_chart(fig_bc, use_container_width=True)
    else:
        st.info(f"No hay costos de cerveza ingresados para {yr_bc}. Usa los inputs de arriba para agregarlos.")

    st.divider()
    if st.button("🗑️ Limpiar todos los costos de cerveza"):
        for k in list(st.session_state.beer_costs.keys()):
            st.session_state.beer_costs[k] = 0.0
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# TAB 9: RECOMENDACIONES (AI)
# ══════════════════════════════════════════════════════════════════════════
with tab_rec:
    st.header("💡 Recomendaciones AI")

    api_key = (st.session_state.get("api_key_sidebar") or
               os.environ.get("ANTHROPIC_API_KEY", ""))

    if not api_key:
        st.warning("Ingresa tu API Key de Anthropic en el sidebar para usar esta función.")
    else:
        pl_data, _ = get_pl()
        recent_col = month_cols[-1] if month_cols else None

        ventas_r  = safe_val(get_row(pl_data, "ventas netas"),  recent_col) if recent_col else None
        ebitda_r  = safe_val(get_row(pl_data, "resultado operativo"), recent_col) if recent_col else None
        neto_r    = safe_val(get_row(pl_data, "resultado neto"), recent_col) if recent_col else None
        cogs_r    = safe_val(get_row(pl_data, "total cogs"),    recent_col) if recent_col else None
        gm_r      = safe_val(get_row(pl_data, "margen bruto"),  recent_col) if recent_col else None

        beer_total = sum(v for v in st.session_state.beer_costs.values() if v > 0)
        splits_summary = ", ".join([f"{k}: {v}%" for k,v in st.session_state.cat_splits.items()])

        if st.button("🤖 Generar Informe AI"):
            with st.spinner("Generando análisis..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    msg = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=1500,
                        messages=[{"role": "user", "content":
                            f"Eres el CFO advisor de Unseen Creatures Brewing & Blending, "
                            f"un taproom en los Estados Unidos. Analiza estos datos financieros "
                            f"y dame recomendaciones claras y accionables en español.\n\n"
                            f"DATOS MES MÁS RECIENTE ({recent_col}):\n"
                            f"- Ventas Netas: {fmt_usd(ventas_r)}\n"
                            f"- Margen Bruto: {fmt_usd(gm_r)}\n"
                            f"- Total COGS: {fmt_usd(cogs_r)}\n"
                            f"- EBITDA: {fmt_usd(ebitda_r)}\n"
                            f"- Resultado Neto: {fmt_usd(neto_r)}\n\n"
                            f"ASIGNACIÓN DE COSTOS ACTUAL:\n{splits_summary}\n\n"
                            f"COSTO TOTAL CERVEZA INGRESADO: {fmt_usd(beer_total)}\n\n"
                            f"Dame un informe con:\n"
                            f"1. ESTADO ACTUAL — diagnóstico de 3 líneas\n"
                            f"2. TOP 3 OPORTUNIDADES — acciones concretas esta semana\n"
                            f"3. RIESGOS — 2 riesgos principales a vigilar\n"
                            f"4. UN NÚMERO A VIGILAR — el KPI más importante y por qué\n\n"
                            f"Sé específico con los números. Tono directo, sin relleno."
                        }]
                    )
                    st.session_state.ai_report = msg.content[0].text
                except Exception as e:
                    st.error(f"Error llamando a la API: {e}")

        if st.session_state.ai_report:
            st.divider()
            st.markdown(st.session_state.ai_report)
            st.divider()
            st.caption("Informe generado automáticamente. Revisa los números antes de tomar decisiones.")
            if st.button("🔄 Regenerar"):
                st.session_state.ai_report = None
                st.rerun()

# ── FOOTER ─────────────────────────────────────────────────────────────────
st.divider()
beer_active = sum(1 for v in st.session_state.beer_costs.values() if v > 0)
st.caption(
    f"Unseen Creatures Brewing & Blending · "
    f"modelo_unseen_v4.xlsx · "
    f"Costos cerveza activos: {beer_active} meses · "
    f"Splits personalizados: {sum(1 for k,v in st.session_state.cat_splits.items() if v != CAT_DEFAULTS.get(k,50))}"
)
