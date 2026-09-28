import re
import pandas as pd
import streamlit as st

# --- DATA LOADING ---


@st.cache_data
def load_core_data(file_path: str) -> pd.DataFrame:
    """
    Loads and caches the core program requirements.
    Caches the data to ensure the UI remains responsive during re-runs.
    """
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Core data file not found at {file_path}")
        return pd.DataFrame()


# --- LOGIC ENGINE ---


def calculate_progress(
    registered_courses: pd.DataFrame,
    core_df: pd.DataFrame,
):
    """
    Analyzes student transcript against core requirements.
    Filters out NaN values and organizes credits into categorical totals.
    """
    if registered_courses.empty:
        return {}, {}, [], {}, {}

    # 1. STANDARDIZATION & CLEANING
    registered_courses = registered_courses.dropna(subset=["code"])
    core_df["course_code"] = core_df["course_code"].astype(str).str.strip().str.upper()
    registered_courses["code"] = (
        registered_courses["code"].astype(str).str.strip().str.upper()
    )

    core_lookup = (
        core_df.drop_duplicates(subset=["course_code"])
        .set_index("course_code")
        .to_dict("index")
    )
    valid_sections = core_df["sections"].unique()

    comp_totals, ip_totals, rem_totals = {}, {}, {}
    rem_course_details = {}
    ip_codes = []

    # 2. PROCESSING LOOP
    for _, row in registered_courses.iterrows():
        code = row["code"]
        if code == "NAN" or not code:
            continue

        grade = row["grade"]
        raw_sec_list = row["section"]
        credit_val = float(row["credits"])

        is_completed = not (pd.isna(grade) or str(grade).strip() == "")

        section_name = (
            raw_sec_list[0]
            if isinstance(raw_sec_list, list) and raw_sec_list
            else str(raw_sec_list)
        )

        if code in core_lookup:
            section = core_lookup[code]["sections"]
            if is_completed:
                comp_totals[section] = comp_totals.get(section, 0.0) + credit_val
            else:
                ip_totals[section] = ip_totals.get(section, 0.0) + credit_val
                ip_codes.append(code)
        else:
            # Fuzzy match for credits not explicitly in the Core CSV
            matched_section = "Unassigned"
            for valid in valid_sections:
                if (
                    section_name.strip().lower() in valid.lower()
                    or valid.lower() in section_name.strip().lower()
                ):
                    matched_section = valid
                    break

            rem_totals[matched_section] = (
                rem_totals.get(matched_section, 0.0) + credit_val
            )
            if matched_section not in rem_course_details:
                rem_course_details[matched_section] = []

            rem_course_details[matched_section].append(
                {"code": code, "credits": credit_val}
            )

    return comp_totals, ip_totals, ip_codes, rem_totals, rem_course_details


# --- HELPER FUNCTION ---
def is_transfer_or_ap(grade_val) -> bool:
    """Evaluates if a grade denotes a transfer or AP credit."""
    grade_str = str(grade_val).strip().upper()
    # Matches common transfer notation (T, TA, TB, TR, CR, AP)
    return grade_str.startswith("T") or grade_str in ["CR", "AP"]


# --- UI LAYER ---


def main():
    st.set_page_config(page_title="Core Program Progress Tracker", layout="wide")
    st.title("🎓 Core Program Progress Tracker")

    # Load Core Structure
    core_struct_df = load_core_data("./data/core_program_dataframe.csv")
    if core_struct_df.empty:
        st.stop()

    core_struct_df = core_struct_df[core_struct_df["course_code"].notna()]

    if "all_expanded" not in st.session_state:
        st.session_state.all_expanded = False

    with st.sidebar:
        st.header("Academic Progress Upload")
        file_uploaded = st.file_uploader(
            "Upload Transcript (CSV or XLSX)", type=["csv", "xlsx"]
        )
        st.divider()
        if st.button("**Expand Sections**", type="primary"):
            st.session_state.all_expanded = not st.session_state.all_expanded

    registrations_df = pd.DataFrame(
        {"code": [], "grade": [], "section": [], "credits": []}
    )

    if file_uploaded:
        main_df = (
            pd.read_csv(file_uploaded)
            if file_uploaded.name.endswith(".csv")
            else pd.read_excel(file_uploaded)
        )

        required_cols = [
            "Registration",
            "Grade",
            "Registration Hours",
            "Eligibility Rules",
        ]
        if all(col in main_df.columns for col in required_cols):
            codes = main_df["Registration"].str.split(" - ").str[0].str.strip().tolist()
            grades = main_df["Grade"].tolist()
            credits_list = (
                pd.to_numeric(main_df["Registration Hours"], errors="coerce")
                .fillna(0)
                .tolist()
            )
            sections = (
                main_df["Eligibility Rules"]
                .apply(lambda rule: re.findall(r"-\s+(.*?),\s+\d+", str(rule)))
                .to_list()
            )

            registrations_df = pd.DataFrame(
                {
                    "code": codes,
                    "grade": grades,
                    "section": sections,
                    "credits": credits_list,
                }
            )
        else:
            st.error(f"Missing required columns: {', '.join(required_cols)}")

    ku_df = core_struct_df[
        core_struct_df["categories"] == "KNOWLEDGE AND UNDERSTANDING"
    ]
    ku_requirements = ku_df[
        ["sections", "section_credit_min", "section_credit_max"]
    ].drop_duplicates()

    comp_data, ip_data, ip_codes, rem_totals, rem_course_details = calculate_progress(
        registrations_df, ku_df
    )

    # --- ADVANCED CREDIT CAPPING LOGIC ---
    total_completed = 0.0
    total_ip = 0.0
    total_remaining_adj = sum(rem_totals.values())

    for _, row in ku_requirements.iterrows():
        name = row["sections"]
        s_max = float(row["section_credit_max"])

        earned = comp_data.get(name, 0.0)
        pending = ip_data.get(name, 0.0)

        capped_earned = min(earned, s_max)
        total_completed += capped_earned

        space_left = s_max - capped_earned
        capped_pending = min(pending, max(0.0, space_left))
        total_ip += capped_pending

    TARGET_TOTAL = 26.0
    adj_total = total_completed + min(total_ip, TARGET_TOTAL - total_completed)

    st.header("Knowledge and Understanding Summary")
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Completed Credits", f"{total_completed + total_remaining_adj:g} hrs")
    c2.metric(
        "Projected Total",
        f"{adj_total:g} hrs",
        delta=f"{total_ip:g} hrs In-Progress",
    )
    with c3:
        st.write("Projected Degree Progress")
        st.progress(min(adj_total / TARGET_TOTAL, 1.0) if TARGET_TOTAL > 0 else 0)

    st.divider()

    st.subheader("Section Breakdown (Including In-Progress & Remaining)")

    for _, row in ku_requirements.iterrows():
        name = row["sections"]
        s_min, s_max = float(row["section_credit_min"]), float(
            row["section_credit_max"]
        )
        earned, remaining, pending = (
            comp_data.get(name, 0),
            rem_totals.get(name, 0),
            ip_data.get(name, 0),
        )
        combined = earned + remaining + pending
        excess = combined - s_max if combined > s_max else 0

        combined_for_badge = min(combined, s_max)

        if (combined_for_badge >= s_min) and (pending == 0):
            status, color = (
                ("Met", "normal") if combined_for_badge > 0 else ("Optional", "off")
            )
        elif (combined_for_badge >= s_min) and (pending > 0):
            status, color = "⚠️ Projected", "yellow"
        else:
            status, color = f"Need {s_min - combined_for_badge:g} more", "inverse"

        with st.expander(
            f"{name} :blue-badge[:material/star: Min: {s_min:g}]",
            expanded=st.session_state.all_expanded,
        ):
            col_met, col_details = st.columns([1, 3])
            col_met.metric(
                label="Completed + In-Progress",
                value=f"{combined_for_badge:g} / {s_max:g} hrs",
                delta=status,
                delta_color=color,
            )
            if excess > 0:
                col_met.divider()
                col_met.write(f"***Excess Credits: {excess:g}***")

            with col_details:
                section_courses = ku_df[ku_df["sections"] == name]

                comp_mask = section_courses["course_code"].isin(
                    registrations_df["code"]
                ) & ~section_courses["course_code"].isin(ip_codes)

                if any(comp_mask):
                    st.markdown("**Completed Courses:**")
                    for _, c in section_courses[comp_mask].iterrows():
                        trans_data = registrations_df.loc[
                            registrations_df["code"] == c["course_code"]
                        ]
                        cred_to_show = (
                            trans_data["credits"].values[0]
                            if not trans_data.empty
                            else 0
                        )
                        grade_val = (
                            trans_data["grade"].values[0]
                            if not trans_data.empty
                            else ""
                        )

                        # Apply Transfer/AP Badge dynamically
                        badge = (
                            " :violet-background[Transfer / AP]"
                            if is_transfer_or_ap(grade_val)
                            else ""
                        )
                        st.success(
                            f"✅ **{c['course_code']}** ({cred_to_show:g} hrs){badge}"
                        )

                if name in rem_course_details:
                    st.markdown("**Overrides / Co-Requisites:**")
                    for item in rem_course_details[name]:
                        if pd.notna(item["code"]) and item["code"] != "NAN":
                            st.info(f"📖 **{item['code']}** ({item['credits']:g} hrs)")

                ip_list = section_courses[section_courses["course_code"].isin(ip_codes)]
                if not ip_list.empty:
                    st.markdown("**In-Progress Courses:**")
                    for _, c in ip_list.iterrows():
                        trans_cred = registrations_df.loc[
                            registrations_df["code"] == c["course_code"], "credits"
                        ].values
                        cred_to_show = trans_cred[0] if len(trans_cred) > 0 else 0
                        st.warning(f"🕒 **{c['course_code']}** ({cred_to_show:g} hrs)")

                if (
                    not any(comp_mask)
                    and name not in rem_course_details
                    and ip_list.empty
                ):
                    st.info("No courses registered in this section.")


if __name__ == "__main__":
    main()
