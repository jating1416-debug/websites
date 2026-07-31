import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from thefuzz import fuzz
from statsmodels.tsa.seasonal import seasonal_decompose
import time
import re
import warnings
warnings.filterwarnings('ignore')

# ---- Optional libraries ----
try:
    from sklearn.ensemble import (RandomForestRegressor, 
                                   RandomForestClassifier, 
                                   IsolationForest)
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (r2_score, mean_absolute_error, 
                                  mean_squared_error, accuracy_score, 
                                  confusion_matrix)
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

try:
    from fpdf import FPDF
    FPDF_OK = True
except ImportError:
    FPDF_OK = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MPL_OK = True
except ImportError:
    MPL_OK = False

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Smart Data Cleaner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin: 10px 0;
    }
    .issue-card-critical {
        background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
        border-radius: 10px;
        padding: 15px;
        color: white;
        margin: 8px 0;
        border-left: 5px solid #c92a2a;
    }
    .issue-card-warning {
        background: linear-gradient(135deg, #ffd93d, #f9ca24);
        border-radius: 10px;
        padding: 15px;
        color: #2c3e50;
        margin: 8px 0;
        border-left: 5px solid #f39c12;
    }
    .issue-card-success {
        background: linear-gradient(135deg, #6bcf7f, #4ecb71);
        border-radius: 10px;
        padding: 15px;
        color: white;
        margin: 8px 0;
        border-left: 5px solid #27ae60;
    }
    .step-active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
        padding: 12px 20px;
        color: white;
        font-weight: 600;
        margin: 5px 0;
    }
    .step-complete {
        background: #d4edda;
        border-radius: 10px;
        padding: 12px 20px;
        color: #155724;
        margin: 5px 0;
        border-left: 4px solid #28a745;
    }
    .step-pending {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 12px 20px;
        color: #6c757d;
        margin: 5px 0;
        opacity: 0.6;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .quality-score {
        font-size: 3rem;
        font-weight: bold;
        color: #667eea;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .pulse { animation: pulse 2s infinite; }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
MAX_ROWS = 150000
MAX_HISTORY = 15
ML_SAMPLE_CAP = 20000

# ============================================================
# SESSION STATE
# ============================================================
def init_state():
    defaults = {
        'current_df': None,
        'active_dataset': None,
        'history': [],
        'redo_stack': [],
        'pipeline_log': [],
        'user_mode': 'beginner',
        'workflow_step': 0,
        'completed_steps': [],
        'data_quality_score': 0,
        'initial_quality_score': 0,
        'issues_detected': [],
        'fuzzy_matches': None,
        'anomaly_result': None,
        'ml_summary': None,
        'ml_importance': None,
        'anomaly_summary': None,
        'pdf_report': None,
        'merged_df': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def calculate_quality_score(df):
    if df is None or df.empty:
        return 0
    score = 100
    missing_pct = (
        df.isnull().sum().sum() / 
        (df.shape[0] * df.shape[1])
    ) * 100
    score -= min(missing_pct, 30)
    dup_pct = (df.duplicated().sum() / df.shape[0]) * 100
    score -= min(dup_pct, 20)
    for col in df.select_dtypes(include=['object']).columns:
        try:
            pd.to_numeric(df[col].dropna().head(100))
            score -= 2
        except Exception:
            pass
    return max(0, min(100, score))


def detect_issues(df):
    issues = []
    if df is None or df.empty:
        return issues

    # Missing values
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            pct = (null_count / len(df)) * 100
            severity = 'critical' if pct > 50 else 'warning'
            issues.append({
                'severity': severity,
                'type': 'missing_values',
                'column': col,
                'detail': f'{pct:.1f}% missing ({null_count:,} rows)',
                'auto_fixable': True
            })

    # Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        pct = (dup_count / len(df)) * 100
        issues.append({
            'severity': 'warning' if pct < 10 else 'critical',
            'type': 'duplicates',
            'column': 'All columns',
            'detail': f'{dup_count:,} duplicate rows ({pct:.1f}%)',
            'auto_fixable': True
        })

    # Data type mismatches
    for col in df.select_dtypes(include=['object']).columns:
        sample = df[col].dropna().head(100)
        if len(sample) > 0:
            try:
                pd.to_numeric(sample)
                issues.append({
                    'severity': 'warning',
                    'type': 'datatype',
                    'column': col,
                    'detail': 'Stored as text but looks like numbers',
                    'auto_fixable': True
                })
            except Exception:
                pass
            if any(k in col.lower() for k in 
                   ['date', 'time', 'dt', 'timestamp']):
                try:
                    pd.to_datetime(sample.head(10))
                    issues.append({
                        'severity': 'warning',
                        'type': 'datatype',
                        'column': col,
                        'detail': 'Stored as text but looks like dates',
                        'auto_fixable': True
                    })
                except Exception:
                    pass

    # Outliers
    for col in df.select_dtypes(include=[np.number]).columns:
        try:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            n_out = df[
                (df[col] < q1 - 1.5 * iqr) | 
                (df[col] > q3 + 1.5 * iqr)
            ][col].count()
            if n_out > 0:
                pct = (n_out / len(df)) * 100
                if pct > 5:
                    issues.append({
                        'severity': 'info',
                        'type': 'outliers',
                        'column': col,
                        'detail': f'{n_out:,} outliers ({pct:.1f}%)',
                        'auto_fixable': False
                    })
        except Exception:
            pass

    return issues


def auto_fix_issues(df, issues):
    fixed_df = df.copy()
    actions = []
    for issue in issues:
        if not issue.get('auto_fixable'):
            continue
        try:
            col = issue['column']
            if issue['type'] == 'missing_values':
                if pd.api.types.is_numeric_dtype(fixed_df[col]):
                    med = fixed_df[col].median()
                    fixed_df[col] = fixed_df[col].fillna(med)
                    actions.append(f"Filled '{col}' with median ({med:.2f})")
                else:
                    mode = fixed_df[col].mode()
                    fill_val = mode[0] if not mode.empty else ""
                    fixed_df[col] = fixed_df[col].fillna(fill_val)
                    actions.append(f"Filled '{col}' with mode ('{fill_val}')")
            elif issue['type'] == 'duplicates':
                before = len(fixed_df)
                fixed_df = fixed_df.drop_duplicates()
                actions.append(
                    f"Removed {before - len(fixed_df):,} duplicates"
                )
            elif issue['type'] == 'datatype':
                if 'numbers' in issue['detail']:
                    fixed_df[col] = pd.to_numeric(
                        fixed_df[col], errors='coerce'
                    )
                    actions.append(f"Converted '{col}' to numeric")
                elif 'dates' in issue['detail']:
                    fixed_df[col] = pd.to_datetime(
                        fixed_df[col], errors='coerce'
                    )
                    actions.append(f"Converted '{col}' to datetime")
        except Exception as e:
            st.warning(f"Could not fix '{issue['column']}': {e}")
    return fixed_df, actions


def log_entry(action, detail, shape):
    return {
        'Step': len(st.session_state.pipeline_log) + 1,
        'Action': action,
        'Detail': detail,
        'Time': datetime.now().strftime('%H:%M:%S'),
        'Shape': f"{shape[0]:,} × {shape[1]}"
    }


def apply_change(new_df, action, detail=""):
    st.session_state.history.append((
        st.session_state.current_df.copy(),
        list(st.session_state.pipeline_log)
    ))
    if len(st.session_state.history) > MAX_HISTORY:
        st.session_state.history.pop(0)
    st.session_state.redo_stack = []
    st.session_state.current_df = new_df
    st.session_state.pipeline_log.append(
        log_entry(action, detail, new_df.shape)
    )
    st.session_state.data_quality_score = calculate_quality_score(new_df)


def do_undo():
    if st.session_state.history:
        st.session_state.redo_stack.append((
            st.session_state.current_df.copy(),
            list(st.session_state.pipeline_log)
        ))
        df_prev, log_prev = st.session_state.history.pop()
        st.session_state.current_df = df_prev
        st.session_state.pipeline_log = log_prev
        st.session_state.data_quality_score = calculate_quality_score(df_prev)


def do_redo():
    if st.session_state.redo_stack:
        st.session_state.history.append((
            st.session_state.current_df.copy(),
            list(st.session_state.pipeline_log)
        ))
        df_next, log_next = st.session_state.redo_stack.pop()
        st.session_state.current_df = df_next
        st.session_state.pipeline_log = log_next
        st.session_state.data_quality_score = calculate_quality_score(df_next)


# ============================================================
# CACHED FUNCTIONS
# ============================================================
@st.cache_data(ttl=1800, max_entries=6, show_spinner="Reading file...")
def parse_file(file_bytes: bytes, file_name: str):
    bio = BytesIO(file_bytes)
    try:
        if file_name.endswith('.csv'):
            return pd.read_csv(bio)
        elif file_name.endswith('.xlsx'):
            return pd.read_excel(bio)
        elif file_name.endswith('.json'):
            return pd.read_json(bio)
    except Exception as e:
        st.error(f"Parse error: {e}")
    return None


@st.cache_data(ttl=600, max_entries=10, show_spinner=False)
def cached_describe(df: pd.DataFrame):
    return df.describe(include='all').fillna('-')


@st.cache_data(ttl=600, max_entries=10, show_spinner=False)
def cached_corr(df_num: pd.DataFrame):
    return df_num.corr()


# ============================================================
# WORKFLOW STEPS
# ============================================================
STEPS = [
    {'id': 0, 'name': 'Upload',    'icon': '📁'},
    {'id': 1, 'name': 'Quality',   'icon': '🔍'},
    {'id': 2, 'name': 'Clean',     'icon': '🧹'},
    {'id': 3, 'name': 'Analyze',   'icon': '📊'},
    {'id': 4, 'name': 'Download',  'icon': '💾'},
]

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);
            padding:25px;border-radius:15px;
            margin-bottom:20px;color:white;'>
    <h1 style='margin:0;font-size:2.2rem;'>🧹 Smart Data Cleaner</h1>
    <p style='margin:5px 0 0 0;opacity:0.9;'>
        AI-Powered Data Cleaning & Analysis
    </p>
</div>
""", unsafe_allow_html=True)

# Mode selector
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
with col_m2:
    mode = st.radio(
        "Experience Level:",
        ["Beginner (Guided)", "Intermediate", "Expert (Full Control)"],
        horizontal=True, key='mode_sel'
    )
    if "Beginner" in mode:
        st.session_state.user_mode = 'beginner'
    elif "Intermediate" in mode:
        st.session_state.user_mode = 'intermediate'
    else:
        st.session_state.user_mode = 'expert'

st.markdown("---")

# ============================================================
# PROGRESS TRACKER
# ============================================================
if st.session_state.user_mode in ['beginner', 'intermediate']:
    done = st.session_state.completed_steps
    curr = st.session_state.workflow_step
    pct  = (len(done) / len(STEPS)) * 100

    st.markdown("### Your Progress")
    st.progress(pct / 100)
    st.caption(f"{pct:.0f}% complete")

    cols = st.columns(len(STEPS))
    for idx, step in enumerate(STEPS):
        with cols[idx]:
            if idx in done:
                st.markdown(f"""
                <div class='step-complete'>
                ✅<br><small>{step['name']}</small>
                </div>""", unsafe_allow_html=True)
            elif idx == curr:
                st.markdown(f"""
                <div class='step-active pulse'>
                {step['icon']}<br><small><b>{step['name']}</b></small>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='step-pending'>
                {step['icon']}<br><small>{step['name']}</small>
                </div>""", unsafe_allow_html=True)
    st.markdown("---")

# ============================================================
# FILE UPLOAD
# ============================================================
st.markdown("### 📁 Upload Your Data")
if st.session_state.user_mode == 'beginner':
    st.info("👋 Start by uploading a CSV or Excel file. "
            "Your data stays 100% private.")

uc1, uc2, uc3 = st.columns(3)
with uc1:
    file1 = st.file_uploader("File 1 (Required)",
                              type=['csv','xlsx','json'], key="f1")
with uc2:
    file2 = st.file_uploader("File 2 (Optional)",
                              type=['csv','xlsx','json'], key="f2")
with uc3:
    file3 = st.file_uploader("File 3 (Optional)",
                              type=['csv','xlsx','json'], key="f3")


def load_file(f):
    try:
        df = parse_file(f.getvalue(), f.name)
        if df is None:
            return None
        if df.shape[0] > MAX_ROWS:
            st.error(f"{f.name}: {df.shape[0]:,} rows exceeds limit of "
                     f"{MAX_ROWS:,}")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading {f.name}: {e}")
        return None


dataframes = {}
for f in [file1, file2, file3]:
    if f:
        loaded = load_file(f)
        if loaded is not None:
            dataframes[f.name] = loaded
            st.success(f"✅ {f.name}: "
                       f"{loaded.shape[0]:,} rows × {loaded.shape[1]} cols")

if dataframes and 0 not in st.session_state.completed_steps:
    st.session_state.completed_steps.append(0)
    st.session_state.workflow_step = 1

st.markdown("---")

# ============================================================
# JOIN / MERGE (FIXED - PREVIEW ADDED)
# ============================================================
if len(dataframes) >= 2:
    st.markdown("### 🔗 Join Files (Optional)")
    if st.session_state.user_mode == 'beginner':
        st.info("💡 Combine two files on a common column "
                "(like VLOOKUP in Excel)")

    fnames = list(dataframes.keys())
    jc1, jc2 = st.columns(2)
    with jc1:
        sel_f1 = st.selectbox("First File:", fnames, key="jf1")
    with jc2:
        sel_f2 = st.selectbox("Second File:",
                               [f for f in fnames if f != sel_f1], key="jf2")

    jc3, jc4 = st.columns(2)
    with jc3:
        jcol1 = st.selectbox(f"Join Column ({sel_f1}):",
                              dataframes[sel_f1].columns.tolist(), key="jc1")
    with jc4:
        jcol2 = st.selectbox(f"Join Column ({sel_f2}):",
                              dataframes[sel_f2].columns.tolist(), key="jc2")

    jtype = st.radio(
        "Join Type:",
        ["Inner", "Left", "Right", "Outer"],
        horizontal=True, key="jtype",
        help="Inner=matching only | Left=all from file1 | "
             "Right=all from file2 | Outer=everything"
    )
    jmap = {"Inner": "inner", "Left": "left",
            "Right": "right", "Outer": "outer"}

    if st.button("🔗 Perform Join", key="join_btn", type="primary"):
        try:
            with st.spinner("Joining files..."):
                merged = pd.merge(
                    dataframes[sel_f1], dataframes[sel_f2],
                    left_on=jcol1, right_on=jcol2,
                    how=jmap[jtype]
                )
                st.session_state['merged_df'] = merged

            st.success(
                f"✅ Joined! {merged.shape[0]:,} rows × "
                f"{merged.shape[1]} columns"
            )

            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("File 1 Rows",
                          f"{dataframes[sel_f1].shape[0]:,}")
            with m2:
                st.metric("File 2 Rows",
                          f"{dataframes[sel_f2].shape[0]:,}")
            with m3:
                st.metric("Merged Rows", f"{merged.shape[0]:,}")
            with m4:
                base = max(dataframes[sel_f1].shape[0],
                           dataframes[sel_f2].shape[0])
                st.metric("Match Rate",
                          f"{merged.shape[0]/base*100:.1f}%")

            # ✅ PREVIEW - ALWAYS SHOWN
            st.markdown("#### 👁️ Merged Data Preview")
            st.dataframe(merged.head(50))

            with st.expander("🔍 Side-by-Side Source Preview"):
                pc1, pc2 = st.columns(2)
                with pc1:
                    st.markdown(f"**{sel_f1}**")
                    st.dataframe(dataframes[sel_f1].head(10))
                with pc2:
                    st.markdown(f"**{sel_f2}**")
                    st.dataframe(dataframes[sel_f2].head(10))

            with st.expander("📋 Column Details"):
                col_info = pd.DataFrame({
                    'Column': merged.columns,
                    'Type': merged.dtypes.astype(str).values,
                    'Non-Null': merged.count().values,
                    'Nulls': merged.isnull().sum().values,
                })
                st.dataframe(col_info)

        except Exception as e:
            st.error(f"❌ Join failed: {e}")
            st.warning("**Tips:** Check column types match, "
                       "no extra spaces in values")

    st.markdown("---")

# ============================================================
# DATASET SELECTOR
# ============================================================
if dataframes:
    st.markdown("### 📊 Select Dataset")
    options = list(dataframes.keys())
    if st.session_state.get('merged_df') is not None:
        options.append("🔗 Merged Data")

    selected = st.selectbox("Choose:", options, key="ds_select")

    if (st.session_state.active_dataset != selected or
            st.session_state.current_df is None):
        if selected == "🔗 Merged Data":
            base_df = st.session_state['merged_df'].copy()
        else:
            base_df = dataframes[selected].copy()

        st.session_state.active_dataset = selected
        st.session_state.current_df = base_df
        st.session_state.history = []
        st.session_state.redo_stack = []
        st.session_state.pipeline_log = [
            log_entry("Load", f"Loaded '{selected}'", base_df.shape)
        ]
        st.session_state.initial_quality_score = \
            calculate_quality_score(base_df)
        st.session_state.data_quality_score = \
            st.session_state.initial_quality_score
        st.session_state.issues_detected = detect_issues(base_df)

    df = st.session_state.current_df
    st.markdown("---")

    # ============================================================
    # QUALITY DASHBOARD
    # ============================================================
    st.markdown("## 🔍 Data Quality Dashboard")

    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        st.markdown(f"""
        <div class='metric-card'>
        <div style='font-size:.85rem;color:#6c757d;'>Quality Score</div>
        <div class='quality-score'>
            {st.session_state.data_quality_score:.0f}/100
        </div>
        </div>""", unsafe_allow_html=True)
    with qc2:
        imp = (st.session_state.data_quality_score -
               st.session_state.initial_quality_score)
        st.metric("Improvement",
                  f"+{imp:.0f}" if imp > 0 else f"{imp:.0f}")
    with qc3:
        crit = len([i for i in st.session_state.issues_detected
                    if i['severity'] == 'critical'])
        st.metric("Critical Issues", crit)
    with qc4:
        st.metric("Total Rows", f"{df.shape[0]:,}")

    # Issues
    issues = st.session_state.issues_detected
    if issues:
        st.markdown("### 🚨 Detected Issues")
        critical = [i for i in issues if i['severity'] == 'critical']
        warnings = [i for i in issues if i['severity'] == 'warning']

        if critical:
            st.markdown("#### 🔴 Critical")
            for i in critical:
                st.markdown(f"""
                <div class='issue-card-critical'>
                <b>{i['column']}</b> — {i['detail']}
                </div>""", unsafe_allow_html=True)

        if warnings:
            st.markdown("#### 🟡 Warnings")
            for i in warnings:
                st.markdown(f"""
                <div class='issue-card-warning'>
                <b>{i['column']}</b> — {i['detail']}
                </div>""", unsafe_allow_html=True)

        fixable = [i for i in issues if i.get('auto_fixable')]
        if fixable:
            st.markdown("<br>", unsafe_allow_html=True)
            fc1, fc2 = st.columns([3, 1])
            with fc1:
                st.info(f"💡 {len(fixable)} issues can be auto-fixed")
            with fc2:
                if st.button("🧹 Auto-Fix All",
                             type="primary", key="auto_fix"):
                    with st.spinner("Fixing..."):
                        fixed_df, actions = auto_fix_issues(df, fixable)
                        apply_change(fixed_df, "Auto-Fix",
                                     f"Fixed {len(actions)} issues")
                        st.session_state.issues_detected = \
                            detect_issues(fixed_df)
                        if 2 not in st.session_state.completed_steps:
                            st.session_state.completed_steps.append(2)
                    st.success(f"✅ Fixed {len(actions)} issues!")
                    for a in actions:
                        st.write(f"• {a}")
                    st.rerun()
    else:
        st.markdown("""
        <div class='issue-card-success'>
        ✅ <b>Great!</b> No major issues detected.
        </div>""", unsafe_allow_html=True)
        for s in [1, 2]:
            if s not in st.session_state.completed_steps:
                st.session_state.completed_steps.append(s)
        st.session_state.workflow_step = 3

    st.markdown("---")

    # ============================================================
    # UNDO / REDO
    # ============================================================
    st.markdown("### 🧾 History & Controls")
    ur1, ur2, ur3, ur4 = st.columns([1, 1, 1, 3])
    with ur1:
        if st.button(
            f"↩️ Undo ({len(st.session_state.history)})",
            disabled=not st.session_state.history,
            key="undo"
        ):
            do_undo(); st.rerun()
    with ur2:
        if st.button(
            f"↪️ Redo ({len(st.session_state.redo_stack)})",
            disabled=not st.session_state.redo_stack,
            key="redo"
        ):
            do_redo(); st.rerun()
    with ur3:
        if st.button("🔄 Reset", key="reset"):
            st.session_state.active_dataset = None
            st.rerun()
    with ur4:
        st.caption(
            f"{len(st.session_state.pipeline_log)} steps | "
            f"Score: {st.session_state.data_quality_score:.0f}/100"
        )

    with st.expander(
        f"📜 Pipeline Log ({len(st.session_state.pipeline_log)} steps)"
    ):
        if st.session_state.pipeline_log:
            log_df = pd.DataFrame(st.session_state.pipeline_log)
            st.dataframe(log_df, hide_index=True)
            st.download_button(
                "📥 Download Log",
                log_df.to_csv(index=False).encode(),
                file_name="pipeline_log.csv",
                mime="text/csv"
            )

    st.markdown("---")

    # ============================================================
    # BASIC OVERVIEW
    # ============================================================
    with st.expander("📊 Data Overview",
                     expanded=(st.session_state.user_mode == 'expert')):
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric("Rows", f"{df.shape[0]:,}")
        with mc2: st.metric("Columns", df.shape[1])
        with mc3:
            mem = df.memory_usage(deep=True).sum() / 1024**2
            st.metric("Memory", f"{mem:.2f} MB")
        with mc4: st.metric("Dtypes", df.dtypes.nunique())

        ot1, ot2, ot3 = st.tabs(["Head", "Sample", "Info"])
        with ot1:
            st.dataframe(df.head(10))
        with ot2:
            st.dataframe(df.sample(min(5, len(df))))
        with ot3:
            st.dataframe(pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str).values,
                'Non-Null': df.count().values,
                'Null %': (
                    df.isnull().mean() * 100
                ).round(1).values
            }))

    # ============================================================
    # CLEANING TOOLBOX
    # ============================================================
    st.markdown("## 🧰 Data Cleaning Tools")

    tb1, tb2, tb3, tb4 = st.tabs([
        "🕳️ Missing Values",
        "✂️ Columns",
        "🔤 Text",
        "🔎 Find & Replace"
    ])

    # -- MISSING VALUES --
    with tb1:
        miss_cols = df.columns[df.isnull().any()].tolist()
        if not miss_cols:
            st.success("✅ No missing values!")
        else:
            mv1, mv2, mv3 = st.columns(3)
            with mv1:
                mv_col = st.selectbox("Column:", miss_cols, key="mv_col")
            with mv2:
                mv_action = st.selectbox("Action:", [
                    "Drop Rows", "Fill Mean", "Fill Median",
                    "Fill Mode", "Fill Custom", "Forward Fill",
                    "Backward Fill", "Interpolate"
                ], key="mv_action")

            custom_val = None
            ok = True
            with mv3:
                if mv_action == "Fill Custom":
                    custom_val = st.text_input("Value:", key="mv_custom")
                    if not custom_val:
                        st.warning("Enter a value"); ok = False
                    elif pd.api.types.is_numeric_dtype(df[mv_col]):
                        try:
                            float(custom_val)
                        except Exception:
                            st.error("Must be a number"); ok = False
                apply_mv = st.button("✅ Apply",
                                     key="mv_apply", disabled=not ok)

            if apply_mv:
                try:
                    ndf = df.copy()
                    if mv_action == "Drop Rows":
                        ndf = ndf.dropna(subset=[mv_col])
                    elif mv_action == "Fill Mean":
                        ndf[mv_col] = ndf[mv_col].fillna(
                            ndf[mv_col].mean()
                        )
                    elif mv_action == "Fill Median":
                        ndf[mv_col] = ndf[mv_col].fillna(
                            ndf[mv_col].median()
                        )
                    elif mv_action == "Fill Mode":
                        m = ndf[mv_col].mode()
                        ndf[mv_col] = ndf[mv_col].fillna(
                            m[0] if not m.empty else ""
                        )
                    elif mv_action == "Fill Custom":
                        v = (float(custom_val)
                             if pd.api.types.is_numeric_dtype(df[mv_col])
                             else custom_val)
                        ndf[mv_col] = ndf[mv_col].fillna(v)
                    elif mv_action == "Forward Fill":
                        ndf[mv_col] = ndf[mv_col].ffill()
                    elif mv_action == "Backward Fill":
                        ndf[mv_col] = ndf[mv_col].bfill()
                    elif mv_action == "Interpolate":
                        ndf[mv_col] = ndf[mv_col].interpolate()

                    apply_change(ndf, "Missing Values",
                                 f"'{mv_col}' → {mv_action}")
                    st.success(
                        f"✅ Done! Remaining nulls: "
                        f"{ndf[mv_col].isnull().sum()}"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    # -- COLUMNS --
    with tb2:
        rc1, rc2, rc3 = st.columns([2, 2, 1])
        with rc1:
            col_r = st.selectbox("Column:", df.columns.tolist(),
                                 key="ren_col")
        with rc2:
            new_n = st.text_input("New Name:", value=col_r,
                                  key="ren_val")
        with rc3:
            st.write("")
            if st.button("✏️ Rename", key="ren_btn"):
                if new_n and new_n != col_r:
                    ndf = df.rename(columns={col_r: new_n})
                    apply_change(ndf, "Rename", f"'{col_r}'→'{new_n}'")
                    st.success("✅ Renamed!"); st.rerun()

        st.markdown("---")
        drop_c = st.multiselect("Drop Columns:",
                                df.columns.tolist(), key="drop_ms")
        if st.button("🗑️ Drop", key="drop_btn"):
            if drop_c:
                ndf = df.drop(columns=drop_c)
                apply_change(ndf, "Drop Cols",
                             f"Dropped: {', '.join(drop_c)}")
                st.success("✅ Dropped!"); st.rerun()

    # -- TEXT --
    with tb3:
        t_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not t_cols:
            st.info("No text columns found")
        else:
            tc1, tc2 = st.columns(2)
            with tc1:
                tc_col = st.selectbox("Column:", t_cols, key="tc_col")
            with tc2:
                tc_act = st.selectbox("Action:", [
                    "Trim Whitespace", "Lowercase", "UPPERCASE",
                    "Title Case", "Remove Special Chars",
                    "Remove Extra Spaces"
                ], key="tc_act")
            if st.button("🧹 Apply", key="tc_btn"):
                try:
                    ndf = df.copy()
                    s = ndf[tc_col].astype(str)
                    if tc_act == "Trim Whitespace":
                        s = s.str.strip()
                    elif tc_act == "Lowercase":
                        s = s.str.lower()
                    elif tc_act == "UPPERCASE":
                        s = s.str.upper()
                    elif tc_act == "Title Case":
                        s = s.str.title()
                    elif tc_act == "Remove Special Chars":
                        s = s.str.replace(r'[^A-Za-z0-9\s]', '',
                                          regex=True)
                    elif tc_act == "Remove Extra Spaces":
                        s = s.str.replace(r'\s+', ' ',
                                          regex=True).str.strip()
                    ndf[tc_col] = s
                    apply_change(ndf, "Text Clean",
                                 f"'{tc_col}'→{tc_act}")
                    st.success("✅ Done!"); st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    # -- FIND & REPLACE --
    with tb4:
        fr_col = st.selectbox("Column:", df.columns.tolist(),
                              key="fr_col")
        fr1, fr2 = st.columns(2)
        with fr1:
            find_v = st.text_input("Find:", key="fr_find")
        with fr2:
            repl_v = st.text_input("Replace:", key="fr_repl")
        use_rx = st.checkbox("Use Regex", key="fr_rx")
        if st.button("🔎 Apply", key="fr_btn"):
            if not find_v:
                st.warning("Enter a search value")
            else:
                try:
                    ndf = df.copy()
                    ndf[fr_col] = ndf[fr_col].astype(str).str.replace(
                        find_v, repl_v, regex=use_rx
                    )
                    apply_change(ndf, "Find&Replace",
                                 f"'{find_v}'→'{repl_v}' in '{fr_col}'")
                    st.success("✅ Done!"); st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    st.markdown("---")

    # ============================================================
    # OUTLIER + FUZZY
    # ============================================================
    st.markdown("## 🎯 Advanced Detection")
    ob1, ob2 = st.tabs(["📏 Outliers", "🧩 Fuzzy Duplicates"])

    with ob1:
        num_c = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_c:
            st.info("No numeric columns")
        else:
            oc1, oc2, oc3 = st.columns(3)
            with oc1:
                out_col = st.selectbox("Column:", num_c, key="out_col")
            with oc2:
                out_m = st.selectbox("Method:", ["IQR","Z-Score"],
                                     key="out_m")
            with oc3:
                if out_m == "IQR":
                    iq_m = st.slider("Multiplier:", 1.0, 3.0, 1.5,
                                     0.1, key="iqr_m")
                else:
                    z_t = st.slider("Threshold:", 1.0, 5.0, 3.0,
                                    0.1, key="z_t")

            cd = df[out_col].dropna()
            if out_m == "IQR":
                q1 = cd.quantile(0.25); q3 = cd.quantile(0.75)
                iqr = q3 - q1
                lo = q1 - iq_m * iqr; hi = q3 + iq_m * iqr
                mask = (df[out_col] < lo) | (df[out_col] > hi)
            else:
                mn = cd.mean(); sd = cd.std()
                zs = (df[out_col] - mn) / sd if sd != 0 else df[out_col]*0
                mask = zs.abs() > z_t

            mask = mask.fillna(False)
            n_out = int(mask.sum())
            st.metric("Outliers Found", n_out)

            fig = px.box(df, y=out_col, points='outliers',
                         title=f'Box Plot: {out_col}')
            st.plotly_chart(fig, use_container_width=True)

            if n_out > 0:
                if st.checkbox("Show Outlier Rows", key="sh_out"):
                    st.dataframe(df[mask])
                a1, a2 = st.columns(2)
                with a1:
                    if st.button("🗑️ Remove", key="rm_out"):
                        ndf = df[~mask].copy()
                        apply_change(ndf, "Remove Outliers",
                                     f"{n_out} removed from '{out_col}'")
                        st.success("✅ Removed!"); st.rerun()
                with a2:
                    if st.button("📌 Cap", key="cap_out"):
                        ndf = df.copy()
                        if out_m == "IQR":
                            ndf[out_col] = ndf[out_col].clip(lo, hi)
                        else:
                            ndf[out_col] = ndf[out_col].clip(
                                mn - z_t*sd, mn + z_t*sd
                            )
                        apply_change(ndf, "Cap Outliers",
                                     f"'{out_col}' capped")
                        st.success("✅ Capped!"); st.rerun()
            else:
                st.success("✅ No outliers!")

    with ob2:
        st.info("Finds similar-but-not-identical text values")
        fz_cols = df.select_dtypes(
            include=['object']
        ).columns.tolist()

        if not fz_cols:
            st.info("No text columns")
        else:
            fz1, fz2 = st.columns(2)
            with fz1:
                fz_col = st.selectbox("Column:", fz_cols, key="fz_col")
            with fz2:
                fz_thr = st.slider("Similarity %:", 70, 99, 90,
                                   key="fz_thr")

            if st.button("🔍 Find Fuzzy Duplicates", key="fz_btn"):
                sdf = df[[fz_col]].dropna().reset_index().head(2000)
                vals = sdf[fz_col].astype(str).tolist()
                idxs = sdf['index'].tolist()
                total = len(vals)

                pb = st.progress(0)
                st_txt = st.empty()
                matches = []; seen = set()

                for i in range(total):
                    if i % 20 == 0:
                        pb.progress(min(i/total, 1.0))
                        st_txt.text(f"Comparing {i}/{total}...")
                    if i in seen:
                        continue
                    grp = [i]
                    for j in range(i+1, total):
                        if j in seen:
                            continue
                        if fuzz.ratio(vals[i], vals[j]) >= fz_thr:
                            grp.append(j); seen.add(j)
                    if len(grp) > 1:
                        seen.add(i)
                        for g in grp:
                            matches.append({
                                'Group': len(matches)//max(len(grp),1)+1,
                                'Row Index': idxs[g],
                                'Value': vals[g]
                            })

                pb.empty(); st_txt.empty()
                st.session_state['fuzzy_matches'] = (
                    pd.DataFrame(matches) if matches else None
                )
                st.rerun()

            # ✅ PERSISTENT RESULTS
            fm = st.session_state.get('fuzzy_matches')
            if fm is not None:
                fm1, fm2, fm3 = st.columns(3)
                with fm1: st.metric("Groups", fm['Group'].nunique())
                with fm2: st.metric("Rows", fm['Row Index'].nunique())
                with fm3:
                    avg = fm.groupby('Group').size().mean()
                    st.metric("Avg Size", f"{avg:.1f}")
                st.dataframe(fm)
                st.download_button(
                    "📥 Download",
                    fm.to_csv(index=False).encode(),
                    file_name="fuzzy_matches.csv",
                    mime="text/csv"
                )
                if st.button("Clear", key="clr_fz"):
                    st.session_state['fuzzy_matches'] = None
                    st.rerun()
            elif st.session_state.get('fuzzy_matches') is not None:
                st.success("✅ No fuzzy duplicates found!")

    st.markdown("---")

    # ============================================================
    # ML + ANOMALY
    # ============================================================
    st.markdown("## 🤖 AI-Powered Analysis")

    if not SKLEARN_OK:
        st.warning("Install scikit-learn: `pip install scikit-learn`")
    else:
        ml1, ml2 = st.tabs(["🎯 Quick Predict", "🚨 Anomaly Detection"])

        with ml1:
            num_cols_ml = df.select_dtypes(
                include=[np.number]
            ).columns.tolist()
            if len(df.columns) < 2:
                st.info("Need 2+ columns")
            else:
                mp1, mp2 = st.columns(2)
                with mp1:
                    tgt = st.selectbox("Target:", df.columns.tolist(),
                                       key="ml_tgt")
                with mp2:
                    feats = st.multiselect(
                        "Features:",
                        [c for c in df.columns if c != tgt],
                        default=[c for c in num_cols_ml
                                 if c != tgt][:5],
                        key="ml_feats"
                    )

                ts = df[tgt].dropna()
                is_num = pd.api.types.is_numeric_dtype(ts)
                prob = ("Regression" if is_num and ts.nunique() > 15
                        else "Classification")
                st.caption(f"Detected: **{prob}**")

                if st.button("🚀 Train", key="ml_tr"):
                    if not feats:
                        st.warning("Select features")
                    else:
                        try:
                            with st.spinner("Training..."):
                                mdf = df[feats+[tgt]].dropna()
                                if len(mdf) > ML_SAMPLE_CAP:
                                    mdf = mdf.sample(ML_SAMPLE_CAP,
                                                     random_state=42)
                                if len(mdf) < 30:
                                    st.error("Need 30+ rows"); st.stop()

                                X = pd.get_dummies(mdf[feats],
                                                   drop_first=True)
                                if X.shape[1] > 200:
                                    X = X.iloc[:, :200]
                                y = mdf[tgt]
                                is_r = prob == "Regression"
                                if not is_r:
                                    y = y.astype(str)

                                Xtr,Xte,ytr,yte = train_test_split(
                                    X,y,test_size=0.2,random_state=42
                                )
                                mdl = (
                                    RandomForestRegressor(
                                        n_estimators=60,
                                        random_state=42,n_jobs=-1)
                                    if is_r else
                                    RandomForestClassifier(
                                        n_estimators=60,
                                        random_state=42,n_jobs=-1)
                                )
                                mdl.fit(Xtr, ytr)
                                preds = mdl.predict(Xte)

                                r1,r2,r3 = st.columns(3)
                                if is_r:
                                    rv = r2_score(yte, preds)
                                    mae = mean_absolute_error(yte, preds)
                                    rmse = float(np.sqrt(
                                        mean_squared_error(yte, preds)
                                    ))
                                    with r1: st.metric("R²",f"{rv:.3f}")
                                    with r2: st.metric("MAE",f"{mae:.2f}")
                                    with r3: st.metric("RMSE",f"{rmse:.2f}")
                                    st.session_state['ml_summary'] = (
                                        f"R²={rv:.3f},MAE={mae:.2f}"
                                    )
                                    fig = px.scatter(
                                        x=yte, y=preds,
                                        labels={'x':'Actual','y':'Predicted'}
                                    )
                                    st.plotly_chart(fig,
                                                    use_container_width=True)
                                else:
                                    acc = accuracy_score(yte, preds)
                                    with r1:
                                        st.metric("Accuracy",
                                                  f"{acc*100:.1f}%")
                                    with r2: st.metric("Classes",y.nunique())
                                    with r3: st.metric("Test Rows",len(yte))
                                    st.session_state['ml_summary'] = (
                                        f"Acc={acc*100:.1f}%"
                                    )

                                imp = pd.DataFrame({
                                    'Feature': X.columns,
                                    'Importance': mdl.feature_importances_
                                }).sort_values('Importance',
                                               ascending=False).head(15)
                                fig = px.bar(
                                    imp, x='Importance', y='Feature',
                                    orientation='h',
                                    title='Feature Importance',
                                    color='Importance'
                                )
                                fig.update_layout(
                                    yaxis={'categoryorder':'total ascending'}
                                )
                                st.plotly_chart(fig,
                                                use_container_width=True)
                                st.session_state['ml_importance'] = imp

                                if 3 not in st.session_state.completed_steps:
                                    st.session_state.completed_steps.append(3)

                        except Exception as e:
                            st.error(f"❌ {e}")

        with ml2:
            an_nc = df.select_dtypes(
                include=[np.number]
            ).columns.tolist()
            if not an_nc:
                st.info("Need numeric columns")
            else:
                a1, a2 = st.columns(2)
                with a1:
                    an_cols = st.multiselect(
                        "Columns:", an_nc,
                        default=an_nc[:4], key="an_cols"
                    )
                with a2:
                    cont = st.slider("Anomaly %:", 1, 20, 5,
                                     key="cont") / 100

                if st.button("🚨 Detect", key="an_btn"):
                    if not an_cols:
                        st.warning("Select columns")
                    else:
                        try:
                            with st.spinner("Scanning..."):
                                ad = df[an_cols].dropna()
                                if len(ad) < 20:
                                    st.error("Need 20+ rows"); st.stop()
                                iso = IsolationForest(
                                    contamination=cont,
                                    random_state=42, n_jobs=-1
                                )
                                lbs = iso.fit_predict(ad)
                                st.session_state['anomaly_result'] = {
                                    'index': ad.index[lbs==-1].tolist(),
                                    'cols': an_cols,
                                    'data_index': ad.index.tolist(),
                                    'n_scanned': len(ad),
                                }
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")

                ar = st.session_state.get('anomaly_result')
                if ar:
                    aidx = [i for i in ar['index'] if i in df.index]
                    n_a = len(aidx)
                    am1,am2,am3 = st.columns(3)
                    with am1: st.metric("Anomalies", n_a)
                    with am2: st.metric("Scanned", ar['n_scanned'])
                    with am3:
                        st.metric("Rate",
                                  f"{n_a/max(ar['n_scanned'],1)*100:.1f}%")
                    st.session_state['anomaly_summary'] = (
                        f"{n_a} anomalies in {ar['n_scanned']} rows"
                    )

                    pc = [c for c in ar['cols'] if c in df.columns]
                    vi = [i for i in ar['data_index'] if i in df.index]
                    if len(pc) >= 2 and vi:
                        pdf = df.loc[vi, pc].copy()
                        pdf['Status'] = np.where(
                            pdf.index.isin(aidx),'Anomaly','Normal'
                        )
                        fig = px.scatter(
                            pdf, x=pc[0], y=pc[1], color='Status',
                            color_discrete_map={
                                'Anomaly':'red','Normal':'lightblue'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    if n_a > 0:
                        with st.expander(f"👀 View {n_a} Anomalies"):
                            st.dataframe(df.loc[aidx])
                        if st.button("🗑️ Remove", key="rm_an"):
                            ndf = df.drop(index=aidx)
                            apply_change(ndf, "Remove Anomalies",
                                         f"{n_a} rows removed")
                            st.session_state.pop('anomaly_result',None)
                            st.success("✅ Removed!"); st.rerun()

    st.markdown("---")

    # ============================================================
    # VISUALIZATIONS
    # ============================================================
    st.markdown("## 📈 Visualizations")

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(
        include=['datetime64']
    ).columns.tolist()

    v1,v2,v3,v4 = st.tabs([
        "📊 Numeric","🎨 Categorical","🔥 Correlation","📉 Trend"
    ])

    with v1:
        if num_cols:
            sn = st.selectbox("Column:", num_cols, key="nv")
            vc1,vc2 = st.columns(2)
            with vc1:
                fig = px.histogram(df, x=sn, nbins=30,
                                   title=f'Distribution: {sn}')
                st.plotly_chart(fig, use_container_width=True)
            with vc2:
                fig = px.box(df, y=sn, title=f'Box: {sn}')
                st.plotly_chart(fig, use_container_width=True)
            if len(num_cols) >= 2:
                sc1,sc2 = st.columns(2)
                with sc1:
                    xa = st.selectbox("X:", num_cols, key="sx")
                with sc2:
                    ya = st.selectbox(
                        "Y:", [c for c in num_cols if c!=xa], key="sy"
                    )
                fig = px.scatter(df, x=xa, y=ya,
                                 title=f'{xa} vs {ya}')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns")

    with v2:
        if cat_cols:
            sc = st.selectbox("Column:", cat_cols, key="cv")
            vc = df[sc].value_counts().head(15).reset_index()
            vc.columns = [sc,'Count']
            fig = px.bar(vc, x=sc, y='Count',
                         title=f'Top 15: {sc}', color='Count')
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.pie(vc.head(8), names=sc, values='Count',
                          title=f'Distribution: {sc}')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No categorical columns")

    with v3:
        if len(num_cols) >= 2:
            corr = cached_corr(df[num_cols])
            fig = px.imshow(corr, text_auto='.2f',
                            title='Correlation Heatmap',
                            color_continuous_scale='RdBu_r')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need 2+ numeric columns")

    with v4:
        if date_cols and num_cols:
            dc1,dc2 = st.columns(2)
            with dc1:
                xd = st.selectbox("Date:", date_cols, key="td_x")
            with dc2:
                yv = st.selectbox("Value:", num_cols, key="td_y")
            tdf = df.dropna(subset=[xd,yv]).sort_values(xd)
            fig = px.line(tdf, x=xd, y=yv,
                          title=f'{yv} Over Time')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need a date column and numeric column. "
                    "Convert date column type first.")

    st.markdown("---")

    # ============================================================
    # DOWNLOAD
    # ============================================================
    st.markdown("## 💾 Download Results")
    if st.session_state.user_mode == 'beginner':
        st.info("💡 Download before closing - nothing saved on servers!")

    final_df = st.session_state.current_df

    dl1,dl2,dl3 = st.columns(3)
    with dl1:
        st.download_button(
            "📥 Download CSV",
            final_df.to_csv(index=False).encode(),
            file_name=f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with dl2:
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            final_df.to_excel(w, index=False, sheet_name='Data')
        st.download_button(
            "📥 Download Excel",
            buf.getvalue(),
            file_name=f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with dl3:
        steps = "\n".join(
            f"{s['Step']}. {s['Action']} - {s['Detail']}"
            for s in st.session_state.pipeline_log
        )
        rpt = (f"DATA REPORT\n"
               f"Generated: {datetime.now()}\n"
               f"Score: {st.session_state.data_quality_score:.0f}/100\n"
               f"\nSTEPS:\n{steps}\n"
               f"\nFINAL: {final_df.shape[0]:,} rows × "
               f"{final_df.shape[1]} cols")
        st.download_button(
            "📄 Download Report",
            rpt,
            file_name="report.txt",
            mime="text/plain",
            use_container_width=True
        )

    # PDF
    if FPDF_OK:
        st.markdown("### 📑 PDF Report")

        def _safe(t):
            ep = re.compile(
                "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
                "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
                "\U00002702-\U000027B0\U000024C2-\U0001F251]+",
                flags=re.UNICODE
            )
            cleaned = ep.sub('', str(t))
            try:
                cleaned.encode('latin-1')
                return cleaned
            except Exception:
                return cleaned.encode('latin-1','replace').decode('latin-1')

        def build_pdf():
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_fill_color(102, 126, 234)
            pdf.rect(0, 0, 210, 40, 'F')
            pdf.set_font('Helvetica','B',20)
            pdf.set_text_color(255,255,255)
            pdf.set_y(14)
            pdf.cell(0,10,'DATA CLEANING REPORT',align='C')
            pdf.ln(20)
            pdf.set_text_color(0,0,0)
            pdf.set_font('Helvetica','',10)
            pdf.cell(
                0,8,
                _safe(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}"),
                align='C'
            )
            pdf.ln(14)
            pdf.set_font('Helvetica','B',13)
            pdf.cell(0,9,'Summary'); pdf.ln(9)
            pdf.set_font('Helvetica','',10)
            rows = [
                ("Initial Score",
                 f"{st.session_state.initial_quality_score:.0f}/100"),
                ("Final Score",
                 f"{st.session_state.data_quality_score:.0f}/100"),
                ("Total Rows", f"{final_df.shape[0]:,}"),
                ("Total Columns", str(final_df.shape[1])),
                ("Missing Values",
                 f"{final_df.isnull().sum().sum():,}"),
                ("Duplicate Rows",
                 f"{final_df.duplicated().sum():,}"),
            ]
            for lbl,val in rows:
                pdf.set_fill_color(243,244,246)
                pdf.cell(70,8,_safe(lbl),border=1,fill=True)
                pdf.cell(60,8,_safe(val),border=1); pdf.ln(8)
            pdf.ln(5)
            pdf.set_font('Helvetica','B',13)
            pdf.cell(0,9,'Cleaning Steps'); pdf.ln(9)
            pdf.set_font('Helvetica','',9)
            for s in st.session_state.pipeline_log:
                a = ''.join(c for c in s['Action'] if ord(c)<256).strip()
                pdf.multi_cell(
                    0,6,
                    _safe(f"Step {s['Step']} [{s['Time']}] {a}: "
                          f"{s['Detail']}")
                )
            return bytes(pdf.output())

        if st.button("📑 Generate PDF", type="primary", key="pdf_btn"):
            with st.spinner("Building PDF..."):
                st.session_state['pdf_report'] = build_pdf()
            st.success("✅ Ready!")

        if st.session_state.get('pdf_report'):
            st.download_button(
                "📥 Download PDF",
                st.session_state['pdf_report'],
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    if 4 not in st.session_state.completed_steps:
        st.session_state.completed_steps.append(4)

else:
    # Welcome Screen
    st.markdown("""
    <div class='feature-card'>
        <h2 style='margin:0;'>👋 Welcome!</h2>
        <p style='margin:8px 0 0 0;'>
            Upload a file above to start cleaning your data
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("**🔍 Auto-Detect**\n"
                    "- Missing values\n- Duplicates\n"
                    "- Type errors\n- Outliers")
    with c2:
        st.markdown("**🧹 Smart Clean**\n"
                    "- One-click fix\n- Undo/Redo\n"
                    "- Step guide\n- Fuzzy match")
    with c3:
        st.markdown("**📊 AI Analysis**\n"
                    "- ML predict\n- Anomaly detect\n"
                    "- Charts\n- PDF report")

    st.markdown("---")
    st.markdown("🔒 **Privacy:** Data never leaves your browser | "
                "Session-only | Close tab = data erased")

# Footer
st.markdown("---")
st.caption("🔒 100% Private | No Storage | © 2026")
