
import os
import streamlit as st
from PIL import Image
import pandas as pd          
import numpy as np           
import matplotlib.pyplot as plt  
import seaborn as sns  
import streamlit.components.v1 as components 


# ==========================================
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="Jatin Kumar | Data Analyst Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Search Console Verification Tag
components.html(
    '<meta name="google-site-verification" content="google913320ab3b7a3a08" />', 
    height=0
)



# Custom Styling for modern look
st.markdown("""
    <style>
    /* Hero Section Styling */
    .hero-section {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 20px;
    }
    .hero-description {
        font-size: 1.1rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Main Styling */
    .main-title { font-size: 2.3rem; font-weight: 700; color: #1E88E5; }
    .sub-title { font-size: 1.2rem; color: #555555; }
    .badge {
        display: inline-block;
        padding: 6px 14px;
        margin: 4px;
        background-color: #E3F2FD;
        color: #0D47A1;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .st-expander {
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        background-color: #FAFAFA;
    }
    
    /* Status Badge */
    .status-badge {
        background: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
        margin: 10px 0;
    }
    
    /* Social Icons */
    .social-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    .social-card {
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        min-width: 150px;
    }
    .social-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: gray;
        margin-top: 50px;
        border-top: 2px solid #E0E0E0;
    }
    
    /* Navigation Guide Box */
    .nav-guide {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

# File extensions grouping
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG', '.gif', '.GIF')
VIDEO_EXTS = ('.mp4', '.mov', '.webm', '.MP4')
CODE_EXTS = {
    'Python 🐍': ('.py', '.ipynb'),
    'SQL Database 💾': ('.sql',),
    'Excel / Data 📊': ('.xlsx', '.csv'),
    'Power BI Report 📈': ('.pbix',)
}

# ==========================================
# 2. SIDEBAR WITH NAVIGATION & PHOTO
# ==========================================
with st.sidebar:
    # Profile Photo (if exists)
    photo_path = os.path.join(BASE_DIR, "profile_photo.jpg")
    if os.path.exists(photo_path):
        st.image(photo_path, width=200)
    else:
        st.markdown("### 👤 Jatin Kumar")
        st.caption("Data Analyst")
    
    st.markdown("---")
    
    # NAVIGATION GUIDE (WORKING VERSION)
    st.markdown("### 📍 Page Navigation")
    st.markdown("""
    <div class="nav-guide">
        <p style='margin: 5px 0; font-size: 0.95rem;'><b>👆 Use the tabs above to navigate:</b></p>
        <p style='margin: 5px 0;'>🏠 <b>Home</b> - About & Skills</p>
        <p style='margin: 5px 0;'>🎯 <b>Projects</b> - View all 4+ projects</p>
        <p style='margin: 5px 0;'>🖼️ <b>Gallery</b> - All visualizations</p>
        <p style='margin: 5px 0;'>📄 <b>Resume</b> - Download CV</p>
        <p style='margin: 5px 0;'>📬 <b>Contact</b> - Get in touch</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Professional Links
    st.markdown("### 🔗 Connect With Me")
    st.markdown("""
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jatin-kumar-5a46a720a)
    
    [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jating1416-debug)
    
    [![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/jatinkhandelwal112)
    
    [![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:Jating1416@gmail.com)
    """)
    
    st.markdown("---")
    
    # Status
    st.markdown("### 🎯 Current Status")
    st.success("✅ Open to Opportunities")
    st.info("📍 Seeking: Data Analyst / BI Analyst roles")
    
    st.markdown("---")
    
    # Resume Download
    resume_path = os.path.join(BASE_DIR, "resume.pdf")
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Resume",
                data=pdf_file,
                file_name="Jatin_Kumar_Resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.caption("💡 Add 'resume.pdf' to enable download")

# ==========================================
# 3. HERO SECTION (PROFESSIONAL BANNER)
# ==========================================
banner_filename = "ChatGPT Image Jul 10, 2026, 09_40_34 AM.png"
banner_path = os.path.join(BASE_DIR, banner_filename)

if os.path.exists(banner_path):
    banner_image = Image.open(banner_path)
    st.image(banner_image, use_container_width=True)
else:
    # Fallback Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">👋 Hi, I'm Jatin Kumar</h1>
        <h2 class="hero-subtitle">Aspiring Data Analyst | Turning Data into Insights</h2>
        <p class="hero-description">
            Passionate about transforming raw data into actionable business intelligence using 
            <strong>Python, SQL, Power BI, and Excel</strong>
        </p>
        <div class="status-badge">🚀 Available for Opportunities</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 4. MAIN TABS
# ==========================================
tab_home, tab_projects, tab_gallery, tab_datasets, tab_analyzer, tab_resume, tab_contact = st.tabs([
    "🏠 Home & About Me",
    "🎯 Projects Showcase", 
    "🖼️ All Images Gallery",
    "📊 Kaggle Datasets",
    "🧹 Cleaning & Visualize Your Data",
    "📄 Resume & Profile", 
    "📬 Contact Me"
])

# ------------------------------------------
# TAB 1: HOME & ABOUT ME
# ------------------------------------------
with tab_home:
    # About Section
    st.markdown("## 👤 About Me")
    
    col_about, col_metrics = st.columns([2, 1])
    
    with col_about:
        st.markdown("""
        I'm a **fresher Data Analyst** passionate about uncovering insights from data and 
        creating impactful visualizations. With hands-on experience in **Python, SQL, Excel, 
        and Power BI**, I specialize in:
        
        - 📊 **Data Cleaning & Transformation** - Turning messy data into structured datasets
        - 📈 **Dashboard Development** - Building interactive Power BI dashboards
        - 💡 **Statistical Analysis** - Finding patterns and trends
        - 🎯 **Business Intelligence** - Converting data into actionable recommendations
        
        🎓 **Background:** Self-taught through online courses and practical projects  
        🔍 **Currently:** Actively seeking entry-level Data Analyst opportunities  
        💪 **Strength:** Quick learner with strong problem-solving skills
        """)
    
    with col_metrics:
        st.markdown("### 📊 Quick Stats")
        st.metric("Projects Completed", "4+", delta="All Live")
        st.metric("Tools Mastered", "6", delta="Python, SQL, Excel...")
        st.metric("Learning Hours", "500+", delta="Self-paced")
        st.metric("GitHub Repos", "4+", delta="Public")
    
    st.markdown("---")
    
    # Skills Section
    st.markdown("## 🛠️ Technical Skills & Toolkit")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Data Analysis
        <span class="badge">Python (Pandas, NumPy)</span>
        <span class="badge">SQL (MySQL)</span>
        <span class="badge">Excel (Advanced)</span>
        <span class="badge">Statistics</span>
        <span class="badge">Data Cleaning</span>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        ### 📈 Visualization
        <span class="badge">Power BI</span>
        <span class="badge">DAX Queries</span>
        <span class="badge">Matplotlib</span>
        <span class="badge">Seaborn</span>
        <span class="badge">Plotly</span>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        ### 💼 Business Skills
        <span class="badge">Data Storytelling</span>
        <span class="badge">KPI Tracking</span>
        <span class="badge">Problem Solving</span>
        <span class="badge">Critical Thinking</span>
        <span class="badge">Communication</span>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # What I Bring Section
    st.markdown("## 💡 What I Bring to the Table")
    
    st.info("""
    ### End-to-End Data Analysis Pipeline
    
    **From Raw Data → Actionable Insights**
    
    1. 📥 **Data Collection** - Gathering data from multiple sources (CSV, SQL, JSON)
    2. 🧹 **Data Cleaning** - Handling missing values, duplicates, and inconsistencies
    3. 🔍 **Exploratory Analysis** - Understanding patterns and distributions
    4. 📊 **Visualization** - Creating compelling charts and dashboards
    5. 💡 **Insight Generation** - Translating findings into business recommendations
    
    ✨ **Focus:** Business-oriented solutions, not just technical exercises
    """)

# ------------------------------------------
# TAB 2: PROJECTS SHOWCASE
# ------------------------------------------
with tab_projects:
    st.markdown("## 🎯 Featured Projects Portfolio")
    st.markdown("""
    <p style='font-size: 1.1rem; color: #555;'>
    Click on any project to view detailed analysis, 
    code files, and visualizations.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    if os.path.exists(PROJECTS_DIR):
        project_folders = sorted([
            f for f in os.listdir(PROJECTS_DIR) 
            if os.path.isdir(os.path.join(PROJECTS_DIR, f))
        ])

        if not project_folders:
            st.warning("⚠️ No projects found.")
        else:
            for idx, proj_name in enumerate(project_folders, 1):
                folder_path = os.path.join(PROJECTS_DIR, proj_name)
                
                # ✅ SABHI FILES COLLECT KARO - SUBFOLDERS SE BHI
                all_files = []
                all_file_paths = {}
                
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        all_files.append(file)
                        all_file_paths[file] = full_path

                with st.expander(
                    f"📌 **Project {idx}: {proj_name}**", 
                    expanded=False
                ):
                    
                    # ============================
                    # 1. BUSINESS INSIGHTS
                    # ============================
                    st.markdown("### 🎯 Project Overview & Business Impact")
                    insights_files = [
                        "business_insights.txt", 
                        "insights.txt", 
                        "details.txt", 
                        "readme.txt",
                        "README.txt",
                        "README.md"
                    ]
                    found_insights = False

                    for txt_file in insights_files:
                        # Direct folder mein check karo
                        txt_path = os.path.join(folder_path, txt_file)
                        if os.path.exists(txt_path):
                            with open(txt_path, "r", encoding="utf-8") as f:
                                st.success(f.read())
                            found_insights = True
                            break
                        
                        # Subfolders mein bhi check karo
                        if txt_file in all_file_paths:
                            with open(
                                all_file_paths[txt_file], 
                                "r", 
                                encoding="utf-8"
                            ) as f:
                                st.success(f.read())
                            found_insights = True
                            break
                    
                    if not found_insights:
                        st.info(
                            "💡 Add a `business_insights.txt` "
                            "file to showcase key findings"
                        )

                    st.markdown("---")
                    
                    # ============================
                    # 2. TECH STACK BADGES
                    # ============================
                    st.markdown("### 🛠️ Technologies Used")
                    tech_used = []
                    for category, exts in CODE_EXTS.items():
                        if any(f.endswith(exts) for f in all_files):
                            tech_used.append(category)
                    
                    if tech_used:
                        tech_badges = " ".join([
                            f'<span class="badge">{tech}</span>' 
                            for tech in tech_used
                        ])
                        st.markdown(tech_badges, unsafe_allow_html=True)
                    else:
                        st.caption("No tech files detected")
                    
                    st.markdown("---")
                    
                    # ============================
                    # 3. ALL FILES - DOWNLOAD
                    # ============================
                    st.markdown("### 📂 Project Files & Code")
                    
                    found_files = False
                    file_cols = st.columns(4)
                    col_idx = 0

                    for category, exts in CODE_EXTS.items():
                        # Saari files match karo (subfolders se bhi)
                        matched_files = [
                            f for f in all_files 
                            if f.endswith(exts)
                        ]
                        
                        if matched_files:
                            found_files = True
                            with file_cols[col_idx % 4]:
                                st.markdown(f"**{category}**")
                                for fname in matched_files:
                                    fpath = all_file_paths[fname]
                                    with open(fpath, "rb") as fp:
                                        st.download_button(
                                            label=f"💾 {fname}",
                                            data=fp,
                                            file_name=fname,
                                            key=f"dl_{proj_name}_{fname}",
                                            use_container_width=True
                                        )
                            col_idx += 1
                    
                    if not found_files:
                        st.caption(
                            "No code files found "
                            "(.py, .sql, .pbix, .xlsx, .csv, .ipynb)"
                        )

                    st.markdown("---")
                    
                    # ============================
                    # 4. CSV DATA PREVIEW 
                    # ============================
                    import pandas as pd
                    
                    csv_files = [
                        f for f in all_files 
                        if f.endswith(('.csv', '.CSV'))
                    ]
                    
                    if csv_files:
                        st.markdown("### 📊 Dataset Preview")
                        
                        # Multiple CSV tabs banao
                        if len(csv_files) > 1:
                            csv_tabs = st.tabs(csv_files)
                            for csv_tab, csv_file in zip(
                                csv_tabs, csv_files
                            ):
                                with csv_tab:
                                    try:
                                        df = pd.read_csv(
                                            all_file_paths[csv_file]
                                        )
                                        st.markdown(
                                            f"**📋 {csv_file}** - "
                                            f"Shape: `{df.shape[0]} rows "
                                            f"× {df.shape[1]} columns`"
                                        )
                                        st.dataframe(
                                            df.head(10),
                                            use_container_width=True
                                        )
                                        
                                        # Stats bhi dikhao
                                        with st.expander(
                                            "📈 Data Statistics"
                                        ):
                                            st.dataframe(
                                                df.describe(),
                                                use_container_width=True
                                            )
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                        else:
                            # Single CSV
                            try:
                                df = pd.read_csv(
                                    all_file_paths[csv_files[0]]
                                )
                                st.markdown(
                                    f"**📋 {csv_files[0]}** - "
                                    f"Shape: `{df.shape[0]} rows "
                                    f"× {df.shape[1]} columns`"
                                )
                                st.dataframe(
                                    df.head(10),
                                    use_container_width=True
                                )
                                with st.expander("📈 Data Statistics"):
                                    st.dataframe(
                                        df.describe(),
                                        use_container_width=True
                                    )
                            except Exception as e:
                                st.error(f"Error loading CSV: {e}")
                    
                    st.markdown("---")
                    
                    # ============================
                    # 5. SCREENSHOTS
                    # ============================
                    st.markdown(
                        "### 📸 Dashboard Screenshots & Visualizations"
                    )
                    images = sorted([
                        f for f in all_files 
                        if f.endswith(IMAGE_EXTS)
                    ])

                    if images:
                        img_cols = st.columns(2)
                        for i, img_name in enumerate(images):
                            img_path = all_file_paths[img_name]
                            with img_cols[i % 2]:
                                st.image(
                                    img_path,
                                    caption=img_name,
                                    use_container_width=True
                                )
                    else:
                        st.caption("No screenshots available")
                    
                    # ============================
                    # 6. VIDEOS
                    # ============================
                    videos = sorted([
                        f for f in all_files 
                        if f.endswith(VIDEO_EXTS)
                    ])
                    if videos:
                        st.markdown("---")
                        st.markdown("### 🎥 Demo Videos")
                        for vid_name in videos:
                            st.video(all_file_paths[vid_name])
    else:
        st.error(
            "⚠️ 'projects' directory not found. "
            "Create it next to app.py"
        )
# ------------------------------------------
# TAB 3: GALLERY
# ------------------------------------------
# ------------------------------------------
# TAB 3: GALLERY (WITH FILTER & PERFECT ALIGNMENT)
# ------------------------------------------
with tab_gallery:
    st.markdown("## 🖼️ Complete Portfolio Gallery")
    st.write("All project visualizations and dashboards:")

    if os.path.exists(PROJECTS_DIR):
        all_gallery_images = []
        
        # ✅ os.walk() - Subfolders mein bhi dhundega
        for p_folder in os.listdir(PROJECTS_DIR):
            p_path = os.path.join(PROJECTS_DIR, p_folder)
            
            if os.path.isdir(p_path):
                # Subfolders ke andar bhi dhundega
                for root, dirs, files in os.walk(p_path):
                    for file in files:
                        if file.endswith(IMAGE_EXTS):
                            full_path = os.path.join(root, file)
                            all_gallery_images.append((
                                p_folder,  # Project name
                                file,       # Image name
                                full_path   # Full path
                            ))

        if all_gallery_images:
            # Project wise group karke dikhao
            st.markdown(f"**Total Images Found: {len(all_gallery_images)}**")
            st.markdown("---")
            
            # Project wise filter
            project_names = list(set([
                img[0] for img in all_gallery_images
            ]))
            
            # Filter buttons
            selected = st.selectbox(
                "🔍 Filter by Project:",
                ["All Projects"] + sorted(project_names)
            )
            
            # Filter images
            if selected == "All Projects":
                filtered_images = all_gallery_images
            else:
                filtered_images = [
                    img for img in all_gallery_images 
                    if img[0] == selected
                ]
            
            st.markdown(f"**Showing: {len(filtered_images)} images**")
            st.markdown("---")
            
            # 🟢 PERFECT GRID FIX (Row by Row)
            for i in range(0, len(filtered_images), 3):
                cols = st.columns(3) # Har nayi row ke liye 3 naye column
                for j in range(3):
                    if i + j < len(filtered_images):
                        proj, img_f, img_p = filtered_images[i + j]
                        with cols[j]:
                            try:
                                # Captions aur Image ko render kar rahe hain
                                st.image(
                                    img_p,
                                    caption=f"📁 {proj} | {img_f}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"❌ Cannot load: {img_f}")
        else:
            st.warning("""
            ⚠️ No images found in any project folder!
            
            **Fix:**
            - Add .png or .jpg files to your project folders
            - Check GitHub pe images upload hain ya nahi
            """)
    else:
        st.error("Projects directory not found!")

    
# ------------------------------------------
# TAB: KAGGLE DATASETS
# ------------------------------------------
with tab_datasets:

    st.markdown("## 📊 My Kaggle Datasets")
    st.markdown("""
    All datasets I have created and published 
    on Kaggle. Click the link to access directly.
    """)
    
    st.markdown("---")
    
    # ============================
    # DATASETS LIST
    # Sirf yahan apna data bharo!
    # ============================
    datasets = [
       {
        "category": "💰 Financial Fraud",
        "name": "Indian Financial Fraud Dataset",
        "description": "Comprehensive dataset of financial fraud cases in India. Contains transaction patterns, fraud indicators and customer data for fraud detection analysis.",
        "link": "https://www.kaggle.com/datasets/jatinkhandelwal112/indian-financial-fraud-dataset",
        "tags": ["Finance", "Fraud Detection", "Python", "ML"]
    },
    # Agle datasets yahan aayenge
]
        
       
        # Naye dataset add karte rehna bas yahan!
        # {
        #     "category": "Category Name",
        #     "name": "Dataset Name",
        #     "description": "Short description",
        #     "link": "Kaggle link",
        #     "tags": ["tag1", "tag2"]
        # },
    
    
    # ============================
    # DISPLAY EACH DATASET
    # ============================
    for dataset in datasets:
        with st.expander(
            f"{dataset['category']} | {dataset['name']}"
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {dataset['name']}")
                st.markdown(f"**Category:** {dataset['category']}")
                st.markdown(f"**Description:** {dataset['description']}")
                
                # Tags
                tags = " ".join([
                    f'<span class="badge">{tag}</span>' 
                    for tag in dataset['tags']
                ])
                st.markdown(tags, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 🔗 Access")
                st.markdown(f"""
                [![Kaggle Dataset](https://img.shields.io/badge/View_on_Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)]({dataset['link']})
                """)
    
    st.markdown("---")
    
    # Kaggle Profile Link
    st.markdown("""
    <div style='text-align: center; padding: 20px;
                background: #E3F2FD; border-radius: 10px;'>
        <h3>🏆 My Kaggle Profile</h3>
        <p>All datasets available here</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    [![Kaggle Profile](https://img.shields.io/badge/Visit_Kaggle_Profile-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/jatinkhandelwal112)
    """)

# ============================
# NEW TAB: CLEANING & VISUALIZE DATA
# ============================

with tab_analyzer:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    st.markdown("## 🧹 Cleaning & Visualize Your Data")
    st.markdown("""
    Upload CSV, Excel or JSON file for instant analysis.
    🔒 **Your data is NOT stored anywhere.**
    """)

    MAX_ROWS = 150000
    st.markdown("---")

    # FILE UPLOAD
    st.markdown("### 📁 Upload Your Files (Max 3)")
    col1, col2, col3 = st.columns(3)

    with col1:
        file1 = st.file_uploader(
            "📄 File 1 (Required)",
            type=['csv', 'xlsx', 'json'],
            key="analyzer_file1"
        )
    with col2:
        file2 = st.file_uploader(
            "📄 File 2 (Optional)",
            type=['csv', 'xlsx', 'json'],
            key="analyzer_file2"
        )
    with col3:
        file3 = st.file_uploader(
            "📄 File 3 (Optional)",
            type=['csv', 'xlsx', 'json'],
            key="analyzer_file3"
        )

    # LOAD FILE FUNCTION
    def load_analyzer_file(file):
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
                st.error(
                    f"⚠️ File too large! "
                    f"Max {MAX_ROWS:,} rows. "
                    f"Your file: {df.shape[0]:,} rows."
                )
                return None
            return df
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return None

    # LOAD FILES
    analyzer_dataframes = {}

    if file1:
        df1 = load_analyzer_file(file1)
        if df1 is not None:
            analyzer_dataframes[file1.name] = df1
            st.success(
                f"✅ {file1.name}: "
                f"{df1.shape[0]:,} rows × {df1.shape[1]} cols"
            )

    if file2:
        df2 = load_analyzer_file(file2)
        if df2 is not None:
            analyzer_dataframes[file2.name] = df2
            st.success(
                f"✅ {file2.name}: "
                f"{df2.shape[0]:,} rows × {df2.shape[1]} cols"
            )

    if file3:
        df3 = load_analyzer_file(file3)
        if df3 is not None:
            analyzer_dataframes[file3.name] = df3
            st.success(
                f"✅ {file3.name}: "
                f"{df3.shape[0]:,} rows × {df3.shape[1]} cols"
            )

    st.markdown("---")

    # JOIN SECTION
    if len(analyzer_dataframes) >= 2:
        st.markdown("### 🔗 Join Your Files (Optional)")
        file_names = list(analyzer_dataframes.keys())

        col_a, col_b = st.columns(2)
        with col_a:
            sel_f1 = st.selectbox(
                "First File:",
                file_names,
                key="join_f1"
            )
        with col_b:
            rem = [f for f in file_names if f != sel_f1]
            sel_f2 = st.selectbox(
                "Second File:",
                rem,
                key="join_f2"
            )

        col_c, col_d = st.columns(2)
        with col_c:
            jcol1 = st.selectbox(
                f"Join Column ({sel_f1}):",
                analyzer_dataframes[sel_f1].columns.tolist(),
                key="jcol1"
            )
        with col_d:
            jcol2 = st.selectbox(
                f"Join Column ({sel_f2}):",
                analyzer_dataframes[sel_f2].columns.tolist(),
                key="jcol2"
            )

        jtype = st.radio(
            "Join Type:",
            ["Inner Join","Left Join","Right Join","Outer Join"],
            horizontal=True,
            key="jtype"
        )

        jmap = {
            "Inner Join": "inner",
            "Left Join": "left",
            "Right Join": "right",
            "Outer Join": "outer"
        }

        if st.button("🔗 Perform Join", key="join_btn"):
            try:
                merged = pd.merge(
                    analyzer_dataframes[sel_f1],
                    analyzer_dataframes[sel_f2],
                    left_on=jcol1,
                    right_on=jcol2,
                    how=jmap[jtype]
                )
                st.session_state['merged_df'] = merged
                st.success(
                    f"✅ Join done! "
                    f"{merged.shape[0]:,} rows × "
                    f"{merged.shape[1]} cols"
                )
            except Exception as e:
                st.error(f"❌ Join failed: {e}")

        st.markdown("---")

    # MAIN ANALYSIS
    if analyzer_dataframes:
        st.markdown("### 📊 Select Dataset")

        options = list(analyzer_dataframes.keys())
        if 'merged_df' in st.session_state:
            options.append("🔗 Merged Data")

        selected = st.selectbox(
            "Choose dataset:",
            options,
            key="dataset_select"
        )

        if selected == "🔗 Merged Data":
            df = st.session_state['merged_df'].copy()
        else:
            df = analyzer_dataframes[selected].copy()

        # SESSION STATE MEIN SAVE
        st.session_state['current_df'] = df

        st.markdown("---")

        # ============================
        # SECTION 1: BASIC OVERVIEW
        # ============================
        st.markdown("## 📊 Basic Data Overview")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Rows", f"{df.shape[0]:,}")
        with m2:
            st.metric("Total Columns", df.shape[1])
        with m3:
            mem = df.memory_usage(deep=True).sum()/1024**2
            st.metric("Memory", f"{mem:.2f} MB")
        with m4:
            st.metric("Data Types", df.dtypes.nunique())

        t1, t2, t3, t4, t5 = st.tabs([
            "Head","Sample","Info","Columns","Describe"
        ])

        with t1:
            st.markdown("**df.head():**")
            st.dataframe(df.head(), use_container_width=True)

        with t2:
            st.markdown("**df.sample():**")
            st.dataframe(
                df.sample(min(5, df.shape[0])),
                use_container_width=True
            )

        with t3:
            st.markdown("**df.info():**")
            info_df = pd.DataFrame({
                'Column': df.columns,
                'Non-Null': df.count().values,
                'Dtype': df.dtypes.astype(str).values
            })
            st.dataframe(info_df, use_container_width=True)

        with t4:
            st.markdown("**df.columns:**")
            st.write(df.columns.tolist())

        with t5:
            st.markdown("**df.describe():**")
            st.dataframe(
                df.describe(),
                use_container_width=True
            )

        st.markdown("---")

        # ============================
        # SECTION 2: DATA QUALITY
        # ============================
        st.markdown("## 🔍 Data Quality Check")

        q1, q2 = st.columns(2)

        with q1:
            st.markdown("**Missing Values:**")
            miss = pd.DataFrame({
                'Column': df.columns,
                'Missing': df.isnull().sum().values,
                'Missing%': (
                    df.isnull().sum()/len(df)*100
                ).round(2).values
            })
            miss = miss[miss['Missing'] > 0]
            if not miss.empty:
                st.dataframe(miss, use_container_width=True)
            else:
                st.success("✅ No missing values!")

        with q2:
            st.markdown("**Duplicate Rows:**")
            dup = df.duplicated().sum()
            st.metric("Duplicates", f"{dup:,}")
            if dup > 0:
                st.warning(f"⚠️ {dup} duplicates found")
            else:
                st.success("✅ No duplicates!")

        st.markdown("---")

        # ============================
        # SECTION 3: DATA TYPE FIX
        # ============================
        st.markdown("## 🔧 Fix Data Types")

        d1, d2, d3 = st.columns(3)

        with d1:
            col_to_fix = st.selectbox(
                "Select Column:",
                df.columns.tolist(),
                key="dtype_col"
            )
        with d2:
            st.markdown(
                f"**Current:** `{str(df[col_to_fix].dtype)}`"
            )
            new_type = st.selectbox(
                "Convert To:",
                ["Integer","Float","String","Date"],
                key="new_dtype"
            )
        with d3:
            st.markdown("**Action:**")
            if st.button("🔄 Convert", key="convert_btn"):
                try:
                    if new_type == "Integer":
                        df[col_to_fix] = pd.to_numeric(
                            df[col_to_fix], errors='coerce'
                        ).astype('Int64')
                    elif new_type == "Float":
                        df[col_to_fix] = pd.to_numeric(
                            df[col_to_fix], errors='coerce'
                        )
                    elif new_type == "String":
                        df[col_to_fix] = df[col_to_fix].astype(str)
                    elif new_type == "Date":
                        df[col_to_fix] = pd.to_datetime(
                            df[col_to_fix], errors='coerce'
                        )
                    st.session_state['current_df'] = df
                    st.success(
                        f"✅ '{col_to_fix}' → {new_type}!"
                    )
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

        st.markdown("---")

        # ============================
        # SECTION 4: SMART DUPLICATE
        # ============================
        st.markdown("## 🗑️ Smart Duplicate Detection")

        st.info(
            "💡 Select ID column to exclude from "
            "duplicate check (like customer_id, emp_id)"
        )

        id_col = st.selectbox(
            "Select ID/Primary Key Column:",
            ["None"] + df.columns.tolist(),
            key="id_col"
        )

        if id_col != "None":
            check_cols = [c for c in df.columns if c != id_col]
        else:
            check_cols = df.columns.tolist()

        st.markdown(
            f"**Checking columns:** {', '.join(check_cols)}"
        )

        dup_mask = df.duplicated(subset=check_cols, keep=False)
        true_dups = df.duplicated(
            subset=check_cols, keep='first'
        ).sum()

        dc1, dc2 = st.columns(2)
        with dc1:
            st.metric("True Duplicates", true_dups)
        with dc2:
            if true_dups > 0:
                st.warning(f"⚠️ {true_dups} duplicates!")
            else:
                st.success("✅ No duplicates!")

        if true_dups > 0:
            if st.checkbox("👀 Show Duplicates", key="show_dup"):
                st.dataframe(
                    df[dup_mask].sort_values(by=check_cols),
                    use_container_width=True
                )

            if st.button(
                "🗑️ Remove Duplicates",
                key="rem_dup_btn"
            ):
                df = df.drop_duplicates(
                    subset=check_cols, keep='first'
                )
                st.session_state['current_df'] = df
                st.success(
                    f"✅ Removed! New: {df.shape[0]:,} rows"
                )

        st.markdown("---")

        # ============================
        # SECTION 5: VISUALIZATIONS
        # ============================
        df = st.session_state.get('current_df', df)

        st.markdown("## 📈 Visualizations")

        num_cols = df.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        cat_cols = df.select_dtypes(
            include=['object']
        ).columns.tolist()

        v1, v2, v3 = st.tabs([
            "📊 Numeric",
            "🎨 Categorical",
            "🔥 Correlation"
        ])

        with v1:
            if num_cols:
                sel_num = st.selectbox(
                    "Select Column:",
                    num_cols,
                    key="num_viz"
                )
                vc1, vc2 = st.columns(2)
                with vc1:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    df[sel_num].hist(
                        bins=30, ax=ax, color='#667eea'
                    )
                    ax.set_title(f'Distribution: {sel_num}')
                    st.pyplot(fig)
                    plt.close(fig)
                with vc2:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.boxplot(
                        y=df[sel_num], ax=ax, color='#764ba2'
                    )
                    ax.set_title(f'Box Plot: {sel_num}')
                    st.pyplot(fig)
                    plt.close(fig)
            else:
                st.info("No numeric columns found")

        with v2:
            if cat_cols:
                sel_cat = st.selectbox(
                    "Select Column:",
                    cat_cols,
                    key="cat_viz"
                )
                vc = df[sel_cat].value_counts().head(10)
                fig, ax = plt.subplots(figsize=(8, 5))
                vc.plot(kind='bar', ax=ax, color='#667eea')
                ax.set_title(f'Top 10: {sel_cat}')
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No categorical columns found")

        with v3:
            if len(num_cols) >= 2:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(
                    df[num_cols].corr(),
                    annot=True, fmt='.2f',
                    cmap='coolwarm', ax=ax
                )
                ax.set_title('Correlation Heatmap')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Need 2+ numeric columns")

        st.markdown("---")

        # ============================
        # SECTION 6: DOWNLOAD
        # ============================
        st.markdown("## 💾 Download Cleaned Data")
        st.info("🔒 Data NOT stored - Download now!")

        final_df = st.session_state.get('current_df', df)
        csv_out = final_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "📥 Download CSV",
            csv_out,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_btn"
        )

    else:
        st.info("👆 Upload at least one file to start!")
# ------------------------------------------
# TAB 4: RESUME
# ------------------------------------------
with tab_resume:
    st.markdown("## 📄 Resume & Professional Profile")
    
    col_r1, col_r2 = st.columns([2, 1])
    
    with col_r1:
        st.markdown("""
        ### Jatin Kumar
        **Aspiring Data Analyst**
        
        #### 🎓 Education
        
        **Master's Degree**
        - **Program:** MBA in Operation Management
        - **University:** Vivekananda Global University
        - **Status:** Pursuing
        
        **Bachelor's Degree**
        - **Program:** Bachelor of Computer Application
        - **University:** Sikkim Alpine University
        - **Year:** 2022-2025
        
        **Diploma**
        - **Program:** Diploma in Pharmacy
        - **University:** Apeejay Stya University
        - **Year:** 2020-2022
        
        #### 💼 Technical Expertise
        - **Languages:** Python, SQL
        - **Tools:** Power BI, Excel, Pandas, NumPy
        - **Databases:** MySQL
        - **Visualization:** Matplotlib, Seaborn, Plotly
        
        #### 🏆 Key Achievements
        - ✅ Completed 4+ end-to-end data analysis projects
        - ✅ Built interactive dashboards viewed by 100+ users
        - ✅ Self-taught Python and SQL through practical projects
        - ✅ Active contributor on GitHub and Kaggle
        """)
    
    with col_r2:
        st.markdown("### 📥 Download Options")
        
        resume_path = os.path.join(BASE_DIR, "resume.pdf")
        if os.path.exists(resume_path):
            with open(resume_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Resume (PDF)",
                    data=pdf_file,
                    file_name="Jatin Kumar Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            st.success("✅ Resume available for download")
        else:
            st.warning("💡 Add 'resume.pdf' to enable download")
        
        st.markdown("---")
        st.markdown("### 📊 Portfolio Stats")
        st.metric("Projects", "4+")
        st.metric("Code Files", "15+")
        st.metric("Visualizations", "20+")

# ------------------------------------------
# TAB 5: CONTACT
# ------------------------------------------
with tab_contact:
    st.markdown("## 📬 Let's Connect!")
    st.write("I'm actively looking for Data Analyst opportunities. Feel free to reach out!")
    
    st.markdown("---")
    
    # Social Cards
    st.markdown("### 🌐 Connect on Social Platforms")
    
    social_col1, social_col2, social_col3, social_col4 = st.columns(4)
    
    with social_col1:
        st.markdown("""
        <div class="social-card">
            <h2>📧</h2>
            <h4>Email</h4>
            <a href="mailto:Jating1416@gmail.com" target="_blank">Send Message</a>
        </div>
        """, unsafe_allow_html=True)
    
    with social_col2:
        st.markdown("""
        <div class="social-card">
            <h2>💼</h2>
            <h4>LinkedIn</h4>
            <a href="https://www.linkedin.com/in/jatin-kumar-5a46a720a/" target="_blank">Connect</a>
        </div>
        """, unsafe_allow_html=True)
    
    with social_col3:
        st.markdown("""
        <div class="social-card">
            <h2>🐙</h2>
            <h4>GitHub</h4>
            <a href="https://github.com/jating1416-debug" target="_blank">View Code</a>
        </div>
        """, unsafe_allow_html=True)
    
    with social_col4:
        st.markdown("""
        <div class="social-card">
            <h2 style="font-family: Arial; font-weight: bold;">K</h2>
            <h4>Kaggle</h4>
            <a href="https://www.kaggle.com/jatinkhandelwal112" target="_blank">Explore</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Contact Form
    st.markdown("### ✉️ Send Me a Message")
    
    with st.form("contact_form", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            name = st.text_input("Your Name *")
            email = st.text_input("Your Email *")
        
        with col_form2:
            subject = st.text_input("Subject")
            phone = st.text_input("Phone (Optional)")
        
        message = st.text_area("Your Message *", height=150)
        
        submitted = st.form_submit_button("📤 Send Message", use_container_width=True)
        
        if submitted:
            if name and email and message:
                st.success(f"✅ Thank you {name}! Your message has been received. I'll get back to you at {email} soon!")
            else:
                st.error("⚠️ Please fill in all required fields (*)")
    
    st.markdown("---")
    
    # Quick Info
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        ### 📍 Location
        India (Open to Remote)
        
        ### ⏰ Response Time
        Usually within 24 hours
        """)
    
    with col_info2:
        st.markdown("""
        ### 💼 Availability
        🟢 **Available for:**
        - Full-time positions
        - Internships
        - Work From Home
        
        """)

# ==========================================
# 5. FOOTER
# ==========================================
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3>Jatin Kumar - Data Analyst Portfolio</h3>
    <p>© 2026 All Rights Reserved</p>
    <p style="font-size: 0.9rem; color: #999;">
        📊 Turning Data into Decisions | 🚀 Always Learning | 💡 Problem Solver
    </p>
</div>
""", unsafe_allow_html=True)