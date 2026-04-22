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
    
@st.cache_data
def load_catalog_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Catalog data file not found at {file_path}")
        return pd.DataFrame()

def calculate_progress(registered_codes_and_grades, core_df, catalog_df):
    """
    Returns dictionaries for completed credits, IP credits, and a list of IP codes.
    """
    if not registered_codes_and_grades or not registered_codes_and_grades[0]:
        return {}, {}, []

    codes, grades = registered_codes_and_grades

    completed_codes = []
    ip_codes = []

    for code, grade in zip(codes, grades):
        # Identify In-Progress: if grade is NaN or an empty string
        if pd.isna(grade) or str(grade).strip() == "":
            ip_codes.append(code)
        else:
            completed_codes.append(code)

    # Calculate completed totals per section
    completed_df = core_df[core_df["course_code"].isin(completed_codes)]

    completed_codes = completed_df["course_code"].tolist()  # Update completed codes based on actual matches

    comp_totals = completed_df.groupby("sections")["credits"].sum().to_dict()

    # Calculate IP totals per section
    ip_df = core_df[core_df["course_code"].isin(ip_codes)]
    ip_totals = ip_df.groupby("sections")["credits"].sum().to_dict()

    # Get co-reqs and overrides for IP courses (if needed for future logic)
    remaining_codes = list(set(codes) - set(completed_codes) - set(ip_codes))    # Debug: Show matched completed codes
    rem_code_credits = [] # Debug: Store credits for unmatched codes

    # TODO: add remaining credits to comp_totals or ip_totals based on the presence of grades

    # Differentiate between overrides and co-reqs (may not be needed for current logic, but useful for future enhancements)
    override_codes = []     
    coreq_codes = []        

    return comp_totals, ip_totals, ip_codes, remaining_codes


def main():
    st.set_page_config(page_title="Core Program Progress Tracker", layout="wide")
    st.title("🎓 Core Program Progress Tracker")

    # Load Core and Catalog data
    core_struct_df = load_core_data("./data/core_program_dataframe.csv")
    if core_struct_df.empty:
        st.stop()

    catalog_df = load_catalog_data("./data/Catalog Draft 26-27.csv")
    if catalog_df.empty:
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
            codes = main_df["Registration"].str.split(" - ").str[0].str.strip().tolist()
            grades = main_df["Grade"].tolist()
            registered_codes_and_grades = (codes, grades)
        else:
            st.error("Missing 'Registration' or 'Grade' columns.")

    # --- LOGIC ---
    # Filter for K&U category
    ku_df = core_struct_df[
        core_struct_df["categories"] == "KNOWLEDGE AND UNDERSTANDING"
    ]
    ku_requirements = ku_df[
        ["sections", "section_credit_min", "section_credit_max"]
    ].drop_duplicates()

    # Get segmented data
    comp_data, ip_data, ip_codes, rem_codes = calculate_progress(
        registered_codes_and_grades, ku_df, catalog_df
    )

    # calculate_overrides_and_coreqs(registered_codes_and_grades, catalog_df)

    # --- SUMMARY ---
    total_completed = sum(comp_data.values())
    total_ip = sum(ip_data.values())
    projected_total = total_completed + total_ip
    TARGET_TOTAL = 26

    st.header("Knowledge and Understanding Summary")

    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Completed Credits", f"{total_completed} hrs")
    # Show IP as a 'delta' to highlight projected growth
    c2.metric(
        "Projected Total",
        f"{projected_total} hrs",
        delta=f"{total_ip} credits In-Progress",
    )

    with c3:
        st.write("Projected Degree Progress")
        progress_val = (
            min(projected_total / TARGET_TOTAL, 1.0) if TARGET_TOTAL > 0 else 0
        )
        st.progress(progress_val)

    st.divider()

    # --- SECTION BREAKDOWN ---
    st.subheader("Section Breakdown (Including In-Progress)")
    for _, row in ku_requirements.iterrows():
        name = row["sections"]
        s_min = row["section_credit_min"]
        s_max = row["section_credit_max"]

        earned = comp_data.get(name, 0)
        pending = ip_data.get(name, 0)
        combined = earned + pending

        # Color Logic based on projected success (Combined credits)
        if (combined >= s_min) and (pending == 0):
            if combined == 0:  # check if the section is optional
                status = "Optional"
                color = "off"
            else:
                status = "Met" if combined <= s_max else "⚠️ Max Reached"
                color = "normal"
        elif (combined >= s_min) and (pending > 0):
            status = "⚠️ Projected"
            color = "yellow"
        else:
            status = f"Need {int(s_min - combined)} more"
            color = "inverse"

        # Expandable section details
        with st.expander(f"{name} :blue-badge[:material/star: Min: {int(s_min)}]"):
            col_met, col_details = st.columns([1, 3])

            col_met.metric(
                label="Completed + In Progress",
                value=f"{int(combined)} / {int(s_max)} hrs",
                delta=status,
                delta_color=color,
            )

            with col_details:
                section_courses = ku_df[ku_df["sections"] == name]

                # Show Completed Courses
                comp_mask = section_courses["course_code"].isin(
                    registered_codes_and_grades[0]
                ) & ~section_courses["course_code"].isin(ip_codes)
                comp_list = section_courses[comp_mask]

                if not comp_list.empty:
                    st.markdown("**Eligible Completed Courses:**")
                    for _, c in comp_list.iterrows():
                        st.success(f"{c['course_code']} ({c['credits']} hrs)")

                # Show In Progress Courses
                ip_list = section_courses[section_courses["course_code"].isin(ip_codes)]
                if not ip_list.empty:
                    st.markdown("**Current In-Progress Courses:**")
                    for _, c in ip_list.iterrows():
                        st.warning(f"🕒 {c['course_code']} ({c['credits']} hrs)")

                if comp_list.empty and ip_list.empty:
                    st.info("No courses registered in this section.")


if __name__ == "__main__":
    main()
