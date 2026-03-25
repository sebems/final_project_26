import json
import pandas as pd
from helper_functions.helpers import (
    MAIN_DATA_PATH,
    CORE_JSON_PATH,
    CORE_JSON_DATAFRAME_PATH,
    PREP_COLS_AND_TYPES,
    clean_main_dataframe,
    PREP_COLS,
)


def json_to_dataframe(json_file):
    # Load the JSON data
    with open(json_file, "r") as f:
        data = json.load(f)

    program_name = data.get("program_name", "Core Program")
    rows = []

    # Traverse categories
    for category in data.get("categories", []):
        cat_name = category.get("name")

        # Traverse sections
        for section in category.get("sections", []):
            sec_name = section.get("name")

            # 1. Handle courses directly under the section (no subsection)
            for course in section.get("courses", []):
                rows.append(
                    {
                        "program_name": program_name,
                        "categories": cat_name,
                        "sections": sec_name,
                        "subsections": None,  # No subsection for these courses
                        "course_code": course.get("code"),
                        "course_name": course.get("name"),
                    }
                )

            # 2. Handle courses nested within subsections
            for subsection in section.get("subsections", []):
                sub_name = subsection.get("name")
                for course in subsection.get("courses", []):
                    rows.append(
                        {
                            "program_name": program_name,
                            "categories": cat_name,
                            "sections": sec_name,
                            "subsections": sub_name,
                            "course_code": course.get("code"),
                            "course_name": course.get("name"),
                        }
                    )

    # Create and return the DataFrame
    return pd.DataFrame(rows)


import pandas as pd
import re


def extract_nested_requirements(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Capture all tags that could be headers or requirements
    elements = re.findall(r"<(span|p|li)[^>]*>(.*?)<\/\1>", html_content, re.DOTALL)

    data = []
    current_cat = None
    current_sec = None
    current_sub = None

    for tag, content in elements:
        text = re.sub(r"<[^>]+>", " ", content).strip()
        if not text:
            continue

        # 1. IDENTIFY CATEGORY (e.g., KNOWLEDGE AND UNDERSTANDING)
        # These are spans that are entirely uppercase
        if tag == "span" and text.isupper() and len(text) > 5:
            current_cat = text
            current_sec = None  # Reset children
            current_sub = None
            continue

        # 2. IDENTIFY SECTION (e.g., Arts, Oral Rhetoric, Visual Rhetoric)
        # In your HTML, these are usually spans with class="subhead"
        if "subhead" in tag and not text.isupper():
            current_sec = text
            current_sub = None  # Reset subsection
            continue

        # 3. IDENTIFY SUBSECTION (e.g., Art, Communication, Music)
        # These appear as plain text/spans before a course list but after a section header
        # We can identify them because they aren't "Complete..." and aren't courses
        if (
            tag == "span"
            and not text.startswith("Complete")
            and "acalog-course" not in tag
        ):
            # If we already have a section, this is likely a subsection discipline
            if current_sec and text != current_sec:
                current_sub = text

        # 4. CAPTURE REQUIREMENT
        if tag == "p" and text.startswith("Complete"):
            # Use regex to find semester hours
            hours_match = re.search(r"(\d+(?:–\d+)?)\s+semester hours", text)
            hours = hours_match.group(1) if hours_match else "1 course"

            data.append(
                {
                    "category": current_cat,
                    "section": current_sec,
                    "subsection": current_sub,
                    "credits_required": hours,
                    "requirement_text": text,
                }
            )

    return pd.DataFrame(data)


def main():
    # Usage
    core_json_df = json_to_dataframe(CORE_JSON_PATH)

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

    course_df["Course Code"] = course_df["Prefix"] + " " + course_df["Code"]

    core_json_df["course_oid"] = core_json_df["course_code"].map(
        course_df.set_index("Course Code")["Course OID"]
    )

    core_json_df["credits"] = core_json_df["course_code"].map(
        course_df.set_index("Course Code")["Credits:"]
    )

    # courses_list = course_df[["Course OID", "Course Code"]].values.tolist()
    # courses_dict = {course_code: course_oid for course_oid, course_code in courses_list}

    # HARD CODE CREDIT MAX for Core Program Categories
    core_json_df["min_categories_credits"] = core_json_df["categories"].map(
        {
            "KNOWLEDGE AND UNDERSTANDING": 26,
            "FOUNDATIONS": 8,
            "COMPETENCIES AND SKILLS": 10,
            "CROSS-DISCIPLINARY INTEGRATION": 8,
        }
    )
    # HARD CODE CREDIT MIN for Core Program Sections
    core_json_df["section_credit_min"] = core_json_df["sections"].map(
        {
            "World Languages II": 0,
            "Arts, Oral Rhetoric, Visual Rhetoric": 2,
            "Humanities": 2,
            "Mathematical Sciences": 0,
            "Natural Sciences": 0,
            "Social and Behavioral Sciences": 2,
        }
    )

    # HARD CODE CREDIT MAX for Core Program Sections
    core_json_df["section_credit_max"] = core_json_df["sections"].map(
        {
            "World Languages II": 4,
            "Arts, Oral Rhetoric, Visual Rhetoric": 6,
            "Humanities": 6,
            "Mathematical Sciences": 4,
            "Natural Sciences": 6,
            "Social and Behavioral Sciences": 6,
        }
    )

    # Save to CSV
    core_json_df.to_csv(CORE_JSON_DATAFRAME_PATH, index=False)


if __name__ == "__main__":
    main()
