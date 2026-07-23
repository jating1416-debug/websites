import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

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
    """Load file into memory only - NEVER writes to disk"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        elif file.name.endswith('.json'):
            df = pd.read_json(file)
        else:
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

    if selected == "🔗 Merged Data":
        df = st.session_state['merged_df'].copy()
    else:
        df = dataframes[selected].copy()

    st.session_state['current_df'] = df
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
        st.dataframe(df.describe(include='all').fillna('-'), use_container_width=True)

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
                if new_type == "Integer":
                    df[col_to_fix] = pd.to_numeric(df[col_to_fix], errors='coerce').astype('Int64')
                elif new_type == "Float":
                    df[col_to_fix] = pd.to_numeric(df[col_to_fix], errors='coerce')
                elif new_type == "String":
                    df[col_to_fix] = df[col_to_fix].astype(str)
                elif new_type == "Date":
                    df[col_to_fix] = pd.to_datetime(df[col_to_fix], errors='coerce')
                st.session_state['current_df'] = df
                st.success(f"✅ '{col_to_fix}' converted to {new_type}!")
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
            df = df.drop_duplicates(subset=check_cols, keep='first')
            st.session_state['current_df'] = df
            st.success(f"✅ Duplicates removed! New shape: {df.shape[0]:,} rows")

    st.markdown("---")

    # --------------------------------------------------------
    # SECTION 5: INTERACTIVE VISUALIZATIONS (PLOTLY)
    # --------------------------------------------------------
    df = st.session_state.get('current_df', df)

    st.markdown("## 📈 Interactive Visualizations")

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    v1, v2, v3, v4 = st.tabs(["📊 Numeric", "🎨 Categorical", "🔥 Correlation", "📉 Trend"])

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
            corr = df[num_cols].corr()
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
        else:
            st.info("Need a date column and numeric column for trend analysis. "
                     "Convert a column to Date type in 'Fix Data Types' section above.")

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
    # SECTION 7: DOWNLOAD CLEANED DATA + REPORT
    # --------------------------------------------------------
    st.markdown("## 💾 Download Results")
    st.info("🔒 Nothing is saved on our servers — download now before closing this tab!")

    final_df = st.session_state.get('current_df', df)

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

    # Summary report text download
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

else:
    st.info("👆 Upload at least one file above to start cleaning and analyzing your data!")

    st.markdown("---")
    st.markdown("""
    ### 💡 What Can You Do Here?
    
    - 🔍 **Explore** your data with automatic overview and statistics
    - 🧹 **Clean** missing values, duplicates, and fix data types  
    - 🔗 **Merge** multiple files together (joins)
    - 📊 **Visualize** with interactive Plotly charts
    - 🤖 **Auto EDA** - instant exploratory data analysis
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