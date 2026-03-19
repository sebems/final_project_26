import re
import pandas as pd
from helpers import *
from icecream import ic
import streamlit as st


def clean_main_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Dataframe column processing and cleanup
    # Credits
    df["Credits:"] = df["Credits:"].apply(lambda x: re.findall(r"\d+", x)[0])
    # When Offered
    df["When Offered:"] = df["When Offered:"].astype(str)
    df["When Offered:"] = df["When Offered:"].apply(lambda x: x.split(", "))
    df["Is Active"] = df["Is Active"].astype(bool)

    return df


def main():
    st.set_page_config(page_title="Course Catalog Data", layout="wide")

    with st.spinner("Loading data..."):
        main_df = pd.read_csv(
            open(MAIN_DATA_PATH, errors="replace"),
            dtype=PREP_COLS_AND_TYPES,
        )
        # Drop the columns we don't need and clean up the data in the columns we do need
        main_df = main_df[PREP_COLS]
        main_df = clean_main_dataframe(main_df)

        course_df = main_df[
            [
                "Course OID",
                "Course Type",
                "Prefix",
                "Code",
                "Name",
                "Credits:",
                "When Offered:",
                "Is Active",
                "Program Usage",
                "Program OIDs",
            ]
        ]
        course_df["Is Active"] = course_df["Is Active"].astype(bool)

        program_df = pd.read_csv(open(PROGRAM_DATA_PATH, errors="replace"))
        program_df["Is Active"] = program_df["Is Active"].astype(bool)
        program_df = program_df[PREP_PROGRAM_COLS]

    with st.sidebar:
        st.title("Filters")

        active_filter = st.checkbox("Show only active items", value=True)

        programs = {
            id: name
            for id, name in zip(
                program_df["Program OID"].unique(), program_df["Program Name"].unique()
            )
        }

        term_selection = st.selectbox("Term Filter", options=["FA", "SP", "SU"])

        with st.form("program_filter_form"):
            program_selection = st.selectbox(
                "Filter by Program",
                options=list(programs.keys()),
                format_func=lambda x: programs[x],
            )
            submitted = st.form_submit_button("Apply Program Filter")

    if active_filter:
        course_df = course_df[course_df["Is Active"]]  # Filter out inactive courses
        program_df = program_df[program_df["Is Active"]]  # Filter out inactive programs

    # TODO - Add filters for programs and let the filter function on the course dataframe
    # make the filter a selectbox with the unique values from the "Program OID" column in the program dataframe. Then filter the course dataframe based on the selected program OID.
    filtered_df = course_df[
        course_df["Program OIDs"].str.contains(str(program_selection), na=False)
    ]

    # TODO - Add a filter for the "When Offered:" column in the course dataframe.
    # This should be a multiselect with the unique values from the "When Offered:" column in the course dataframe.
    # Then filter the course dataframe based on the selected values.

    filtered_df = filtered_df[
        filtered_df["When Offered:"].apply(lambda x: term_selection in x)
    ]

    # TODO - Add a filter for the "Credits:" column in the course dataframe. This should be a selectbox with the unique values from the "Credits:" column in the course dataframe. Then filter the course dataframe based on the selected value.

    # TODO - Add an accordian for each course that shows the course description and prerequisites when clicked. This should be done using the "Course OID" column in the course dataframe to match the course description and prerequisites from the main dataframe.

    # TODO - Core Requirements Section
    # Foundations
    # Competencies and Skills
    # Knowledge and Understanding
    # Cross-Disciplinary Integration

    # TODO - Knowledge and Understanding Calculator
    # TODO - Scale up the K&U calculator to be a general calculator for core requirements
    # Filter rows where the selection is part of the Program OIDs string
    # Convert the ID to a string so .contains() can search for it in the text column

    st.dataframe(
        filtered_df,
        width="stretch",
        column_order=(
            "Course OID",
            "Course Type",
            "Prefix",
            "Code",
            "Name",
            "Credits:",
            "When Offered:",
            "Program Usage",
        ),
    )


if __name__ == "__main__":
    main()
