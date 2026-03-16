from helpers import *
import pandas as pd
import icecream as ic
import re


def main():
    df = pd.read_csv(
        open("./Catalog Draft 26-27.csv", errors="replace"),
        dtype=PREP_COLS_AND_TYPES,
    )
    df = df[PREP_COLS]

    # Dataframe column processing and cleanup
    # Credits
    df["Credits:"] = df["Credits:"].apply(lambda x: re.findall(r"\d+", x)[0])
    # When Offered
    df["When Offered:"] = df["When Offered:"].astype(str)
    df["When Offered:"] = df["When Offered:"].apply(lambda x: x.split(", "))

    # TODO: create a sub dataframe for the programs and their OIDs
    program_df = df[["Program Usage", "Program OIDs"]]

    # df.head().to_csv("dump.csv", index=False)


if __name__ == "__main__":
    main()
