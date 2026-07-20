import os
import streamlit as st
from PIL import Image

# ==========================================
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="Jatin Kumar | Data Analyst",
    page_icon="📊",
    layout="wide"
)

# Custom Styling for modern look
st.markdown("""
    <style>
    .main-title { font-size: 2.3rem; font-weight: 700; color: #1E88E5; }
    .sub-title { font-size: 1.2rem; color: #555555; }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px;
        background-color: #E3F2FD;
        color: #0D47A1;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    /* Style for the expandable projects to look like cards */
    .st-expander {
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        background-color: #FAFAFA;
    }
    </style>
""", unsafe_allow_html=True)

# Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

# File extensions grouping# File extensions grouping (GIFs & Videos Added)
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG', '.gif', '.GIF')
VIDEO_EXTS = ('.mp4', '.mov', '.webm', '.MP4')
CODE_EXTS = {
    'Python 🐍': ('.py', '.ipynb'),
    'SQL Database 💾': ('.sql',),
    'Excel / Data 📊': ('.xlsx', '.csv'),
    'Power BI Report 📈': ('.pbix',)
}

# ==========================================
# 2. HERO BANNER SECTION (THE SUPER TOP!)
# ==========================================
# Look for the specific banner image in the current directory
banner_filename = "ChatGPT Image Jul 10, 2026, 09_40_34 AM.png"
banner_path = os.path.join(BASE_DIR, banner_filename)

if os.path.exists(banner_path):
    banner_image = Image.open(banner_path)
    # The banner should span the full width
    st.image(banner_image, caption="Jatin Kumar | Aspiring Data Analyst", use_container_width=True)
else:
    # Fallback header if the banner isn't found
    st.markdown('<div class="main-title">Jatin Kumar | Aspiring Data Analyst</div>', unsafe_allow_html=True)
    st.info(f"ℹ️ Place the banner file `{banner_filename}` in the same folder as `app.py` for the full professional look!")

st.markdown("---")

# ==========================================
# 3. MAIN TABS (HOME, PROJECTS, GALLERY, RESUME, CONTACT)
# ==========================================
tab_home, tab_projects, tab_gallery, tab_resume, tab_contact = st.tabs([
    "🏠 Home & About Me",
    "🎯 Projects Showcase", 
    "🖼️ All Images Gallery", 
    "📄 Resume & Profile", 
    "📬 Contact Me"
])

# ------------------------------------------
# TAB 0: HOME & ABOUT ME (Structured Intro)
# ------------------------------------------
with tab_home:
    col_about, col_skills = st.columns([2, 1])

    with col_about:
        st.subheader("👨‍💻 Jatin Kumar")
        # --- BAS IS WRITE BLOCK KO BADALNA HAI ---
        st.write("""
        ### What I Bring to the Table
        
        I focus on converting raw, unstructured data into simple, actionable visual dashboards and clean database architectures. 
        
        * 📊 **End-to-End Pipeline:** From raw CSVs/SQL dumps to refined Power BI reports.
        * 🎯 **Business Focused:** KPI tracking, trend detection, and performance benchmarking.
        * ⚡ **Clean & Efficient:** Writing optimized SQL queries and modular Python scripts for data transformation.
        
        *Currently looking for entry-level Data Analyst / Business Analyst opportunities.*
        """)
        
    with col_skills:
        st.subheader("🛠️ Technical Skills Toolkit")
        st.markdown("""
        **Core Tools:**  
        <span class="badge">📊 Microsoft Excel (Pivot Tables, VLOOKUP)</span>
        <span class="badge">💾 MySQL (Queries, Joins, Aggregations)</span>  
        <span class="badge">🐍 Python (Pandas, NumPy, Matplotlib, Seaborn</span>
        <span class="badge">📈 Power BI (Modeling, Dashboards,DAX,Measures)</span>
        <br><br>
        **Competencies:**  
        <span class="badge">✓ Data Cleaning & Prep</span>
        <span class="badge">✓ Exploratory  Data Analysis (EDA)</span>
        <span class="badge">✓ Visualization & Reporting</span>
        <span class="badge">✓ Statistical Analysis</span>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 1: PROJECTS SHOWCASE (FOLDER READ)
# ------------------------------------------
with tab_projects:
    st.subheader("🎯 Project Portfolio ")
    st.write("Click on any project title below to expand its details, files (Python/SQL/Excel/PowerBI/txt), and screenshots.")

    if os.path.exists(PROJECTS_DIR):
        # Read sub-folders dynamically
        project_folders = sorted(list(set([
            f for f in os.listdir(PROJECTS_DIR) 
            if os.path.isdir(os.path.join(PROJECTS_DIR, f))
        ])))

        if not project_folders:
            st.warning("⚠️ 'projects' folder is empty or not found.")
        else:
            # Line-wise Expandable Cards for each project
            for proj_name in project_folders:
                folder_path = os.path.join(PROJECTS_DIR, proj_name)
                all_files = os.listdir(folder_path)

                with st.expander(f"📌 **Project: {proj_name}**", expanded=False):
                    
                    # 1. READ BUSINESS INSIGHTS & OBJECTIVES (.txt files)
                    insights_files = ["business_insights.txt", "insights.txt", "details.txt", "readme.txt"]
                    found_insights = False

                    for txt_file in insights_files:
                        txt_path = os.path.join(folder_path, txt_file)
                        if os.path.exists(txt_path):
                            with open(txt_path, "r", encoding="utf-8") as f:
                                st.success(f"💡 **Business Insights & Project Details:**\n\n{f.read()}")
                            found_insights = True
                            break # Pehli mili file read karke stop ho jayega
                    
                    if not found_insights:
                        st.caption("ℹ️ *Add a `business_insights.txt` file in this project folder to show key findings here.*")

                    # 2. CATEGORIZE & SHOW FILES (Python, SQL, Excel, Power BI)
                    st.markdown("#### 📂 Source Code & Data Files")
                    found_files = False
                    
                    file_cols = st.columns(4)
                    col_idx = 0

                    for category, exts in CODE_EXTS.items():
                        matched_files = [f for f in all_files if f.endswith(exts)]
                        if matched_files:
                            found_files = True
                            with file_cols[col_idx % 4]:
                                st.markdown(f"**{category}**")
                                for fname in matched_files:
                                    fpath = os.path.join(folder_path, fname)
                                    # Create a separate download button for each file
                                    with open(fpath, "rb") as fp:
                                        st.download_button(
                                            label=f"💾 {fname}",
                                            data=fp,
                                            file_name=fname,
                                            key=f"dl_{proj_name}_{fname}"
                                        )
                            col_idx += 1
                    
                    if not found_files:
                        st.write("No script files (.py, .sql, .pbix, .xlsx) found in this folder.")

                    # 3. DISPLAY PROJECT SCREENSHOTS
                    st.markdown("---")
                    st.markdown("#### 📸 Visualizations & Dashboard Screenshots")
                    images = sorted([f for f in all_files if f.endswith(IMAGE_EXTS)])

                    if images:
                        # Display images in a clean grid
                        img_cols = st.columns(2)  
                        for idx, img_name in enumerate(images):
                            img_path = os.path.join(folder_path, img_name)
                            with img_cols[idx % 2]:
                                st.image(img_path, caption=img_name, use_container_width=True)
                    else:
                        st.write("No images (.png, .jpg) found in this folder.")
    else:
        st.error("⚠️ 'projects' directory missing. Please create it next to app.py.")

                                  # 4. DISPLAY INTERACTIVE DEMOS / VIDEOS
    videos = sorted([f for f in all_files if f.endswith(VIDEO_EXTS)])
    if videos:
                        st.markdown("---")
                        st.markdown("#### 🎥 Dashboard Demo Videos")
                        for vid_name in videos:
                            vid_path = os.path.join(folder_path, vid_name)
                            st.video(vid_path)

           

# ------------------------------------------
# TAB 2: SEPARATE ALL IMAGES GALLERY
# ------------------------------------------
with tab_gallery:
    st.subheader("🖼️ Full Portfolio Image Gallery")
    st.write("All visualizations and screenshots from all projects, aggregated for easy browsing:")

    if os.path.exists(PROJECTS_DIR):
        all_gallery_images = []
        for p_folder in os.listdir(PROJECTS_DIR):
            p_path = os.path.join(PROJECTS_DIR, p_folder)
            if os.path.isdir(p_path):
                for file in os.listdir(p_path):
                    if file.endswith(IMAGE_EXTS):
                        all_gallery_images.append((p_folder, file, os.path.join(p_path, file)))

        if all_gallery_images:
            gal_cols = st.columns(3)  # 3 Column Gallery Grid
            for idx, (proj, img_f, img_p) in enumerate(all_gallery_images):
                with gal_cols[idx % 3]:
                    st.image(img_p, caption=f"📁 {proj} | {img_f}", use_container_width=True)
        else:
            st.info("No project images found.")

# ------------------------------------------
# TAB 3: RESUME SECTION
# ------------------------------------------
with tab_resume:
    st.subheader("📄 Resume & Education Profile")
    st.write("Entry-level Data Analyst passionate about practical problem solving.")

    # Check if resume PDF exists in base dir
    resume_path = os.path.join(BASE_DIR, "resume.pdf")
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download My Resume (PDF)",
                data=pdf_file,
                file_name="Jatin_Kumar_Resume.pdf",
                mime="application/pdf"
            )
    else:
        st.info("ℹ️ Place your `resume.pdf` file in the same folder as `app.py` for a download button.")

# ------------------------------------------
# TAB 4: CONTACT ME
# ------------------------------------------
with tab_contact:
    st.subheader("📬 Get in Touch")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write("### Connect With Me")
        st.write("📧 **Email:** [your.email@example.com](mailto:your.email@example.com)")
        st.write("🔗 **LinkedIn:** [linkedin.com/in/yourprofile](https://linkedin.com)")
        st.write("🐙 **GitHub:** [github.com/jating1416-debug](https://github.com/jating1416-debug)")
        st.write(" K  **Kaggle:** [kaggle.com/your Profile](https://www.kaggle.com/jatinkhandelwal112)")
    with col_c2:
        st.write("### Leave a Message")
        st.text_input("Name")
        st.text_input("Email")
        st.text_area("Message")
        if st.button("Submit Message"):
            st.success("Thank you! I will get back to you soon.")