import pandas as pd
import streamlit as st


# 1. OPTIMIZATION: Cache data loading
@st.cache_data
def load_core_data(file_path):
    return pd.read_csv(file_path)


def calculate_progress(registered_codes, core_df):
    """
    Optimized progress calculation using vectorization.
    Only counts credits for courses that are in the Core Program.
    """
    # Filter core data to only courses that the student has registered for
    completed_courses_df = core_df[core_df["course_code"].isin(registered_codes)]

    # Group by sections to get total credits per section
    # Note: If a course appears in multiple sections, this counts it for all of them
    section_totals = completed_courses_df.groupby("sections")["credits"].sum().to_dict()

    return section_totals


def main():
    st.set_page_config(page_title="Core Program Progress Tracker", layout="wide")
    st.title("🎓 Core Program Progress Tracker")

    # Load data
    core_struct_df = load_core_data("./data/core_program_dataframe.csv")

    # Sidebar for transcript upload
    with st.sidebar:
        st.header("Transcript Upload")
        file_uploaded = st.file_uploader(
            "Upload Transcript (CSV or XLSX)", type=["csv", "xlsx"]
        )

    registered_codes = []
    if file_uploaded:
        if file_uploaded.name.endswith(".csv"):
            main_df = pd.read_csv(file_uploaded)
        else:
            main_df = pd.read_excel(file_uploaded)

        if "Registration" in main_df.columns:
            # Extract code (e.g., "CORE 100" from "CORE 100 - Community...")
            registered_codes = (
                main_df["Registration"].str.split(" - ").str[0].str.strip().tolist()
            )
    else:
        st.info("Please upload a transcript to see your progress.")

    # --- KNOWLEDGE AND UNDERSTANDING (K&U) LOGIC ---
    ku_mask = core_struct_df["categories"] == "KNOWLEDGE AND UNDERSTANDING"
    ku_df = core_struct_df[ku_mask]

    # Get unique K&U sections and their requirements
    ku_requirements = ku_df[
        ["sections", "section_credit_min", "section_credit_max"]
    ].drop_duplicates()

    ku_sections_list = ku_requirements["sections"].tolist()

    # Calculate completed credits per section
    completed_section_data = calculate_progress(registered_codes, ku_df)

    # Display Global K&U Progress
    total_ku_credits = sum(completed_section_data.values())
    target_total = 26

    st.header("Knowledge and Understanding Summary")
    col_total, col_prog = st.columns([1, 3])
    with col_total:
        st.metric("Total K&U Credits", f"{total_ku_credits} / {target_total}")
    with col_prog:
        st.write("Overall Progress")
        st.progress(min(total_ku_credits / target_total, 1.0))

    st.divider()

    # --- INDIVIDUAL SECTION METRICS ---
    st.subheader("Section Breakdown")

    # Create rows of metrics (3 columns per row)
    cols = st.columns(3)
    for i, row in ku_requirements.iterrows():
        section_name = row["sections"]
        earned = completed_section_data.get(section_name, 0)
        s_min = row["section_credit_min"]
        s_max = row["section_credit_max"]

        # Determine status color/label
        if earned >= s_min and earned > 0:
            status = "✅ Met" if earned <= s_max else "⚠️ Max Reached"
        elif s_min == 0:
            status = "Optional"
        else:
            status = f"Need {int(s_min - earned)} more"

        with cols[i % 3]:
            st.metric(
                label=section_name,
                value=f"{int(earned)} / {int(s_max)} hrs",
                delta=status,
                delta_color="normal" if earned >= s_min else "inverse",
                border=True,
            )


if __name__ == "__main__":
    main()
