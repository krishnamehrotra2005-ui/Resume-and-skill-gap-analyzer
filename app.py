import streamlit as st
import pdfplumber
import json
import re
import pandas as pd

from src.skills import extra_skills

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# =====================================
# TITLE
# =====================================

st.title("📄 Resume Analyzer")
st.markdown(
    "Upload your resume and discover your strongest job matches."
)

# =====================================
# LOAD DATA
# =====================================

with open("data/processed/role_skills.json", "r") as f:
    role_skills = json.load(f)

# =====================================
# ROLE DESCRIPTIONS
# =====================================

role_descriptions = {

    "Machine Learning Engineer":
    "Build, train, deploy and optimize machine learning models for real-world applications.",

    "AI Engineer":
    "Develop AI-powered systems using machine learning, deep learning and generative AI technologies.",

    "Data Engineer":
    "Design and maintain data pipelines, databases and large-scale data processing systems.",

    "Data Scientist":
    "Analyze complex datasets, build predictive models and generate data-driven insights.",

    "Data Analyst":
    "Clean, analyze and visualize data to support business decisions and reporting.",

    "Analytics Engineer":
    "Bridge data engineering and analytics by transforming raw data into reliable business datasets.",

    "Backend Developer":
    "Develop server-side applications, APIs and databases that power web and software systems.",

    "Mlops Engineer":
    "Deploy, monitor and maintain machine learning models and infrastructure in production environments.",

    "Python Developer":
    "Build software applications, automation scripts and backend systems using Python.",

    "Business Analyst":
    "Analyze business requirements, identify problems and recommend data-driven solutions.",

    "Bi Analyst":
    "Create dashboards, reports and business intelligence solutions to support decision-making.",

    "Computer Vision Engineer":
    "Develop image processing and computer vision systems for object detection, recognition and analysis.",

    "Software Engineer":
    "Design, develop, test and maintain software applications and systems.",

    "Nlp Engineer":
    "Build natural language processing systems for text analysis, chatbots and language understanding."
}

# =====================================
# SKILL DATABASE
# =====================================

all_skills = set()

for skills in role_skills.values():
    all_skills.update(skills)

all_skills.update(extra_skills)

all_skills = {
    skill.lower()
    for skill in all_skills
}

# =====================================
# FUNCTIONS
# =====================================

def extract_resume_text(pdf_file):

    text = ""

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_skills_from_resume(text, skill_list):

    text = text.lower()

    found_skills = []

    for skill in skill_list:

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):

            found_skills.append(skill)

    return sorted(found_skills)


def match_score(user_skills, role, role_skills):

    required_skills = role_skills[role]

    matched = 0

    for skill in required_skills:

        if skill.lower() in user_skills:

            matched += 1

    return round(
        (matched / len(required_skills)) * 100,
        2
    )


def skill_gap(user_skills, role, role_skills):

    required_skills = role_skills[role]

    missing = []

    for skill in required_skills:

        if skill.lower() not in user_skills:

            missing.append(skill)

    return missing


def matched_skills(user_skills, role, role_skills):

    required_skills = role_skills[role]

    matched = []

    for skill in required_skills:

        if skill.lower() in user_skills:

            matched.append(skill)

    return matched


# =====================================
# FILE UPLOAD
# =====================================

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

# =====================================
# MAIN APP
# =====================================

if uploaded_file:

    resume_text = extract_resume_text(
        uploaded_file
    )

    user_skills = extract_skills_from_resume(
        resume_text,
        all_skills
    )

    # =====================================
    # ROLE SCORES
    # =====================================

    role_scores = {}

    for role in role_skills:

        role_scores[role] = match_score(
            user_skills,
            role,
            role_skills
        )

    sorted_roles = sorted(
        role_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    best_role = sorted_roles[0][0]
    best_score = sorted_roles[0][1]

    # =====================================
    # SIDEBAR
    # =====================================

    with st.sidebar:

        st.header("🎯 Role Analysis")

        selected_role = st.selectbox(
            "Choose Role",
            list(role_skills.keys())
        )

    selected_score = match_score(
        user_skills,
        selected_role,
        role_skills
    )

    missing_skills = skill_gap(
        user_skills,
        selected_role,
        role_skills
    )

    matched = matched_skills(
        user_skills,
        selected_role,
        role_skills
    )

    # =====================================
    # METRICS
    # =====================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Skills Found",
            len(user_skills)
        )

    with col2:

        st.metric(
            "Best Role",
            best_role
        )

    with col3:

        st.metric(
            "Best Score",
            f"{best_score}%"
        )

    with col4:

        st.metric(
            "Coverage",
            f"{len(matched)}/{len(role_skills[selected_role])}"
        )

    st.divider()

    # =====================================
    # SKILLS
    # =====================================

    st.subheader("🛠 Extracted Skills")

    st.write(
        " | ".join(
            [f"`{skill}`" for skill in user_skills]
        )
    )

    st.divider()

    # =====================================
    # TOP MATCHING ROLES
    # =====================================

    st.subheader("🎯 Top Matching Roles")

    top_roles_df = pd.DataFrame(
        sorted_roles[:5],
        columns=["Role", "Score (%)"]
    )

    st.dataframe(
        top_roles_df,
        use_container_width=True
    )

    st.divider()

    # =====================================
    # ROLE ANALYSIS
    # =====================================

    st.subheader(
        f"📊 Analysis for {selected_role}"
    )

    st.info(
        role_descriptions.get(
            selected_role,
            "Role description not available."
        )
    )

    st.progress(
        selected_score / 100
    )

    if selected_score >= 70:

        st.success(
            f"Match Score: {selected_score}%"
        )

    elif selected_score >= 40:

        st.warning(
            f"Match Score: {selected_score}%"
        )

    else:

        st.error(
            f"Match Score: {selected_score}%"
        )

    st.divider()

    # =====================================
    # MATCHED SKILLS
    # =====================================

    st.subheader("✅ Matched Skills")

    if matched:

        for skill in matched:

            st.success(skill)

    else:

        st.warning(
            "No matching skills found."
        )

    # =====================================
    # MISSING SKILLS
    # =====================================

    st.subheader("📌 Missing Skills")

    if missing_skills:

        for skill in missing_skills:

            st.error(skill)

    else:

        st.success(
            "No Missing Skills Found!"
        )

    st.divider()

    # =====================================
    # DOWNLOAD REPORT
    # =====================================

    report = f"""
Resume Analysis Report

Role: {selected_role}

Match Score: {selected_score}%

Matched Skills:
{chr(10).join(matched)}

Missing Skills:
{chr(10).join(missing_skills)}
"""

    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name="resume_analysis.txt",
        mime="text/plain"
    )