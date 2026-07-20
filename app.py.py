import streamlit as st
import os

# ==========================================
# 1. PAGE CONFIGURATION & SEO INTEGRATION
# ==========================================
st.set_page_config(
    page_title="Jatin Kumar | Data Analytics Portfolio", 
    layout="wide",
    page_icon="📊"
)
st.markdown("""
    <style>
    img {
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# 🔍 GOOGLE SEARCH CONSOLE VERIFICATION
GOOGLE_VERIFICATION_CODE = "YOUR_GOOGLE_VERIFICATION_CODE"
st.html(f"""
    <script>
        var meta = document.createElement('meta');
        meta.name = "google-site-verification";
        meta.content = "{GOOGLE_VERIFICATION_CODE}";
        window.parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
""")

# ==========================================
# 2. SIDEBAR - PROFILE & SOCIAL LINKS
# ==========================================
with st.sidebar:
    st.title("👨‍💻 Jatin Kumar")
    st.subheader("Data Analyst | SQL | Power BI")
    
    st.markdown("### 🔗 Connect With Me")
    st.markdown("🔵 [LinkedIn Profile](https://www.linkedin.com/in/jatin-kumar-5a46a720a/)")
    st.markdown("🐈 [GitHub Repository](https://github.com/jating1416-debug)")
    st.markdown("🦅 [Kaggle Profile](https://www.kaggle.com/jatinkhandelwal112)")
    
    st.write("---")
    
    st.markdown("### 🛠️ Technical Ecosystem")
    st.markdown("""
    - **Languages:** Python (Pandas, NumPy), SQL (MySQL Engine)
    - **BI Tools:** Power BI (DAX, Modeling), Excel
    - **Core:** Data Engineering, Star Schemas, Fraud Analytics
    """)
    
    st.write("---")
    
    # Dynamic Folder Path Info
PROJECTS_DIR = r"C:\Users\JATIN\OneDrive\Desktop\Website\projects"
st.info(f"📂 **Active Projects Folder:**\n`{PROJECTS_DIR}`")

# ==========================================
# 3. MAIN HEADER & EXECUTIVE SUMMARY
# ==========================================
st.title("📊 Data Analytics Portfolio")
st.caption("Engineered by Jatin Kumar")

st.markdown("### 💼 Executive Summary")
st.write("""
Data Analyst with core expertise in processing heavy financial datasets (1.2M+ records) 
into actionable risk and performance metrics. Skilled in architecting end-to-end data pipelines 
using Python and MySQL, and building high-impact, decision-ready dashboards in Power BI. 
Focused on delivering high-performance analytics to monitor transactional velocity, fraud patterns, and operational growth.
""")

st.markdown("---")

# ==========================================
# 4. DYNAMIC AUTOMATED FOLDER SCANNER
# ==========================================
st.header("📁 Production-Grade Projects")

# Create folder if it doesn't exist
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

# Read subdirectories dynamically
project_folders = [f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))]

if not project_folders:
    st.warning(f"⚠️ `{PROJECTS_DIR}` folder abhi khali hai. Apne `Website` folder ke andar `projects` folder mein subfolders banayein.")
    st.info("""
    👉 **Kaise Use Karein (Zero Code Changes):**
    1. `projects` folder mein ek naya folder banao, jaise: `01_Bank_Analytics` ya `02_Fraud_Analytics`.
    2. Us folder mein apni **Dashboard Image** (`.png` / `.jpg`), **SQL File** (`.sql`), aur **Python Code** (`.py`) paste kar do.
    3. Browser ko refresh karo, website automatically aapka naya tab aur saara content dikha degi!
    """)
else:
    # Build Tabs dynamically based on subfolder names!
    tabs = st.tabs([folder.replace("_", " ") for folder in project_folders])

    for idx, folder in enumerate(project_folders):
        folder_path = os.path.join(PROJECTS_DIR, folder)
        files = os.listdir(folder_path)

        with tabs[idx]:
            st.subheader(folder.replace("_", " "))

            # 1. Automatic Image Scanner & SEO Alt Tag Generator
            images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            if images:
                for img in images:
                    img_path = os.path.join(folder_path, img)
                    # Google SEO Optimized Alt Tag
                    alt_text = f"{folder.replace('_', ' ')} Dashboard Jatin Kumar Data Analyst"
                    # Centered Layout & Controlled Width
                    col_img1, col_img2, col_img3 = st.columns([1, 8, 1])
                    with col_img2:
                     st.image(img_path, caption=f"📊 Dashboard Visual: {img}", width=850)
            else:
                st.info("📷 Iss folder mein abhi tak koi Image (.png/.jpg) nahi mili.")

            st.markdown("---")

            col_code1, col_code2 = st.columns(2)

            # 2. Automatic SQL Script Scanner
            with col_code1:
                sql_files = [f for f in files if f.lower().endswith('.sql')]
                if sql_files:
                    st.markdown("#### 🗄️ MySQL Query Engine")
                    for sql_file in sql_files:
                        sql_path = os.path.join(folder_path, sql_file)
                        with open(sql_path, "r", encoding="utf-8") as f:
                            sql_content = f.read()
                        st.caption(f"File: {sql_file}")
                        st.code(sql_content, language="sql")

            # 3. Automatic Python Script Scanner
            with col_code2:
                py_files = [f for f in files if f.lower().endswith('.py')]
                if py_files:
                    st.markdown("#### 🐍 Python Analytics Pipeline")
                    for py_file in py_files:
                        py_path = os.path.join(folder_path, py_file)
                        with open(py_path, "r", encoding="utf-8") as f:
                            py_content = f.read()
                        st.caption(f"File: {py_file}")
                        st.code(py_content, language="python")

st.markdown("---")
st.caption("Engineered for Google Indexing & Optimization by Jatin Kumar © 2026")