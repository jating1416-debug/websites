import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from thefuzz import fuzz
from statsmodels.tsa.seasonal import seasonal_decompose

# ---- Optional heavy libraries (all FREE, no API, no cost) ----
try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score, confusion_matrix
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
# 1. PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Clean & Visualize Data | Jatin Kumar",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. STYLING (Clean embed look - Streamlit branding minimal)
# ============================================================
st.markdown("""
<style>
    /* Hide Streamlit default branding for clean embed */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    .badge {
        display: inline-block;
        padding: 5px 12px;
        margin: 3px;
        background-color: #E3F2FD;
        color: #0D47A1;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.82rem;
    }

    .privacy-banner {
        background: linear-gradient(135deg, #f0fff4, #e6fffa);
        border: 1px solid #9ae6b4;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 15px;
    }

    .limit-banner {
        background: #fffaf0;
        border: 1px solid #fbd38d;
        border-radius: 8px;
        padding: 10px 15px;
        font-size: 0.9rem;
        color: #c05621;
        margin-bottom: 15px;
    }

    .pipeline-step {
        background: #f7fafc;
        border-left: 4px solid #667eea;
        border-radius: 6px;
        padding: 8px 14px;
        margin: 4px 0;
        font-size: 0.88rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. CONSTANTS
# ============================================================
MAX_ROWS = 150000
MAX_FILE_SIZE_MB = 50
MAX_HISTORY = 15          # Undo/Redo memory limit (snapshots)
ML_SAMPLE_CAP = 20000     # Max rows used for model training (speed)

# ============================================================
# 3.5 SESSION STATE + PIPELINE HELPERS (PART 5)
# ============================================================
def init_state():
    defaults = {
        'current_df': None,
        'active_dataset': None,
        'history': [],        # list of (df, pipeline_log_copy) snapshots
        'redo_stack': [],     # list of (df, pipeline_log_copy)
        'pipeline_log': [],   # list of dicts: step, action, detail, time, shape
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def log_entry(action, detail, shape):
    return {
        'Step': len(st.session_state.pipeline_log) + 1,
        'Action': action,
        'Detail': detail,
        'Time': datetime.now().strftime('%H:%M:%S'),
        'Shape': f"{shape[0]:,} × {shape[1]}"
    }


def apply_change(new_df, action, detail=""):
    """Central mutation function: saves snapshot for Undo, logs the step,
    updates the working dataframe. Everything stays in RAM only."""
    st.session_state.history.append(
        (st.session_state.current_df, list(st.session_state.pipeline_log))
    )
    if len(st.session_state.history) > MAX_HISTORY:
        st.session_state.history.pop(0)
    st.session_state.redo_stack = []  # new action clears redo
    st.session_state.current_df = new_df
    st.session_state.pipeline_log.append(log_entry(action, detail, new_df.shape))


def do_undo():
    if st.session_state.history:
        st.session_state.redo_stack.append(
            (st.session_state.current_df, list(st.session_state.pipeline_log))
        )
        df_prev, log_prev = st.session_state.history.pop()
        st.session_state.current_df = df_prev
        st.session_state.pipeline_log = log_prev


def do_redo():
    if st.session_state.redo_stack:
        st.session_state.history.append(
            (st.session_state.current_df, list(st.session_state.pipeline_log))
        )
        df_next, log_next = st.session_state.redo_stack.pop()
        st.session_state.current_df = df_next
        st.session_state.pipeline_log = log_next


# ============================================================
# 3.6 CACHED FILE PARSER (PART 5 - PERFORMANCE)
# ============================================================
@st.cache_data(ttl=900, max_entries=6, show_spinner="📂 Reading file...")
def parse_file(file_bytes: bytes, file_name: str):
    """Cached in RAM only (15 min TTL) - re-uploading the same file is instant.
    NEVER writes to disk."""
    bio = BytesIO(file_bytes)
    if file_name.endswith('.csv'):
        return pd.read_csv(bio)
    elif file_name.endswith('.xlsx'):
        return pd.read_excel(bio)
    elif file_name.endswith('.json'):
        return pd.read_json(bio)
    return None


@st.cache_data(ttl=600, max_entries=10, show_spinner=False)
def cached_describe(df: pd.DataFrame):
    return df.describe(include='all').fillna('-')


@st.cache_data(ttl=600, max_entries=10, show_spinner=False)
def cached_corr(df_num: pd.DataFrame):
    return df_num.corr()


# ============================================================
# 4. HEADER
# ============================================================
st.markdown("## 🧹 Clean & Visualize Your Data")

col_a, col_b = st.columns([3, 1])
with col_a:
    st.markdown("""
    <div class="privacy-banner">
    🔒 <b>100% Private:</b> Your data is NEVER stored or saved anywhere.
    Everything happens in your browser session only — close this tab and
    all data is permanently erased. Zero history, zero tracking.
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown(f"""
    <div class="limit-banner">
    ⚠️ <b>Max Limit:</b><br>{MAX_ROWS:,} rows per file
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# 5. FILE UPLOAD (Multi-file, session only)
# ============================================================
st.markdown("### 📁 Upload Your Files (Max 3)")

col1, col2, col3 = st.columns(3)
with col1:
    file1 = st.file_uploader("📄 File 1 (Required)", type=['csv', 'xlsx', 'json'], key="f1")
with col2:
    file2 = st.file_uploader("📄 File 2 (Optional)", type=['csv', 'xlsx', 'json'], key="f2")
with col3:
    file3 = st.file_uploader("📄 File 3 (Optional)", type=['csv', 'xlsx', 'json'], key="f3")


def load_file(file):
    """Load file into memory only - NEVER writes to disk (cached for speed)"""
    try:
        df = parse_file(file.getvalue(), file.name)
        if df is None:
            return None
        if df.shape[0] > MAX_ROWS:
            st.error(f"⚠️ **{file.name}** too large! Max {MAX_ROWS:,} rows allowed. "
                     f"Your file has {df.shape[0]:,} rows.")
            return None
        return df
    except Exception as e:
        st.error(f"❌ Error loading {file.name}: {e}")
        return None


dataframes = {}
for f in [file1, file2, file3]:
    if f:
        df = load_file(f)
        if df is not None:
            dataframes[f.name] = df
            st.success(f"✅ **{f.name}**: {df.shape[0]:,} rows × {df.shape[1]} columns")

st.markdown("---")

# ============================================================
# 6. JOIN / MERGE MULTIPLE FILES
# ============================================================
if len(dataframes) >= 2:
    st.markdown("### 🔗 Join Your Files (Optional)")
    file_names = list(dataframes.keys())

    jc1, jc2 = st.columns(2)
    with jc1:
        sel_f1 = st.selectbox("First File:", file_names, key="jf1")
    with jc2:
        rem = [f for f in file_names if f != sel_f1]
        sel_f2 = st.selectbox("Second File:", rem, key="jf2")

    jc3, jc4 = st.columns(2)
    with jc3:
        jcol1 = st.selectbox(f"Join Column ({sel_f1}):", dataframes[sel_f1].columns.tolist(), key="jc1")
    with jc4:
        jcol2 = st.selectbox(f"Join Column ({sel_f2}):", dataframes[sel_f2].columns.tolist(), key="jc2")

    jtype = st.radio("Join Type:", ["Inner Join", "Left Join", "Right Join", "Outer Join"],
                     horizontal=True, key="jtype")
    jmap = {"Inner Join": "inner", "Left Join": "left", "Right Join": "right", "Outer Join": "outer"}

    if st.button("🔗 Perform Join", key="join_btn"):
        try:
            merged = pd.merge(dataframes[sel_f1], dataframes[sel_f2],
                              left_on=jcol1, right_on=jcol2, how=jmap[jtype])
            st.session_state['merged_df'] = merged
            st.success(f"✅ Joined! Result: {merged.shape[0]:,} rows × {merged.shape[1]} cols")
        except Exception as e:
            st.error(f"❌ Join failed: {e}")

    st.markdown("---")

# ============================================================
# 7. MAIN ANALYSIS SECTION
# ============================================================
if dataframes:
    st.markdown("### 📊 Select Dataset to Analyze")

    options = list(dataframes.keys())
    if 'merged_df' in st.session_state:
        options.append("🔗 Merged Data")

    selected = st.selectbox("Choose dataset:", options, key="ds_select")

    # ---- BUG FIX: only reset working copy when dataset CHANGES ----
    # (Old code overwrote current_df on every rerun, losing all cleaning!)
    if st.session_state.active_dataset != selected or st.session_state.current_df is None:
        if selected == "🔗 Merged Data":
            base_df = st.session_state['merged_df'].copy()
        else:
            base_df = dataframes[selected].copy()
        st.session_state.active_dataset = selected
        st.session_state.current_df = base_df
        st.session_state.history = []
        st.session_state.redo_stack = []
        st.session_state.pipeline_log = [log_entry("📂 Load", f"Loaded '{selected}'", base_df.shape)]

    df = st.session_state.current_df

    # --------------------------------------------------------
    # PART 5: PIPELINE TRACKER + UNDO / REDO TOOLBAR
    # --------------------------------------------------------
    st.markdown("### 🧾 Cleaning Pipeline & Undo/Redo")

    ur1, ur2, ur3, ur4 = st.columns([1, 1, 1, 3])
    with ur1:
        if st.button(f"↩️ Undo ({len(st.session_state.history)})",
                     key="undo_btn", disabled=len(st.session_state.history) == 0,
                     use_container_width=True):
            do_undo()
            st.rerun()
    with ur2:
        if st.button(f"↪️ Redo ({len(st.session_state.redo_stack)})",
                     key="redo_btn", disabled=len(st.session_state.redo_stack) == 0,
                     use_container_width=True):
            do_redo()
            st.rerun()
    with ur3:
        if st.button("🔄 Reset All", key="reset_btn", use_container_width=True):
            st.session_state.active_dataset = None  # forces re-load on rerun
            st.rerun()
    with ur4:
        st.caption(f"💾 {len(st.session_state.pipeline_log)} steps logged | "
                   f"Undo memory holds last {MAX_HISTORY} actions | Everything in RAM only")

    with st.expander(f"📜 View Cleaning Steps Log ({len(st.session_state.pipeline_log)} steps)", expanded=False):
        if st.session_state.pipeline_log:
            log_df = pd.DataFrame(st.session_state.pipeline_log)
            st.dataframe(log_df, use_container_width=True, hide_index=True)
            log_csv = log_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Pipeline Log (CSV)", log_csv,
                               file_name="cleaning_pipeline_log.csv", mime="text/csv",
                               key="log_dl_btn")
        else:
            st.info("No steps logged yet.")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 1: BASIC OVERVIEW
    # --------------------------------------------------------
    st.markdown("## 📊 Basic Data Overview")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Rows", f"{df.shape[0]:,}")
    with m2:
        st.metric("Total Columns", df.shape[1])
    with m3:
        mem = df.memory_usage(deep=True).sum() / 1024 ** 2
        st.metric("Memory Usage", f"{mem:.2f} MB")
    with m4:
        st.metric("Data Types", df.dtypes.nunique())

    t1, t2, t3, t4, t5 = st.tabs(["Head", "Sample", "Info", "Columns", "Describe"])

    with t1:
        st.dataframe(df.head(10), use_container_width=True)
    with t2:
        st.dataframe(df.sample(min(5, df.shape[0])), use_container_width=True)
    with t3:
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Non-Null Count': df.count().values,
            'Dtype': df.dtypes.astype(str).values
        })
        st.dataframe(info_df, use_container_width=True)
    with t4:
        st.write(df.columns.tolist())
    with t5:
        st.dataframe(cached_describe(df), use_container_width=True)

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 2: DATA QUALITY CHECK
    # --------------------------------------------------------
    st.markdown("## 🔍 Data Quality Check")

    q1, q2 = st.columns(2)
    with q1:
        st.markdown("**Missing Values:**")
        miss = pd.DataFrame({
            'Column': df.columns,
            'Missing': df.isnull().sum().values,
            'Missing %': (df.isnull().sum() / len(df) * 100).round(2).values
        })
        miss = miss[miss['Missing'] > 0]
        if not miss.empty:
            st.dataframe(miss, use_container_width=True)
            fig = px.bar(miss, x='Column', y='Missing %',
                         title='Missing Values by Column',
                         color='Missing %', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No missing values found!")

    with q2:
        st.markdown("**Duplicate Rows:**")
        dup = df.duplicated().sum()
        st.metric("Duplicate Rows", f"{dup:,}")
        if dup > 0:
            st.warning(f"⚠️ {dup} exact duplicate rows found")
        else:
            st.success("✅ No exact duplicates!")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 3: FIX DATA TYPES
    # --------------------------------------------------------
    st.markdown("## 🔧 Fix Data Types")

    d1, d2, d3 = st.columns(3)
    with d1:
        col_to_fix = st.selectbox("Select Column:", df.columns.tolist(), key="dtype_col")
    with d2:
        st.markdown(f"**Current Type:** `{str(df[col_to_fix].dtype)}`")
        new_type = st.selectbox("Convert To:", ["Integer", "Float", "String", "Date"], key="new_dtype")
    with d3:
        st.markdown("**Action:**")
        if st.button("🔄 Convert Column", key="convert_btn"):
            try:
                new_df = df.copy()
                if new_type == "Integer":
                    new_df[col_to_fix] = pd.to_numeric(new_df[col_to_fix], errors='coerce').astype('Int64')
                elif new_type == "Float":
                    new_df[col_to_fix] = pd.to_numeric(new_df[col_to_fix], errors='coerce')
                elif new_type == "String":
                    new_df[col_to_fix] = new_df[col_to_fix].astype(str)
                elif new_type == "Date":
                    new_df[col_to_fix] = pd.to_datetime(new_df[col_to_fix], errors='coerce')
                apply_change(new_df, "🔧 Type Convert", f"'{col_to_fix}' → {new_type}")
                st.success(f"✅ '{col_to_fix}' converted to {new_type}!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Conversion failed: {e}")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 4: SMART DUPLICATE DETECTION
    # --------------------------------------------------------
    st.markdown("## 🗑️ Smart Duplicate Detection")
    st.info("💡 Select an ID column to exclude from duplicate check (like customer_id, transaction_id)")

    id_col = st.selectbox("Select ID/Primary Key Column:", ["None"] + df.columns.tolist(), key="id_col")
    check_cols = [c for c in df.columns if c != id_col] if id_col != "None" else df.columns.tolist()

    st.caption(f"Checking columns: {', '.join(check_cols)}")

    dup_mask = df.duplicated(subset=check_cols, keep=False)
    true_dups = df.duplicated(subset=check_cols, keep='first').sum()

    dc1, dc2 = st.columns(2)
    with dc1:
        st.metric("True Duplicates", true_dups)
    with dc2:
        if true_dups > 0:
            st.warning(f"⚠️ {true_dups} duplicate records found")
        else:
            st.success("✅ No duplicates based on selected columns!")

    if true_dups > 0:
        if st.checkbox("👀 Show Duplicate Rows", key="show_dup"):
            st.dataframe(df[dup_mask].sort_values(by=check_cols), use_container_width=True)

        if st.button("🗑️ Remove Duplicates", key="rem_dup_btn"):
            new_df = df.drop_duplicates(subset=check_cols, keep='first')
            apply_change(new_df, "🗑️ Remove Duplicates", f"{true_dups} rows removed")
            st.success(f"✅ Duplicates removed! New shape: {new_df.shape[0]:,} rows")
            st.rerun()

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 4.5: DATA CLEANING TOOLBOX (PART 1)
    # --------------------------------------------------------
    st.markdown("## 🧰 Data Cleaning Toolbox")

    tb1, tb2, tb3, tb4 = st.tabs(
        ["🕳️ Missing Values", "✂️ Rename/Drop Columns", "🔤 Text Cleaning", "🔎 Find & Replace (Regex)"]
    )

    # ---------- 4.5.1 MISSING VALUE HANDLING ----------
    with tb1:
        st.markdown("**Handle missing (null) values:**")
        miss_cols = df.columns[df.isnull().any()].tolist()

        if not miss_cols:
            st.success("✅ No missing values in this dataset!")
        else:
            mv1, mv2, mv3 = st.columns(3)
            with mv1:
                mv_col = st.selectbox("Select Column:", miss_cols, key="mv_col")
            with mv2:
                mv_action = st.selectbox(
                    "Action:",
                    ["Drop Rows (this column null)", "Fill with Mean", "Fill with Median",
                     "Fill with Mode", "Fill with Custom Value", "Forward Fill", "Backward Fill",
                     "Interpolate"],
                    key="mv_action"
                )
            custom_val = None
            with mv3:
                if mv_action == "Fill with Custom Value":
                    custom_val = st.text_input("Custom Value:", key="mv_custom")
                st.write("")
                apply_mv = st.button("✅ Apply", key="mv_apply_btn")

            if apply_mv:
                try:
                    new_df = df.copy()
                    if mv_action == "Drop Rows (this column null)":
                        new_df = new_df.dropna(subset=[mv_col])
                    elif mv_action == "Fill with Mean":
                        new_df[mv_col] = new_df[mv_col].fillna(new_df[mv_col].mean())
                    elif mv_action == "Fill with Median":
                        new_df[mv_col] = new_df[mv_col].fillna(new_df[mv_col].median())
                    elif mv_action == "Fill with Mode":
                        mode_val = new_df[mv_col].mode()
                        new_df[mv_col] = new_df[mv_col].fillna(mode_val[0] if not mode_val.empty else "")
                    elif mv_action == "Fill with Custom Value":
                        new_df[mv_col] = new_df[mv_col].fillna(custom_val)
                    elif mv_action == "Forward Fill":
                        new_df[mv_col] = new_df[mv_col].ffill()
                    elif mv_action == "Backward Fill":
                        new_df[mv_col] = new_df[mv_col].bfill()
                    elif mv_action == "Interpolate":
                        new_df[mv_col] = new_df[mv_col].interpolate()

                    apply_change(new_df, "🕳️ Missing Values", f"'{mv_col}' → {mv_action}")
                    st.success(f"✅ '{mv_col}' updated using '{mv_action}'. "
                               f"Remaining nulls: {new_df[mv_col].isnull().sum()}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Action failed: {e}")

            st.caption("💡 Mean/Median only work on numeric columns.")

    # ---------- 4.5.2 RENAME / DROP COLUMNS ----------
    with tb2:
        st.markdown("**Rename a column:**")
        rc1, rc2, rc3 = st.columns([2, 2, 1])
        with rc1:
            col_rename = st.selectbox("Select Column:", df.columns.tolist(), key="rename_col")
        with rc2:
            new_name = st.text_input("New Name:", value=col_rename, key="rename_val")
        with rc3:
            st.write("")
            if st.button("✏️ Rename", key="rename_btn"):
                if new_name and new_name != col_rename:
                    new_df = df.rename(columns={col_rename: new_name})
                    apply_change(new_df, "✏️ Rename Column", f"'{col_rename}' → '{new_name}'")
                    st.success(f"✅ '{col_rename}' renamed to '{new_name}'")
                    st.rerun()

        st.markdown("---")
        st.markdown("**Drop columns:**")
        drop_cols = st.multiselect("Select Columns to Drop:", df.columns.tolist(), key="drop_cols_ms")
        if st.button("🗑️ Drop Selected Columns", key="drop_cols_btn"):
            if drop_cols:
                new_df = df.drop(columns=drop_cols)
                apply_change(new_df, "✂️ Drop Columns", f"Dropped: {', '.join(drop_cols)}")
                st.success(f"✅ Dropped: {', '.join(drop_cols)}. "
                           f"New shape: {new_df.shape[0]:,} × {new_df.shape[1]}")
                st.rerun()
            else:
                st.warning("⚠️ Select at least one column to drop.")

    # ---------- 4.5.3 TEXT CLEANING ----------
    with tb3:
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            st.info("No text/string columns found in this dataset.")
        else:
            tc1, tc2 = st.columns(2)
            with tc1:
                tc_col = st.selectbox("Select Text Column:", text_cols, key="tc_col")
            with tc2:
                tc_action = st.selectbox(
                    "Cleaning Action:",
                    ["Trim Whitespace", "Lowercase", "UPPERCASE", "Title Case",
                     "Remove Special Characters", "Remove Extra Spaces"],
                    key="tc_action"
                )

            if st.button("🧹 Apply Text Cleaning", key="tc_apply_btn"):
                try:
                    new_df = df.copy()
                    s = new_df[tc_col].astype(str)
                    if tc_action == "Trim Whitespace":
                        s = s.str.strip()
                    elif tc_action == "Lowercase":
                        s = s.str.lower()
                    elif tc_action == "UPPERCASE":
                        s = s.str.upper()
                    elif tc_action == "Title Case":
                        s = s.str.title()
                    elif tc_action == "Remove Special Characters":
                        s = s.str.replace(r'[^A-Za-z0-9\s]', '', regex=True)
                    elif tc_action == "Remove Extra Spaces":
                        s = s.str.replace(r'\s+', ' ', regex=True).str.strip()

                    new_df[tc_col] = s
                    apply_change(new_df, "🔤 Text Cleaning", f"'{tc_col}' → {tc_action}")
                    st.success(f"✅ '{tc_col}' cleaned using '{tc_action}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Cleaning failed: {e}")

    # ---------- 4.5.4 FIND & REPLACE (REGEX) ----------
    with tb4:
        st.markdown("**Find & Replace (supports plain text or regex pattern):**")
        fr_col = st.selectbox("Select Column:", df.columns.tolist(), key="fr_col")

        fr1, fr2 = st.columns(2)
        with fr1:
            find_val = st.text_input("Find (text or regex):", key="fr_find")
        with fr2:
            replace_val = st.text_input("Replace With:", key="fr_replace")

        use_regex = st.checkbox("Treat 'Find' as Regex Pattern", value=False, key="fr_regex_toggle")

        if st.button("🔎 Apply Find & Replace", key="fr_apply_btn"):
            if find_val == "":
                st.warning("⚠️ Enter a value to find.")
            else:
                try:
                    new_df = df.copy()
                    new_df[fr_col] = new_df[fr_col].astype(str).str.replace(
                        find_val, replace_val, regex=use_regex
                    )
                    apply_change(new_df, "🔎 Find & Replace",
                                 f"'{find_val}' → '{replace_val}' in '{fr_col}'")
                    st.success(f"✅ Replaced '{find_val}' with '{replace_val}' in '{fr_col}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Find & Replace failed: {e}")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 4.7: OUTLIER DETECTION & FUZZY DUPLICATE MATCHING (PART 2)
    # --------------------------------------------------------
    df = st.session_state.current_df

    st.markdown("## 🎯 Outlier Detection & Fuzzy Duplicates")

    ob1, ob2 = st.tabs(["📏 Outlier Detection", "🧩 Fuzzy Duplicate Matching"])

    # ---------- 4.7.1 OUTLIER DETECTION ----------
    with ob1:
        out_num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not out_num_cols:
            st.info("No numeric columns found for outlier detection.")
        else:
            oc1, oc2, oc3 = st.columns(3)
            with oc1:
                out_col = st.selectbox("Select Numeric Column:", out_num_cols, key="out_col")
            with oc2:
                out_method = st.selectbox("Method:", ["IQR (Interquartile Range)", "Z-Score"], key="out_method")
            with oc3:
                if out_method == "IQR (Interquartile Range)":
                    iqr_mult = st.slider("IQR Multiplier:", 1.0, 3.0, 1.5, 0.1, key="iqr_mult")
                else:
                    z_thresh = st.slider("Z-Score Threshold:", 1.0, 5.0, 3.0, 0.1, key="z_thresh")

            col_data = df[out_col].dropna()

            if out_method == "IQR (Interquartile Range)":
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - iqr_mult * iqr
                upper = q3 + iqr_mult * iqr
                outlier_mask = (df[out_col] < lower) | (df[out_col] > upper)
                st.caption(f"Bounds: lower = {lower:.2f}, upper = {upper:.2f}")
            else:
                mean = col_data.mean()
                std = col_data.std()
                z_scores = (df[out_col] - mean) / std if std != 0 else df[out_col] * 0
                outlier_mask = z_scores.abs() > z_thresh
                st.caption(f"Mean = {mean:.2f}, Std = {std:.2f}")

            outlier_mask = outlier_mask.fillna(False)
            n_outliers = int(outlier_mask.sum())

            oc4, oc5 = st.columns(2)
            with oc4:
                st.metric("Outliers Found", n_outliers)
            with oc5:
                fig = px.box(df, y=out_col, title=f'Box Plot: {out_col} (outliers highlighted)',
                             points='outliers')
                st.plotly_chart(fig, use_container_width=True)

            if n_outliers > 0:
                if st.checkbox("👀 Show Outlier Rows", key="show_outliers"):
                    st.dataframe(df[outlier_mask], use_container_width=True)

                oa1, oa2 = st.columns(2)
                with oa1:
                    if st.button("🗑️ Remove Outlier Rows", key="remove_outliers_btn"):
                        new_df = df[~outlier_mask]
                        apply_change(new_df, "📏 Remove Outliers",
                                     f"{n_outliers} rows removed from '{out_col}' ({out_method})")
                        st.success(f"✅ Removed {n_outliers} outlier rows. New shape: {new_df.shape[0]:,} rows")
                        st.rerun()
                with oa2:
                    if st.button("📌 Cap Outliers (Winsorize)", key="cap_outliers_btn"):
                        new_df = df.copy()
                        if out_method == "IQR (Interquartile Range)":
                            new_df[out_col] = new_df[out_col].clip(lower=lower, upper=upper)
                        else:
                            new_df[out_col] = new_df[out_col].clip(lower=mean - z_thresh * std,
                                                                   upper=mean + z_thresh * std)
                        apply_change(new_df, "📌 Cap Outliers", f"'{out_col}' winsorized ({out_method})")
                        st.success(f"✅ '{out_col}' outliers capped to boundary values")
                        st.rerun()
            else:
                st.success("✅ No outliers detected with current settings!")

    # ---------- 4.7.2 FUZZY DUPLICATE MATCHING ----------
    with ob2:
        st.info("💡 Finds rows that are *similar but not exactly identical* (e.g. 'Jatin Kumar' vs 'jatin  kumar') — useful for messy text data like names, addresses, companies.")

        fuzzy_text_cols = df.select_dtypes(include=['object']).columns.tolist()

        if not fuzzy_text_cols:
            st.info("No text columns found for fuzzy matching.")
        else:
            fz1, fz2 = st.columns(2)
            with fz1:
                fuzzy_col = st.selectbox("Select Text Column to Compare:", fuzzy_text_cols, key="fuzzy_col")
            with fz2:
                fuzzy_thresh = st.slider("Similarity Threshold (%):", 70, 99, 90, 1, key="fuzzy_thresh")

            st.caption("⚠️ Compares every row against every other row — for large datasets this checks the first 2,000 rows only, to keep it fast.")

            if st.button("🔍 Find Fuzzy Duplicates", key="fuzzy_find_btn"):
                sample_df = df[[fuzzy_col]].dropna().reset_index()
                sample_df = sample_df.head(2000)
                values = sample_df[fuzzy_col].astype(str).tolist()
                idxs = sample_df['index'].tolist()

                matches = []
                seen = set()
                for i in range(len(values)):
                    if i in seen:
                        continue
                    group = [i]
                    for j in range(i + 1, len(values)):
                        if j in seen:
                            continue
                        score = fuzz.ratio(values[i], values[j])
                        if score >= fuzzy_thresh:
                            group.append(j)
                            seen.add(j)
                    if len(group) > 1:
                        seen.add(i)
                        for g in group:
                            matches.append({
                                'Group': len(matches) // max(len(group), 1) + 1,
                                'Row Index': idxs[g],
                                'Value': values[g]
                            })

                if matches:
                    match_df = pd.DataFrame(matches)
                    st.session_state['fuzzy_matches'] = match_df
                    st.warning(f"⚠️ Found {match_df['Row Index'].nunique()} rows involved in possible fuzzy duplicate groups")
                    st.dataframe(match_df, use_container_width=True)
                    st.caption("💡 Review these manually — fuzzy matches are suggestions, not automatic deletions. "
                               "Use 'Rename/Drop Columns' or the ID-based duplicate tool above to clean them up.")
                else:
                    st.success("✅ No fuzzy duplicates found at this similarity threshold!")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 4.8: QUICK PREDICT + ANOMALY DETECTION (PART 4)
    # --------------------------------------------------------
    df = st.session_state.current_df

    st.markdown("## 🤖 Quick Predict & Anomaly Detection (ML)")

    if not SKLEARN_OK:
        st.warning("⚠️ scikit-learn not installed. Run: `pip install scikit-learn` and add "
                   "`scikit-learn` to requirements.txt — it's free and runs 100% locally (no API).")
    else:
        ml1, ml2 = st.tabs(["🎯 Quick Predict (ML Model)", "🚨 Anomaly Detection (Isolation Forest)"])

        # ---------- 4.8.1 QUICK PREDICT ----------
        with ml1:
            st.info("💡 Trains a Random Forest model **inside your browser session** — nothing leaves "
                    "your session, no API, no cost. Pick a target column and see what predicts it!")

            ml_num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            all_usable = [c for c in df.columns
                          if df[c].dtype in [np.float64, np.int64, np.float32, np.int32, object]
                          or str(df[c].dtype).startswith(('int', 'float'))]

            if len(df.columns) < 2 or not all_usable:
                st.info("Need at least 2 columns for prediction.")
            else:
                mp1, mp2 = st.columns(2)
                with mp1:
                    target_col = st.selectbox("🎯 Target Column (what to predict):",
                                              df.columns.tolist(), key="ml_target")
                with mp2:
                    feat_options = [c for c in df.columns if c != target_col]
                    feature_cols = st.multiselect("📊 Feature Columns (predictors):",
                                                  feat_options,
                                                  default=[c for c in ml_num_cols if c != target_col][:5],
                                                  key="ml_features")

                # Auto-detect problem type
                target_series = df[target_col].dropna()
                is_numeric_target = pd.api.types.is_numeric_dtype(target_series)
                n_unique = target_series.nunique()

                if is_numeric_target and n_unique > 15:
                    problem_type = "Regression (predict a number)"
                else:
                    problem_type = "Classification (predict a category)"
                st.caption(f"🧠 Auto-detected: **{problem_type}** — target has {n_unique:,} unique values")

                if st.button("🚀 Train Model & Predict", key="ml_train_btn"):
                    if not feature_cols:
                        st.warning("⚠️ Select at least one feature column.")
                    else:
                        try:
                            with st.spinner("🧠 Training model (100% local, no API)..."):
                                ml_df = df[feature_cols + [target_col]].dropna()
                                if len(ml_df) > ML_SAMPLE_CAP:
                                    ml_df = ml_df.sample(ML_SAMPLE_CAP, random_state=42)
                                    st.caption(f"⚡ Sampled {ML_SAMPLE_CAP:,} rows for speed.")

                                if len(ml_df) < 30:
                                    st.error("❌ Need at least 30 non-null rows to train a model.")
                                else:
                                    # Encode categorical features (one-hot, capped)
                                    X = pd.get_dummies(ml_df[feature_cols], drop_first=True)
                                    if X.shape[1] > 200:
                                        st.warning("⚠️ Too many categories — using first 200 encoded features.")
                                        X = X.iloc[:, :200]
                                    y = ml_df[target_col]

                                    is_reg = problem_type.startswith("Regression")
                                    if not is_reg:
                                        y = y.astype(str)

                                    X_train, X_test, y_train, y_test = train_test_split(
                                        X, y, test_size=0.2, random_state=42
                                    )

                                    if is_reg:
                                        model = RandomForestRegressor(n_estimators=60, random_state=42, n_jobs=-1)
                                    else:
                                        model = RandomForestClassifier(n_estimators=60, random_state=42, n_jobs=-1)

                                    model.fit(X_train, y_train)
                                    preds = model.predict(X_test)

                                    st.markdown("### 📈 Model Results")
                                    r1, r2, r3 = st.columns(3)
                                    if is_reg:
                                        r2_val = r2_score(y_test, preds)
                                        mae = mean_absolute_error(y_test, preds)
                                        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
                                        with r1:
                                            st.metric("R² Score", f"{r2_val:.3f}")
                                        with r2:
                                            st.metric("MAE (avg error)", f"{mae:,.2f}")
                                        with r3:
                                            st.metric("RMSE", f"{rmse:,.2f}")
                                        st.session_state['ml_summary'] = (
                                            f"Regression on '{target_col}': R²={r2_val:.3f}, MAE={mae:.2f}, RMSE={rmse:.2f}"
                                        )

                                        # Actual vs Predicted plot
                                        fig = px.scatter(x=y_test, y=preds,
                                                         labels={'x': f'Actual {target_col}', 'y': f'Predicted {target_col}'},
                                                         title='Actual vs Predicted')
                                        fig.add_trace(go.Scatter(x=[y_test.min(), y_test.max()],
                                                                 y=[y_test.min(), y_test.max()],
                                                                 mode='lines', name='Perfect Prediction',
                                                                 line=dict(dash='dash', color='red')))
                                        st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        acc = accuracy_score(y_test, preds)
                                        with r1:
                                            st.metric("Accuracy", f"{acc * 100:.1f}%")
                                        with r2:
                                            st.metric("Classes", y.nunique())
                                        with r3:
                                            st.metric("Test Rows", len(y_test))
                                        st.session_state['ml_summary'] = (
                                            f"Classification on '{target_col}': Accuracy={acc*100:.1f}% ({y.nunique()} classes)"
                                        )

                                        # Confusion matrix (top 10 classes max)
                                        top_classes = y_test.value_counts().head(10).index.tolist()
                                        cm_mask = y_test.isin(top_classes)
                                        cm = confusion_matrix(y_test[cm_mask], pd.Series(preds)[cm_mask.values],
                                                              labels=top_classes)
                                        fig = px.imshow(cm, x=top_classes, y=top_classes, text_auto=True,
                                                        labels=dict(x="Predicted", y="Actual"),
                                                        title='Confusion Matrix (Top 10 classes)',
                                                        color_continuous_scale='Blues')
                                        st.plotly_chart(fig, use_container_width=True)

                                    # Feature importance
                                    imp_df = pd.DataFrame({
                                        'Feature': X.columns,
                                        'Importance': model.feature_importances_
                                    }).sort_values('Importance', ascending=False).head(15)
                                    fig = px.bar(imp_df, x='Importance', y='Feature', orientation='h',
                                                 title='🏆 What Drives the Prediction? (Feature Importance)',
                                                 color='Importance', color_continuous_scale='Viridis')
                                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                                    st.plotly_chart(fig, use_container_width=True)
                                    st.session_state['ml_importance'] = imp_df

                                    st.caption("💡 Model is temporary — it lives only in this session and is "
                                               "erased when you close the tab. Zero storage, zero API cost.")
                        except Exception as e:
                            st.error(f"❌ Model training failed: {e}")

        # ---------- 4.8.2 ANOMALY DETECTION ----------
        with ml2:
            st.info("💡 **Isolation Forest** finds rows that look 'strange' compared to the rest — "
                    "great for spotting fraud, data entry errors, or unusual records. Runs locally, no API.")

            an_num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            if len(an_num_cols) < 1:
                st.info("Need at least 1 numeric column for anomaly detection.")
            else:
                an1, an2 = st.columns(2)
                with an1:
                    anomaly_cols = st.multiselect("Numeric Columns to Analyze:",
                                                  an_num_cols, default=an_num_cols[:4],
                                                  key="anomaly_cols")
                with an2:
                    contamination = st.slider("Expected Anomaly % (contamination):",
                                              1, 20, 5, 1, key="contamination") / 100

                if st.button("🚨 Detect Anomalies", key="anomaly_btn"):
                    if not anomaly_cols:
                        st.warning("⚠️ Select at least one numeric column.")
                    else:
                        try:
                            with st.spinner("🔍 Scanning for anomalies..."):
                                an_data = df[anomaly_cols].dropna()
                                if len(an_data) < 20:
                                    st.error("❌ Need at least 20 non-null rows.")
                                    st.session_state.pop('anomaly_result', None)
                                else:
                                    iso = IsolationForest(contamination=contamination,
                                                          random_state=42, n_jobs=-1)
                                    labels = iso.fit_predict(an_data)
                                    scores = iso.decision_function(an_data)
                                    st.session_state['anomaly_result'] = {
                                        'index': an_data.index[labels == -1].tolist(),
                                        'cols': anomaly_cols,
                                        'labels': labels,
                                        'scores': scores,
                                        'data_index': an_data.index.tolist(),
                                        'n_scanned': len(an_data),
                                    }
                        except Exception as e:
                            st.error(f"❌ Anomaly detection failed: {e}")
                            st.session_state.pop('anomaly_result', None)

                # ---- Show results (persist across reruns so Remove button works) ----
                ar = st.session_state.get('anomaly_result')
                if ar:
                    anomaly_idx = [i for i in ar['index'] if i in df.index]
                    n_anom = len(anomaly_idx)

                    am1, am2, am3 = st.columns(3)
                    with am1:
                        st.metric("🚨 Anomalies Found", f"{n_anom:,}")
                    with am2:
                        st.metric("Rows Scanned", f"{ar['n_scanned']:,}")
                    with am3:
                        st.metric("Anomaly Rate", f"{n_anom / max(ar['n_scanned'], 1) * 100:.1f}%")

                    st.session_state['anomaly_summary'] = (
                        f"Isolation Forest: {n_anom:,} anomalies in {ar['n_scanned']:,} rows "
                        f"({n_anom / max(ar['n_scanned'], 1) * 100:.1f}%) using columns: {', '.join(ar['cols'])}"
                    )

                    # Visualize on first 2 columns
                    plot_cols = [c for c in ar['cols'] if c in df.columns]
                    valid_data_idx = [i for i in ar['data_index'] if i in df.index]
                    if len(plot_cols) >= 2 and valid_data_idx:
                        plot_df = df.loc[valid_data_idx, plot_cols].copy()
                        plot_df['Status'] = np.where(plot_df.index.isin(anomaly_idx), '🚨 Anomaly', '✅ Normal')
                        fig = px.scatter(plot_df, x=plot_cols[0], y=plot_cols[1],
                                         color='Status',
                                         color_discrete_map={'🚨 Anomaly': 'red', '✅ Normal': 'lightblue'},
                                         title='Anomalies Highlighted')
                        st.plotly_chart(fig, use_container_width=True)
                    elif len(plot_cols) == 1 and valid_data_idx:
                        plot_df = df.loc[valid_data_idx, plot_cols].copy()
                        plot_df['Status'] = np.where(plot_df.index.isin(anomaly_idx), '🚨 Anomaly', '✅ Normal')
                        fig = px.strip(plot_df, x=plot_cols[0], color='Status',
                                       color_discrete_map={'🚨 Anomaly': 'red', '✅ Normal': 'lightblue'},
                                       title='Anomalies Highlighted')
                        st.plotly_chart(fig, use_container_width=True)

                    if n_anom > 0:
                        with st.expander(f"👀 View {n_anom} Anomalous Rows"):
                            st.dataframe(df.loc[anomaly_idx], use_container_width=True)

                        if st.button("🗑️ Remove Anomalous Rows", key="rm_anomaly_btn"):
                            new_df = df.drop(index=anomaly_idx)
                            apply_change(new_df, "🚨 Remove Anomalies",
                                         f"{n_anom} anomalous rows removed (Isolation Forest)")
                            st.session_state.pop('anomaly_result', None)
                            st.success(f"✅ Removed {n_anom} anomalies!")
                            st.rerun()
                    else:
                        st.success("✅ No anomalies remaining with current settings!")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 5: INTERACTIVE VISUALIZATIONS (PLOTLY)
    # --------------------------------------------------------
    df = st.session_state.current_df

    st.markdown("## 📈 Interactive Visualizations")

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    v1, v2, v3, v4, v5, v6 = st.tabs(
        ["📊 Numeric", "🎨 Categorical", "🔥 Correlation", "📉 Trend", "🧮 Pivot Table", "🌍 Geo Map"]
    )

    with v1:
        if num_cols:
            sel_num = st.selectbox("Select Numeric Column:", num_cols, key="num_viz")

            vc1, vc2 = st.columns(2)
            with vc1:
                fig = px.histogram(df, x=sel_num, nbins=30,
                                   title=f'Distribution: {sel_num}',
                                   color_discrete_sequence=['#667eea'])
                st.plotly_chart(fig, use_container_width=True)
            with vc2:
                fig = px.box(df, y=sel_num, title=f'Box Plot: {sel_num}',
                             color_discrete_sequence=['#764ba2'])
                st.plotly_chart(fig, use_container_width=True)

            # Scatter plot if 2+ numeric columns
            if len(num_cols) >= 2:
                st.markdown("**Scatter Plot Explorer:**")
                sc1, sc2 = st.columns(2)
                with sc1:
                    x_axis = st.selectbox("X-Axis:", num_cols, key="scatter_x")
                with sc2:
                    y_axis = st.selectbox("Y-Axis:", [c for c in num_cols if c != x_axis], key="scatter_y")

                color_col = st.selectbox("Color By (optional):", ["None"] + cat_cols, key="scatter_color")
                fig = px.scatter(df, x=x_axis, y=y_axis,
                                 color=color_col if color_col != "None" else None,
                                 title=f'{x_axis} vs {y_axis}')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns found in this dataset")

    with v2:
        if cat_cols:
            sel_cat = st.selectbox("Select Categorical Column:", cat_cols, key="cat_viz")
            vc = df[sel_cat].value_counts().head(15).reset_index()
            vc.columns = [sel_cat, 'Count']

            fig = px.bar(vc, x=sel_cat, y='Count', title=f'Top 15: {sel_cat}',
                         color='Count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.pie(vc.head(8), names=sel_cat, values='Count',
                          title=f'Distribution: {sel_cat} (Top 8)')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No categorical columns found")

    with v3:
        if len(num_cols) >= 2:
            corr = cached_corr(df[num_cols])
            fig = px.imshow(corr, text_auto='.2f', aspect='auto',
                            color_continuous_scale='RdBu_r',
                            title='Correlation Heatmap')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation")

    with v4:
        if date_cols and num_cols:
            dc1, dc2 = st.columns(2)
            with dc1:
                x_date = st.selectbox("Date Column:", date_cols, key="trend_x")
            with dc2:
                y_val = st.selectbox("Value Column:", num_cols, key="trend_y")

            trend_df = df.dropna(subset=[x_date, y_val]).sort_values(x_date)
            fig = px.line(trend_df, x=x_date, y=y_val, title=f'{y_val} Trend Over Time')
            st.plotly_chart(fig, use_container_width=True)

            # ---- Time Series Decomposition ----
            with st.expander("📆 Time Series Decomposition (Trend / Seasonality / Residual)"):
                st.caption("Breaks the series into its underlying Trend, Seasonal pattern, and leftover Residual noise. "
                           "Needs enough data points to detect a repeating pattern.")
                period_guess = st.number_input(
                    "Seasonal Period (e.g. 7 = weekly, 12 = monthly, 365 = yearly):",
                    min_value=2, value=7, step=1, key="decomp_period"
                )
                if st.button("📊 Run Decomposition", key="decomp_btn"):
                    try:
                        ts = trend_df.set_index(x_date)[y_val].asfreq(
                            pd.infer_freq(trend_df[x_date]) or 'D'
                        )
                        ts = ts.interpolate()
                        if len(ts) < 2 * period_guess:
                            st.warning(f"⚠️ Need at least {2 * period_guess} data points for period={period_guess}. "
                                       f"This dataset has {len(ts)}.")
                        else:
                            result = seasonal_decompose(ts, model='additive', period=int(period_guess))
                            decomp_df = pd.DataFrame({
                                'Date': ts.index,
                                'Observed': result.observed.values,
                                'Trend': result.trend.values,
                                'Seasonal': result.seasonal.values,
                                'Residual': result.resid.values
                            })
                            fig_t = px.line(decomp_df, x='Date', y='Trend', title='Trend Component')
                            fig_s = px.line(decomp_df, x='Date', y='Seasonal', title='Seasonal Component')
                            fig_r = px.scatter(decomp_df, x='Date', y='Residual', title='Residual (Noise)')
                            st.plotly_chart(fig_t, use_container_width=True)
                            st.plotly_chart(fig_s, use_container_width=True)
                            st.plotly_chart(fig_r, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Decomposition failed: {e}. Try a different period or check for gaps in dates.")
        else:
            st.info("Need a date column and numeric column for trend analysis. "
                    "Convert a column to Date type in 'Fix Data Types' section above.")

    with v5:
        st.markdown("**Build a Pivot Table** (group data and aggregate values):")
        pv1, pv2, pv3 = st.columns(3)
        with pv1:
            pivot_rows = st.multiselect("Rows (group by):", df.columns.tolist(), key="pivot_rows")
        with pv2:
            pivot_cols_sel = st.multiselect("Columns (optional split by):",
                                            [c for c in cat_cols if c not in pivot_rows], key="pivot_cols")
        with pv3:
            pivot_val = st.selectbox("Value Column (to aggregate):", num_cols if num_cols else df.columns.tolist(),
                                     key="pivot_val")

        agg_func = st.selectbox("Aggregation:", ["sum", "mean", "count", "min", "max", "median"], key="pivot_agg")

        if st.button("🧮 Generate Pivot Table", key="pivot_btn"):
            if not pivot_rows:
                st.warning("⚠️ Select at least one column for Rows.")
            else:
                try:
                    pivot_result = pd.pivot_table(
                        df,
                        index=pivot_rows,
                        columns=pivot_cols_sel if pivot_cols_sel else None,
                        values=pivot_val,
                        aggfunc=agg_func,
                        fill_value=0
                    )
                    st.session_state['pivot_result'] = pivot_result
                    st.dataframe(pivot_result, use_container_width=True)

                    pivot_csv = pivot_result.to_csv().encode('utf-8')
                    st.download_button("📥 Download Pivot Table (CSV)", pivot_csv,
                                       file_name="pivot_table.csv", mime="text/csv", key="pivot_dl_btn")
                except Exception as e:
                    st.error(f"❌ Pivot failed: {e}")

    with v6:
        st.markdown("**Geo Map** (plots countries/regions on a world map — no API key needed):")
        st.caption("💡 Works best with a column containing country names or ISO-3 country codes (e.g. 'India', 'IND').")

        geo_col = st.selectbox("Select Location Column (country names/codes):",
                               cat_cols if cat_cols else df.columns.tolist(), key="geo_col")
        geo_val_col = st.selectbox("Value Column (color intensity, optional):",
                                   ["Count of Rows"] + num_cols, key="geo_val_col")

        if st.button("🌍 Generate Map", key="geo_btn"):
            try:
                if geo_val_col == "Count of Rows":
                    geo_data = df[geo_col].value_counts().reset_index()
                    geo_data.columns = [geo_col, 'Value']
                else:
                    geo_data = df.groupby(geo_col)[geo_val_col].sum().reset_index()
                    geo_data.columns = [geo_col, 'Value']

                fig = px.choropleth(
                    geo_data, locations=geo_col, locationmode='country names',
                    color='Value', color_continuous_scale='Blues',
                    title='Geographic Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("⚠️ If the map looks empty, your location column may not match standard country names — "
                           "try full country names like 'India', 'United States' instead of city names or codes.")
            except Exception as e:
                st.error(f"❌ Map generation failed: {e}")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 6: AUTO EDA SUMMARY
    # --------------------------------------------------------
    st.markdown("## 🤖 Auto EDA Summary")

    with st.expander("📋 Click to view Full Automated Report", expanded=False):
        st.markdown(f"""
        ### Dataset Overview
        - **Total Records:** {df.shape[0]:,}
        - **Total Features:** {df.shape[1]}
        - **Numeric Features:** {len(num_cols)}
        - **Categorical Features:** {len(cat_cols)}
        - **Missing Data:** {df.isnull().sum().sum():,} cells ({(df.isnull().sum().sum()/(df.shape[0]*df.shape[1])*100):.1f}%)
        - **Duplicate Rows:** {df.duplicated().sum():,}
        """)

        if num_cols:
            st.markdown("### 📊 Numeric Columns Summary")
            summary_data = []
            for col in num_cols:
                summary_data.append({
                    'Column': col,
                    'Mean': round(df[col].mean(), 2),
                    'Std Dev': round(df[col].std(), 2),
                    'Min': round(df[col].min(), 2),
                    'Max': round(df[col].max(), 2),
                    'Skewness': round(df[col].skew(), 2)
                })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

        if cat_cols:
            st.markdown("### 🎨 Categorical Columns Summary")
            cat_summary = []
            for col in cat_cols:
                cat_summary.append({
                    'Column': col,
                    'Unique Values': df[col].nunique(),
                    'Most Common': df[col].mode()[0] if not df[col].mode().empty else 'N/A',
                    'Missing %': round(df[col].isnull().sum() / len(df) * 100, 1)
                })
            st.dataframe(pd.DataFrame(cat_summary), use_container_width=True)

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 7: DOWNLOAD CLEANED DATA + REPORTS (PART 6)
    # --------------------------------------------------------
    st.markdown("## 💾 Download Results")
    st.info("🔒 Nothing is saved on our servers — download now before closing this tab!")

    final_df = st.session_state.current_df

    dl1, dl2 = st.columns(2)

    with dl1:
        csv_out = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Cleaned CSV",
            csv_out,
            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv_btn"
        )

    with dl2:
        # Excel download option
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='Cleaned_Data')
        st.download_button(
            "📥 Download as Excel",
            buffer.getvalue(),
            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_xlsx_btn"
        )

    # ---------- 7.1 TEXT REPORT ----------
    pipeline_text = "\n".join(
        f"  {s['Step']}. [{s['Time']}] {s['Action']} - {s['Detail']} (shape: {s['Shape']})"
        for s in st.session_state.pipeline_log
    )
    report_text = f"""
DATA CLEANING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=====================================

DATASET SUMMARY
- Total Rows: {final_df.shape[0]:,}
- Total Columns: {final_df.shape[1]}
- Numeric Columns: {len(num_cols)}
- Categorical Columns: {len(cat_cols)}
- Missing Values: {final_df.isnull().sum().sum():,}
- Duplicate Rows: {final_df.duplicated().sum():,}

CLEANING PIPELINE (all steps applied)
{pipeline_text}

COLUMN DETAILS
{final_df.dtypes.to_string()}

---
Generated by Jatin Kumar's Data Cleaning Tool
https://jatinanalytics.co.in
"""
    st.download_button(
        "📄 Download Text Report",
        report_text,
        file_name=f"data_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_report_btn"
    )

    # ---------- 7.2 PDF REPORT GENERATOR (PART 6) ----------
    st.markdown("### 📑 Professional PDF Report")

    if not FPDF_OK:
        st.warning("⚠️ fpdf2 not installed. Run: `pip install fpdf2` and add `fpdf2` to "
                   "requirements.txt — free library, generates PDFs 100% locally.")
    else:
        def _safe(text):
            """fpdf core fonts are latin-1 only - strip emojis/unicode safely"""
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        def build_pdf_report():
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # ---- Page 1: Cover + Summary ----
            pdf.add_page()
            pdf.set_fill_color(102, 126, 234)
            pdf.rect(0, 0, 210, 40, 'F')
            pdf.set_font('Helvetica', 'B', 22)
            pdf.set_text_color(255, 255, 255)
            pdf.set_y(12)
            pdf.cell(0, 10, 'DATA CLEANING & ANALYSIS REPORT', align='C')
            pdf.ln(20)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 8, _safe(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}  |  "
                                 f"Dataset: {st.session_state.active_dataset}"), align='C')
            pdf.ln(14)

            # Summary metrics
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, '1. Dataset Summary')
            pdf.ln(10)
            pdf.set_font('Helvetica', '', 10)
            summary_rows = [
                ("Total Rows", f"{final_df.shape[0]:,}"),
                ("Total Columns", str(final_df.shape[1])),
                ("Numeric Columns", str(len(num_cols))),
                ("Categorical Columns", str(len(cat_cols))),
                ("Missing Values", f"{final_df.isnull().sum().sum():,}"),
                ("Duplicate Rows", f"{final_df.duplicated().sum():,}"),
                ("Memory Usage", f"{final_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"),
            ]
            for label, val in summary_rows:
                pdf.set_fill_color(243, 244, 246)
                pdf.cell(70, 8, _safe(label), border=1, fill=True)
                pdf.cell(60, 8, _safe(val), border=1)
                pdf.ln(8)

            # ---- Cleaning pipeline ----
            pdf.ln(6)
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, '2. Cleaning Steps Applied')
            pdf.ln(10)
            pdf.set_font('Helvetica', '', 9)
            if st.session_state.pipeline_log:
                for s in st.session_state.pipeline_log:
                    # strip emoji from action names
                    action = ''.join(ch for ch in s['Action'] if ord(ch) < 256).strip()
                    line = f"Step {s['Step']} [{s['Time']}] {action}: {s['Detail']}  (shape: {s['Shape']})"
                    pdf.multi_cell(0, 6, _safe(line))
            else:
                pdf.cell(0, 6, 'No cleaning steps applied.')
                pdf.ln(6)

            # ---- ML results, if any ----
            if st.session_state.get('ml_summary') or st.session_state.get('anomaly_summary'):
                pdf.ln(4)
                pdf.set_font('Helvetica', 'B', 14)
                pdf.cell(0, 10, '3. Machine Learning Insights')
                pdf.ln(10)
                pdf.set_font('Helvetica', '', 9)
                if st.session_state.get('ml_summary'):
                    pdf.multi_cell(0, 6, _safe("Quick Predict: " + st.session_state['ml_summary']))
                if st.session_state.get('anomaly_summary'):
                    pdf.multi_cell(0, 6, _safe("Anomaly Detection: " + st.session_state['anomaly_summary']))
                if isinstance(st.session_state.get('ml_importance'), pd.DataFrame):
                    pdf.ln(2)
                    pdf.set_font('Helvetica', 'B', 10)
                    pdf.cell(0, 7, 'Top Predictive Features:')
                    pdf.ln(7)
                    pdf.set_font('Helvetica', '', 9)
                    for _, row in st.session_state['ml_importance'].head(8).iterrows():
                        pdf.cell(0, 6, _safe(f"  - {row['Feature']}: {row['Importance']:.3f}"))
                        pdf.ln(6)

            # ---- Page 2: Column details ----
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, '4. Column Details')
            pdf.ln(10)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_fill_color(102, 126, 234)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(60, 8, 'Column', border=1, fill=True)
            pdf.cell(30, 8, 'Type', border=1, fill=True)
            pdf.cell(30, 8, 'Non-Null', border=1, fill=True)
            pdf.cell(30, 8, 'Missing %', border=1, fill=True)
            pdf.cell(30, 8, 'Unique', border=1, fill=True)
            pdf.ln(8)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 8)
            for i, col in enumerate(final_df.columns[:60]):  # cap at 60 columns
                fill = i % 2 == 0
                pdf.set_fill_color(243, 244, 246)
                pdf.cell(60, 7, _safe(str(col)[:35]), border=1, fill=fill)
                pdf.cell(30, 7, _safe(str(final_df[col].dtype)), border=1, fill=fill)
                pdf.cell(30, 7, f"{final_df[col].count():,}", border=1, fill=fill)
                pdf.cell(30, 7, f"{final_df[col].isnull().mean() * 100:.1f}%", border=1, fill=fill)
                pdf.cell(30, 7, f"{final_df[col].nunique():,}", border=1, fill=fill)
                pdf.ln(7)

            # ---- Numeric stats ----
            if num_cols:
                pdf.ln(6)
                pdf.set_font('Helvetica', 'B', 14)
                pdf.cell(0, 10, '5. Numeric Statistics')
                pdf.ln(10)
                pdf.set_font('Helvetica', 'B', 8)
                pdf.set_fill_color(102, 126, 234)
                pdf.set_text_color(255, 255, 255)
                for h, w in [('Column', 50), ('Mean', 28), ('Std', 28), ('Min', 28), ('Max', 28), ('Skew', 20)]:
                    pdf.cell(w, 8, h, border=1, fill=True)
                pdf.ln(8)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Helvetica', '', 8)
                for i, col in enumerate(num_cols[:30]):
                    fill = i % 2 == 0
                    pdf.set_fill_color(243, 244, 246)
                    pdf.cell(50, 7, _safe(str(col)[:28]), border=1, fill=fill)
                    pdf.cell(28, 7, f"{final_df[col].mean():,.2f}", border=1, fill=fill)
                    pdf.cell(28, 7, f"{final_df[col].std():,.2f}", border=1, fill=fill)
                    pdf.cell(28, 7, f"{final_df[col].min():,.2f}", border=1, fill=fill)
                    pdf.cell(28, 7, f"{final_df[col].max():,.2f}", border=1, fill=fill)
                    pdf.cell(20, 7, f"{final_df[col].skew():.2f}", border=1, fill=fill)
                    pdf.ln(7)

            # ---- Charts page (matplotlib -> in-memory PNG -> PDF) ----
            if MPL_OK and num_cols:
                pdf.add_page()
                pdf.set_font('Helvetica', 'B', 14)
                pdf.cell(0, 10, '6. Key Charts')
                pdf.ln(12)
                try:
                    # Histogram of first numeric column
                    fig, ax = plt.subplots(figsize=(7, 3.2))
                    final_df[num_cols[0]].dropna().hist(bins=30, ax=ax, color='#667eea', edgecolor='white')
                    ax.set_title(f'Distribution: {num_cols[0]}')
                    img_buf = BytesIO()
                    fig.savefig(img_buf, format='png', dpi=110, bbox_inches='tight')
                    plt.close(fig)
                    img_buf.seek(0)
                    pdf.image(img_buf, x=15, w=180)
                    pdf.ln(5)

                    # Missing values bar chart (if any)
                    miss_pct = final_df.isnull().mean() * 100
                    miss_pct = miss_pct[miss_pct > 0].sort_values(ascending=False).head(15)
                    if not miss_pct.empty:
                        fig, ax = plt.subplots(figsize=(7, 3.2))
                        miss_pct.plot(kind='bar', ax=ax, color='#e53e3e')
                        ax.set_title('Missing Values % by Column')
                        ax.set_ylabel('%')
                        img_buf2 = BytesIO()
                        fig.savefig(img_buf2, format='png', dpi=110, bbox_inches='tight')
                        plt.close(fig)
                        img_buf2.seek(0)
                        pdf.image(img_buf2, x=15, w=180)
                except Exception:
                    pdf.set_font('Helvetica', '', 9)
                    pdf.cell(0, 8, 'Chart rendering skipped.')

            # ---- Footer ----
            pdf.set_y(-25)
            pdf.set_font('Helvetica', 'I', 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 8, _safe("Generated by Jatin Kumar's Data Cleaning Tool | jatinanalytics.co.in | "
                                 "100% private - no data stored"), align='C')

            return bytes(pdf.output())

        if st.button("📑 Generate PDF Report", key="pdf_gen_btn", use_container_width=True):
            try:
                with st.spinner("📄 Building your polished PDF report..."):
                    pdf_bytes = build_pdf_report()
                    st.session_state['pdf_report'] = pdf_bytes
                st.success("✅ PDF report ready! Download below.")
            except Exception as e:
                st.error(f"❌ PDF generation failed: {e}")

        if st.session_state.get('pdf_report'):
            st.download_button(
                "📥 Download PDF Report",
                st.session_state['pdf_report'],
                file_name=f"data_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_btn"
            )

else:
    st.info("👆 Upload at least one file above to start cleaning and analyzing your data!")

    st.markdown("---")
    st.markdown("""
    ### 💡 What Can You Do Here?

    - 🔍 **Explore** your data with automatic overview and statistics
    - 🧹 **Clean** missing values, duplicates, and fix data types
    - ↩️ **Undo/Redo** any cleaning step + full pipeline log
    - 🔗 **Merge** multiple files together (joins)
    - 📊 **Visualize** with interactive Plotly charts
    - 🤖 **Quick Predict** - train ML models on your data (no API, free)
    - 🚨 **Anomaly Detection** - spot strange rows with Isolation Forest
    - 📑 **PDF Report** - download a polished professional report
    - 💾 **Export** cleaned data as CSV or Excel

    **Supported formats:** CSV, Excel (.xlsx), JSON
    **Max size:** 150,000 rows per file
    **Privacy:** Zero data storage — everything clears when you close this tab
    """)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("🔒 Privacy-first tool | No data stored | Session-only processing | © 2026 Jatin Kumar")
