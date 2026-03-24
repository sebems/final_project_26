import re
import pandas as pd


DEBUG = False


def sanitize(input_file_name, output_file_name):
    # Read structure data file
    with open(input_file_name, "r") as infile, open(output_file_name, "w") as outfile:
        for line in infile:
            # Remove Quotation Marks and Whitespace
            clean_line = line.replace('"', "").rstrip()
            clean_line = clean_line.replace("* \t ", "* ")

            # Remove Empty lines
            if clean_line.strip():
                # Write cleaned line to output file
                outfile.write(clean_line + "\n")


def main():
    sanitize("./data/core_struct_data.txt", "./data/cleaned_core_struct_data.txt")


if __name__ == "__main__":
    main()
