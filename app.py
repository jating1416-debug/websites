
import os
import streamlit as st
from PIL import Image

# ==========================================
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="Jatin Kumar | Data Analyst Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
tab_home, tab_projects, tab_gallery, tab_resume, tab_contact = st.tabs([
    "🏠 Home & About Me",
    "🎯 Projects Showcase", 
    "🖼️ All Images Gallery", 
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
    Click on any project to view detailed analysis, code files, and visualizations. 
    All projects demonstrate real-world data analysis scenarios.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    if os.path.exists(PROJECTS_DIR):
        project_folders = sorted([
            f for f in os.listdir(PROJECTS_DIR) 
            if os.path.isdir(os.path.join(PROJECTS_DIR, f))
        ])

        if not project_folders:
            st.warning("⚠️ No projects found in 'projects' folder.")
        else:
            for idx, proj_name in enumerate(project_folders, 1):
                folder_path = os.path.join(PROJECTS_DIR, proj_name)
                all_files = os.listdir(folder_path)

                with st.expander(f"📌 **Project {idx}: {proj_name}**", expanded=False):
                    
                    # Business Insights
                    st.markdown("### 🎯 Project Overview & Business Impact")
                    insights_files = ["business_insights.txt", "insights.txt", "details.txt", "readme.txt"]
                    found_insights = False

                    for txt_file in insights_files:
                        txt_path = os.path.join(folder_path, txt_file)
                        if os.path.exists(txt_path):
                            with open(txt_path, "r", encoding="utf-8") as f:
                                st.success(f.read())
                            found_insights = True
                            break
                    
                    if not found_insights:
                        st.info("💡 Add a `business_insights.txt` file to showcase key findings and business impact")

                    st.markdown("---")
                    
                    # Tech Stack
                    st.markdown("### 🛠️ Technologies Used")
                    tech_used = []
                    for category, exts in CODE_EXTS.items():
                        if any(f.endswith(exts) for f in all_files):
                            tech_used.append(category)
                    
                    if tech_used:
                        tech_badges = " ".join([f'<span class="badge">{tech}</span>' for tech in tech_used])
                        st.markdown(tech_badges, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Source Files
                    st.markdown("### 📂 Project Files & Code")
                    file_cols = st.columns(4)
                    col_idx = 0
                    found_files = False

                    for category, exts in CODE_EXTS.items():
                        matched_files = [f for f in all_files if f.endswith(exts)]
                        if matched_files:
                            found_files = True
                            with file_cols[col_idx % 4]:
                                st.markdown(f"**{category}**")
                                for fname in matched_files:
                                    fpath = os.path.join(folder_path, fname)
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
                        st.caption("No downloadable code files in this project")

                    st.markdown("---")
                    
                    # Screenshots
                    st.markdown("### 📸 Dashboard Screenshots & Visualizations")
                    images = sorted([f for f in all_files if f.endswith(IMAGE_EXTS)])

                    if images:
                        img_cols = st.columns(2)
                        for idx, img_name in enumerate(images):
                            img_path = os.path.join(folder_path, img_name)
                            with img_cols[idx % 2]:
                                st.image(img_path, caption=img_name, use_container_width=True)
                    else:
                        st.caption("No visualization screenshots available")
                    
                    # Videos
                    videos = sorted([f for f in all_files if f.endswith(VIDEO_EXTS)])
                    if videos:
                        st.markdown("---")
                        st.markdown("### 🎥 Dashboard Demo Videos")
                        for vid_name in videos:
                            vid_path = os.path.join(folder_path, vid_name)
                            st.video(vid_path)
    else:
        st.error("⚠️ 'projects' directory not found. Create it in the same folder as app.py")

# ------------------------------------------
# TAB 3: GALLERY
# ------------------------------------------
with tab_gallery:
    st.markdown("## 🖼️ Complete Portfolio Gallery")
    st.write("All project visualizations and dashboards in one place:")

    if os.path.exists(PROJECTS_DIR):
        all_gallery_images = []
        for p_folder in os.listdir(PROJECTS_DIR):
            p_path = os.path.join(PROJECTS_DIR, p_folder)
            if os.path.isdir(p_path):
                for file in os.listdir(p_path):
                    if file.endswith(IMAGE_EXTS):
                        all_gallery_images.append((p_folder, file, os.path.join(p_path, file)))

        if all_gallery_images:
            gal_cols = st.columns(3)
            for idx, (proj, img_f, img_p) in enumerate(all_gallery_images):
                with gal_cols[idx % 3]:
                    st.image(img_p, caption=f"📁 {proj} | {img_f}", use_container_width=True)
        else:
            st.info("No project images found yet. Add screenshots to your project folders!")

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