import re
import json
import pandas as pd
from helper_functions.helpers import CORE_STRUCT_DATA_PATH


def sanitize(input_file_name, output_file_name):
    # Read structure data file
    with open(input_file_name, "r") as infile, open(output_file_name, "w") as outfile:
        for line in infile:
            # Remove Quotation Marks and Whitespace
            clean_line = line.replace('"', "").rstrip()
            clean_line = clean_line.replace("* \t ", "* ")

            # Misc Removes
            clean_line = clean_line.replace("&amp;", "&").replace("(Tag)", "")
            clean_line = clean_line.replace("One from", "")

            # Remove Empty lines
            if clean_line.strip():
                # Write cleaned line to output file
                outfile.write(clean_line + "\n")


def parse_core_struct_data(file_name) -> dict:
    core_struct = {"program_name": "Core Program", "categories": []}

    with open(file_name, "r") as infile:
        for line in infile:
            # 1. CLEANING
            tab_count = len(line) - len(line.lstrip("\t"))
            content = line.strip()

            # Pointers to the most recently created objects
            last_cat = (
                core_struct["categories"][-1] if core_struct["categories"] else None
            )
            last_sec = (
                last_cat["sections"][-1] if last_cat and last_cat["sections"] else None
            )

            # 3. CATEGORY (Tab 0, starts with -)
            if tab_count == 0 and content.startswith("-"):
                name = content.lstrip("- ").strip()
                core_struct["categories"].append({"name": name, "sections": []})

            # 4. SECTION (Tab 1, starts with -)
            elif tab_count == 1 and content.startswith("-"):
                name = content.lstrip("- ").strip()
                last_cat["sections"].append(
                    {"name": name, "courses": [], "subsections": []}
                )

            # 5. SUBSECTION (Tab 1 without dash OR Tab 2 with dash)
            elif (tab_count == 1 and not content.startswith("-")) or (
                tab_count == 2 and content.startswith("-")
            ):
                name = content.lstrip("- ").strip()
                if last_sec is not None:
                    last_sec["subsections"].append({"name": name, "courses": []})

            # 6. COURSE (Tab 2 or 3, starts with *)
            elif tab_count in [2, 3] and content.startswith("*"):
                course_full = content.lstrip("* ").strip()
                course_full = re.sub(r"\t.*", "", course_full).strip()
                code = course_full.split(" - ")[0].strip()

                # Determine Parent: Last subsection gets priority, else the section
                if last_sec:
                    if last_sec["subsections"]:
                        target_list = last_sec["subsections"][-1]["courses"]
                    else:
                        target_list = last_sec["courses"]

                    target_list.append({"code": code, "name": course_full})

    # Save to JSON
    with open(f"./data/core_struct_data_parsed.json", "w") as outfile:
        json.dump(core_struct, outfile, indent=4)

    return core_struct


def main():
    OG_FILE_NAME = CORE_STRUCT_DATA_PATH
    CLEANED_FILE_NAME = "../data/cleaned_core_struct_data.txt"

    sanitize(OG_FILE_NAME, CLEANED_FILE_NAME)

    parse_core_struct_data(CLEANED_FILE_NAME)


if __name__ == "__main__":
    main()
