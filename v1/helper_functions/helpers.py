import re
import pandas as pd

PREP_COLS = [
    "Entity Type",
    "Entity OID",
    "Entity Name",
    "Course OID",
    "Course Type",
    "Prefix",
    "Code",
    "Name",
    "Credits:",
    "When Offered:",
    "Description (Rendered no HTML)",
    "Prerequisite(s): (Rendered no HTML)",
    "Corequisite(s): (Rendered no HTML)",
    "Is Active",
    "Program Usage",
    "Program OIDs",
]

PREP_COLS_AND_TYPES = {
    "Entity Type": str,
    "Entity OID": str,
    "Entity Name": str,
    "Course OID": str,
    "Course Type": str,
    "Prefix": str,
    "Code": str,
    "Name": str,
    "Credits:": str,
    "When Offered:": str,
    "Description (Rendered no HTML)": str,
    "Prerequisite(s): (Rendered no HTML)": str,
    "Corequisite(s): (Rendered no HTML)": str,
    "Is Active": bool,
    "Program Usage": str,
    "Program OIDs": str,
}

PREP_PROGRAM_COLS = [
    "Entity Name",
    "Program OID",
    "Program Type",
    "Degree Type",
    "Program Code",
    "Program Name",
    "Program Description",
    "Structure",
    "Is Active",
]

PREP_PROGRAM_COLS_AND_TYPES = {
    "Entity Name": str,
    "Program OID": str,
    "Program Type": str,
    "Degree Type": str,
    "Program Code": str,
    "Program Name": str,
    "Program Description": str,
    "Structure": str,
    "Is Active": bool,
}

MAIN_DATA_PATH = "../data/Catalog Draft 26-27.csv"
PROGRAM_DATA_PATH = "../data/Programs 26-27.csv"
CORE_STRUCT_DATA_PATH = "../data/core_struct_data.txt"
CORE_JSON_PATH = "../data/core_struct_data_parsed.json"
CORE_JSON_DATAFRAME_PATH = "../data/core_program_dataframe.csv"


def clean_main_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Dataframe column processing and cleanup
    # Credits
    df["Credits:"] = df["Credits:"].apply(lambda x: re.findall(r"\d+", x)[0])
    # When Offered
    df["When Offered:"] = df["When Offered:"].astype(str)
    df["When Offered:"] = df["When Offered:"].apply(lambda x: x.split(", "))
    df["Is Active"] = df["Is Active"].astype(bool)

    return df
