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

    with st.sidebar:
        st.title("Filters")

        active_filter = st.checkbox("Show only active items", value=True)

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
        ]
    ]
    course_df["Is Active"] = course_df["Is Active"].astype(bool)

    program_df = pd.read_csv(open(PROGRAM_DATA_PATH, errors="replace"))
    program_df["Is Active"] = program_df["Is Active"].astype(bool)
    program_df = program_df[PREP_PROGRAM_COLS]

    if active_filter:
        course_df = course_df[course_df["Is Active"]]  # Filter out inactive courses
        program_df = program_df[program_df["Is Active"]]  # Filter out inactive programs

    # st.table(course_df)
    st.dataframe(program_df)


if __name__ == "__main__":
    main()
