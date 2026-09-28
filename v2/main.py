import re
import pandas as pd
import streamlit as st

# --- PAGE SETUP ---
st.set_page_config(page_title="Academic Dashboard", page_icon="🎓", layout="wide")

with st.sidebar:
    st.header("Upload Transcript")
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = (
        pd.read_csv(uploaded_file)
        if uploaded_file.name.endswith(".csv")
        else pd.read_excel(uploaded_file)
    )
else:
    st.info("👋 Welcome! Please upload your transcript to view your dashboard.")
    # Create a placeholder dataframe with the expected columns
    df = pd.DataFrame(
        columns=[
            "Registration",
            "Registration Hours",
            "Grade",
            "Eligibility Rules",
            "Course ID",
            "Course Title",
            "isTransferCredit",
            "isCompleted",
        ]
    )
    st.stop()

K_U_CORE_SECTIONS = pd.DataFrame([
    {"name": "World Languages II", "min": 0, "max": 4, "order": 1},
    {"name": "Arts, Oral Rhetoric, and Visual Rhetoric", "min": 2, "max": 6, "order": 2},
    {"name": "Humanities", "min": 2, "max": 6, "order": 3},
    {"name": "Mathematical Sciences", "min": 0, "max": 4, "order": 4},
    {"name": "Natural Science", "min": 0, "max": 6, "order": 5},
    {"name": "Social and Behavioral Sciences", "min": 2, "max": 6, "order": 6},
])

def clean_eligibility_rules(input_string):
    output = str(input_string).replace("REQ: K&U - ", "")
    output = re.sub(r"[,;]\s*[\d-]+\s+hours.*", "", output, flags=re.DOTALL)
    return output.strip()

# --- DATA CLEANING ---
df["Course ID"] = df["Registration"].apply(
    lambda x: x.split(" - ")[0] if " - " in str(x) else x
)
df["Course Title"] = df["Registration"].apply(
    lambda x: x.split(" - ")[-1] if " - " in str(x) else ""
)
df["isTransferCredit"] = df["Course Title"].apply(
    lambda x: True if "(Transfer Credit)" in str(x) else False
)
df["isCompleted"] = df["Grade"].apply(
    lambda x: True if pd.notna(x) and str(x).strip() else False
)
df["Core Section"] = df["Eligibility Rules"].apply(clean_eligibility_rules)
df["Registration Hours"] = pd.to_numeric(
    df["Registration Hours"], errors="coerce"
).fillna(0)

df = df.dropna(subset=["Registration Hours", "Course ID", "Course Title"])

# Group the dataframe by
aggregated_df = df.groupby(["Core Section", "Course ID"]).agg(
    {
        "Registration Hours": lambda x: ", ".join(x.dropna().astype(int).astype(str)),
        "Grade": lambda x: ", ".join(x.dropna().astype(str)),
        "isCompleted": lambda x: ", ".join(
            ["✅" if status else "⚠️" for status in x]
        ),        
    }
).reset_index()

# Add a row for sections that have no courses
for sec in K_U_CORE_SECTIONS.itertuples():
    if sec.name not in aggregated_df["Core Section"].values:
        aggregated_df = pd.concat(
            [
                aggregated_df,
                pd.DataFrame(
                    {
                        "Core Section": [sec.name],
                        "Course ID": [""],
                        "Registration Hours": [""],
                        "Grade": [""],
                        "isCompleted": [""],
                    }
                ),
            ],
            ignore_index=True,
        )
        
# Add a minimum and maximum hours column for each core section
aggregated_df = aggregated_df.merge(
    K_U_CORE_SECTIONS, how="left", left_on="Core Section", right_on="name"
).drop(columns=["name"])

# Sort the aggregated dataframe by the order of core sections
aggregated_df = aggregated_df.sort_values(by=["order", "Core Section", "Course ID"]).reset_index(drop=True)

# Convert the "Registration Hours" column to numeric for calculations
aggregated_df["Registration Hours"] = pd.to_numeric(aggregated_df["Registration Hours"], errors="coerce").fillna(0)

# Convert the "isCompleted" column to boolean for calculations
aggregated_df["isCompleted"] = aggregated_df["isCompleted"].apply(lambda x: True if "✅" in str(x) else False)

# --- UI RENDER ---
st.title("🎓 Knowledge & Understanding Tracker")
st.markdown(
    "Students must complete at least **26 hours** from a minimum of 5 categories."
)

with st.expander("K&U Core Section Rules", expanded=False):
    st.subheader("Knowledge and Understanding (K&U)")

    st.markdown("""
    Students must complete at least *26 hours* from a minimum of 5 of the following 6 categories, with a minimum of 2 hours from 3 categories as specified below:

    - World Languages II, 0-4 hours
    - Arts, Oral Rhetoric, and Visual Rhetoric, 2-6 hours: up to 4 hours in any one discipline
    - Humanities, 2-6 hours: up to 4 hours in any one discipline
    - Mathematical Sciences, 0-4 hours
    - Natural Sciences, 0-6 hours; up to 4 hours in any one discipline
    - Social and Behavioral Sciences, 2-6 hours: up to 4 hours in any one discipline
    """)
    
    with st.expander("Core Section Minimum and Maximum Hours", expanded=True):
        st.dataframe(K_U_CORE_SECTIONS[["name", "min", "max"]].rename(
            columns={"name": "Core Section", "min": "Minimum Hours", "max": "Maximum Hours"}
        ), hide_index=True, use_container_width=True)

# Course Status Legend
st.markdown("""
**Course Status Legend:**
🟢 `Institutional Credit` | 🔵 `Transfer / AP Credit` | ⚪ `In-Progress` | 🔴 `Not Completed`
""")

# Interactive Tabs
tab_dashboard, tab_details, tab_raw_data = st.tabs(
    ["📊 Visual Dashboard", "📑 Detailed Course Breakdown", "📋 Raw Transcript Data"]
)

with tab_dashboard:
    col_metrics, col_breakdown = st.columns([1, 3])

    with col_metrics:
        # High-Level Metrics
        comp_total_capped = df[df["isCompleted"]]["Registration Hours"].sum()
        proj_total_capped = df["Registration Hours"].sum()
        in_progress_total = abs(proj_total_capped - comp_total_capped)

        st.metric(label="Completed Credits", value=f"{comp_total_capped:g} hrs")
        st.metric(
            label="Projected Total",
            value=f"{proj_total_capped:g} hrs",
            delta=f"{in_progress_total:g} hrs In-Progress",
        )

        st.divider()
        expand_all = st.toggle("Expand All Sections", value=False)

    with col_breakdown:
        st.subheader("Category Breakdown")

        for sec in K_U_CORE_SECTIONS["name"].unique():
            name = sec
            s_min = aggregated_df[aggregated_df["Core Section"] == name]["min"].iloc[0]
            s_max = aggregated_df[aggregated_df["Core Section"] == name]["max"].iloc[0]

            # Completed Filling logic
            sec_df = df[df["Core Section"] == name]
            
            earned = sec_df[sec_df["isCompleted"] == True]["Registration Hours"].sum()
            pending = sec_df[sec_df["isCompleted"] == False]["Registration Hours"].sum()
            
            total_sec = earned + pending
            capped_total_sec = min(total_sec, s_max)
            excess = max(0, total_sec - s_max)
            
            is_completed = earned >= s_min
            
            # Determine status wording
            if is_completed:
                status_text = "✅ Minimum met"
            elif total_sec >= s_min:
                status_text = "🔄 In-progress to meet min"
            else:
                status_text = f"🔴 Needs {s_min - total_sec:g} more hrs"

            progress_val = float(min(total_sec / s_max, 1.0)) if s_max > 0 else 0.0

            # Expander Layout
            with st.expander(name, expanded=expand_all):
                col_chart, col_courses = st.columns([2, 3])

                with col_chart:
                    st.markdown(f"#### {name}")
                    st.caption(f"Target: **{s_min:g} - {s_max:g} hrs** | {status_text}")

                    # Visual Progress Bar
                    st.progress(progress_val)

                    if excess > 0:
                        st.markdown(
                            f"**{capped_total_sec:g} hrs applied** ({earned:g} earned, {pending:g} pending)"
                        )
                        st.markdown(f"🚨 *{excess:g} excess hrs not counted*")
                    else:
                        st.markdown(
                            f"**{capped_total_sec:g} hrs logged** ({earned:g} earned, {pending:g} pending)"
                        )

                with col_courses:
                    # Completed course population logic
                    if sec_df.empty:
                        st.markdown("*No courses logged for this section.*")
                    else:
                        for _, row in sec_df.iterrows():
                            c_id = row["Course ID"]
                            c_title = row["Course Title"]
                            c_hrs = row["Registration Hours"]
                            
                            if row["isCompleted"]:
                                if row.get("isTransferCredit", False):
                                    st.info(f"🔵 **{c_id}**: {c_title} *({c_hrs:g} hrs)*")
                                else:
                                    st.success(f"🟢 **{c_id}**: {c_title} *({c_hrs:g} hrs)*")
                            else:
                                st.warning(f"⚪ **{c_id}**: {c_title} *({c_hrs:g} hrs)*")

with tab_details:
    st.write("#### Detailed Course Breakdown by Core Section")
     
    for sec in aggregated_df["Core Section"].unique():
        section_name = sec

        st.markdown(f"**{section_name}**")

        placeholder_df = aggregated_df[aggregated_df["Core Section"] == section_name][
            ["Course ID", "Registration Hours", "Grade", "isCompleted"]
        ]      
        
        st.dataframe(placeholder_df, hide_index=True, use_container_width=True)


with tab_raw_data:
    st.subheader("Raw Transcript Data", divider=True)
    st.dataframe(df, use_container_width=True, hide_index=True)