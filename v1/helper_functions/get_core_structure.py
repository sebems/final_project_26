import pandas as pd
from helper_functions.helpers import CORE_STRUCT_DATA_PATH


def main():

    program_df = pd.read_csv("./data/Programs 26-27.csv")  # Read in the program data
    # print(program_df.columns)

    # Filter the DataFrame to only include rows where "Program Name" is "Core Program"
    core_program_df = program_df[program_df["Program Name"] == "Core Program"]
    core_struct_data = pd.DataFrame(core_program_df["Structure"])

    # Print the Core Program structures to a text file for further analysis and processing
    print(
        core_struct_data.to_csv(index=False, header=False),
        file=open(CORE_STRUCT_DATA_PATH, "w"),
        flush=True,
    )


if __name__ == "__main__":
    main()
