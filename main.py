import pandas as pd
import streamlit as st

# 1. OPTIMIZATION: Cache data loading
@st.cache_data
def load_core_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Core data file not found at {file_path}")
        return pd.DataFrame()

def calculate_progress(registered_codes_and_grades, core_df):
    """
    Optimized progress calculation using vectorization.
    """
    # If no data is uploaded yet, return empty results
    if not registered_codes_and_grades or not registered_codes_and_grades[0]:
        return {}

    codes, grades = registered_codes_and_grades

    # Filter core data to only courses that the student has registered for
    # AND ensure they have a grade (filtering out empty/NaN grades)
    completed_codes = [code for code, grade in zip(codes, grades) if pd.notnull(grade) and str(grade).strip() != ""]
    
    completed_courses_df = core_df[core_df["course_code"].isin(completed_codes)]

    # Group by sections to get total credits per section
    section_totals = completed_courses_df.groupby("sections")["credits"].sum().to_dict()

    return section_totals

def main():
    st.set_page_config(page_title="Core Program Progress Tracker", layout="wide")
    st.title("🎓 Core Program Progress Tracker")

    # Load data - Ensure this file exists in your directory
    core_struct_df = load_core_data("./data/core_program_dataframe.csv")
    
    if core_struct_df.empty:
        st.stop()

    # Sidebar for transcript upload
    with st.sidebar:
        st.header("Academic Progress Upload")
        file_uploaded = st.file_uploader(
            "Upload Transcript (CSV or XLSX)", type=["csv", "xlsx"]
        )

    registered_codes_and_grades = ([], [])
    
    if file_uploaded:
        if file_uploaded.name.endswith(".csv"):
            main_df = pd.read_csv(file_uploaded)
        else:
            main_df = pd.read_excel(file_uploaded)

        if "Registration" in main_df.columns and "Grade" in main_df.columns:
            # Extract code (e.g., "CORE 100" from "CORE 100 - Community...")
            codes = main_df["Registration"].str.split(" - ").str[0].str.strip().tolist()
            grades = main_df["Grade"].tolist()
            registered_codes_and_grades = (codes, grades)
        else:
            st.error("Uploaded file must contain 'Registration' and 'Grade' columns.")
    else:
        st.info("Please upload a progress report to see your progress.")

    # --- KNOWLEDGE AND UNDERSTANDING (K&U) LOGIC ---
    ku_mask = core_struct_df["categories"] == "KNOWLEDGE AND UNDERSTANDING"
    ku_df = core_struct_df[ku_mask]

    # Get unique K&U sections and their requirements
    ku_requirements = ku_df[
        ["sections", "section_credit_min", "section_credit_max"]
    ].drop_duplicates()

    # Calculate completed credits per section
    completed_section_data = calculate_progress(registered_codes_and_grades, ku_df)

    # Display Global K&U Progress
    total_ku_credits = sum(completed_section_data.values())
    TARGET_TOTAL = 26

    st.header("Knowledge and Understanding Summary")
    col_total, col_prog = st.columns([1, 3])
    with col_total:
        st.metric("Total K&U Credits", f"{total_ku_credits} / {TARGET_TOTAL} hrs")
    with col_prog:
        st.write("Overall Progress")
        progress_val = min(total_ku_credits / TARGET_TOTAL, 1.0) if TARGET_TOTAL > 0 else 0
        st.progress(progress_val)

    st.divider()

    # --- INDIVIDUAL SECTION METRICS ---
    st.subheader("Section Breakdown")

    for _, row in ku_requirements.iterrows():
        section_name = row["sections"]
        earned = completed_section_data.get(section_name, 0)
        s_min = row["section_credit_min"]
        s_max = row["section_credit_max"]

        # Logic for status
        if earned >= s_min and earned > 0:
            status = "✅ Met" if earned <= s_max else "⚠️ Max Reached"
            color = "normal"
        elif s_min == 0:
            status = "Optional"
            color = "off"
        else:
            status = f"Need {int(s_min - earned)} more"
            color = "inverse"

        with st.expander(label=f"{section_name} ({int(earned)}/{int(s_max)} hrs)", expanded=False):
            cols = st.columns([1, 3])
            
            with cols[0]:
                st.metric(
                    label="Status",
                    value=f"{int(earned)} hrs",
                    delta=status,
                    delta_color=color
                )
            
            with cols[1]:
                # Show courses contributing to this section
                courses_in_section = ku_df[ku_df["sections"] == section_name]
                completed_codes = registered_codes_and_grades[0]
                
                # Check which courses from the master list are in the student's upload
                mask = courses_in_section["course_code"].isin(completed_codes)
                completed_courses = courses_in_section[mask]

                if not completed_courses.empty:
                    st.markdown("**Completed Courses:**")
                    for _, course in completed_courses.iterrows():
                        st.success(f"**{course['course_code']}**: {course['credits']} hrs")
                else:
                    st.info("No completed courses in this section yet.")

if __name__ == "__main__":
    main()