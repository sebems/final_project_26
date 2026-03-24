import json
import pandas as pd
# import streamlit as st

def main():
    # st.set_page_config(page_title="Core Requirements", layout="wide")

    # Create a DataFrame for Cores
    core_df = pd.read_json("./data/core_struct_data_parsed.json", orient="records",
                           columns=["categories", "sections", "subsections", "course_codes", "course_names"])
    print(core_df.head())  # Debug: Check the structure of the DataFrame

    # Append course code and credit hours to the DataFrame

    # Streamlit UI

if __name__ == "__main__":
    main()