"""
Netflix Top 10 — Data Cleaning Script
Jan–May 2026 | English Movies & Shows
Author: Lavina Saini
Date: 26-05-2026

This script cleans the raw Netflix Top 10 data collected weekly from:
https://www.netflix.com/tudum/top10

Issues fixed:
  Movies Sheet (6 issues):
    1. Wrong number formats      e.g. "1,72,00,000\t" → 17200000
    2. Runtime format converted  e.g. "01:58:00" → 1.97 (decimal hours)
    3. Column name typo          "Ttitle" → "Title"
    4. Genre spelling mistake    "Documentry" → "Documentary"
    5. Title whitespace          " KPop Demon Hunters" → "KPop Demon Hunters"
    6. Duplicate rows removed

  Shows Sheet (4 issues):
    1. Wrong number formats      same as above
    2. Runtime format converted  same as above
    3. Genre spelling mistake    "Documentry" → "Documentary"
    4. Title whitespace          leading/trailing spaces stripped
"""

import pandas as pd
import re


# ── Helpers ──────────────────────────────────────────────────────────────────

def fix_number_format(value):
    """
    Clean messy number strings like '1,72,00,000\t' or '17,200,000' → 17200000.
    Returns the original value if it is already numeric.
    """
    if pd.isna(value):
        return value
    if isinstance(value, (int, float)):
        return value
    # Remove commas, tabs, and extra whitespace, then convert
    cleaned = re.sub(r"[\t,\s]", "", str(value))
    try:
        return int(cleaned)
    except ValueError:
        return value


def runtime_to_decimal(value):
    """
    Convert HH:MM:SS runtime strings to decimal hours.
    e.g. "01:58:30" → 1.975
    Leaves numeric values untouched.
    """
    if pd.isna(value):
        return value
    if isinstance(value, (int, float)):
        return round(value, 4)
    value = str(value).strip()
    if re.match(r"^\d{1,2}:\d{2}:\d{2}$", value):
        h, m, s = value.split(":")
        return round(int(h) + int(m) / 60 + int(s) / 3600, 4)
    try:
        return round(float(value), 4)
    except ValueError:
        return value


GENRE_FIXES = {
    "documentry": "Documentary",
    "Documentry": "Documentary",
    "documantary": "Documentary",
    "Sci Fi": "Sci-Fi",
    "sci fi": "Sci-Fi",
}

def fix_genre(value):
    """Fix known genre spelling mistakes."""
    if pd.isna(value):
        return value
    return GENRE_FIXES.get(str(value).strip(), str(value).strip())


def fix_column_names(df):
    """Fix column name typos and normalize to consistent casing."""
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
    )
    # Fix known typo: "Ttitle" → "Title"
    df = df.rename(columns={"Ttitle": "Title", "ttitle": "Title"})
    return df


# ── Main Cleaning Function ────────────────────────────────────────────────────

def clean_sheet(df, sheet_name):
    """Apply all cleaning steps to a dataframe and return cleaned version."""
    print(f"\n{'─'*50}")
    print(f"  Cleaning sheet: {sheet_name}")
    print(f"  Rows before: {len(df)}")

    # Step 1 — Fix column name typos
    df = fix_column_names(df)

    # Step 2 — Strip leading/trailing whitespace from Title (Issue: title whitespace)
    if "Title" in df.columns:
        before = df["Title"].copy()
        df["Title"] = df["Title"].str.strip()
        changed = (before != df["Title"]).sum()
        if changed:
            print(f"  [Fixed] Title whitespace: {changed} cell(s)")

    # Step 3 — Fix number formats for Weekly_Viewed and Hours_Viewed
    for col in ["Weekly_Viewed", "Hours_Viewed"]:
        if col in df.columns:
            before = df[col].copy()
            df[col] = df[col].apply(fix_number_format)
            changed = (before.astype(str) != df[col].astype(str)).sum()
            if changed:
                print(f"  [Fixed] Number format in '{col}': {changed} cell(s)")

    # Step 4 — Convert Runtime to decimal hours
    if "Runtime_Hrs" in df.columns:
        before = df["Runtime_Hrs"].copy()
        df["Runtime_Hrs"] = df["Runtime_Hrs"].apply(runtime_to_decimal)
        changed = (before.astype(str) != df["Runtime_Hrs"].astype(str)).sum()
        if changed:
            print(f"  [Fixed] Runtime format converted: {changed} cell(s)")

    # Step 5 — Fix genre spelling mistakes
    if "Genre" in df.columns:
        before = df["Genre"].copy()
        df["Genre"] = df["Genre"].apply(fix_genre)
        changed = (before != df["Genre"]).sum()
        if changed:
            print(f"  [Fixed] Genre spelling: {changed} cell(s)")

    # Step 6 — Remove duplicate rows
    before_count = len(df)
    df = df.drop_duplicates()
    removed = before_count - len(df)
    if removed:
        print(f"  [Fixed] Duplicate rows removed: {removed}")

    # Step 7 — Drop completely empty rows
    df = df.dropna(how="all")

    print(f"  Rows after:  {len(df)}")
    return df


# ── Run ───────────────────────────────────────────────────────────────────────

def main():
    input_file  = r"D:\Lavi\Study\Netflix\Clean Data\Clean Data Movie.xlsx"
    output_file = r"D:\Lavi\Study\Netflix\Clean Data\Clean Data Movie_Cleaned.xlsx"

    print("Netflix Top 10 — Data Cleaning")
    print("=" * 50)

    # Read both sheets
    try:
        movies_raw = pd.read_excel(input_file, sheet_name="Movie(English)",  header=1)
        shows_raw  = pd.read_excel(input_file, sheet_name="Shows(English)", header=1)
    except FileNotFoundError:
        print(f"\n[ERROR] File not found: {input_file}")
        print("  Update the 'input_file' path at the bottom of this script.")
        return

    # Clean both sheets
    movies_clean = clean_sheet(movies_raw.copy(), "Movie(English)")
    shows_clean  = clean_sheet(shows_raw.copy(),  "Shows(English)")

    # Save cleaned data
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        movies_clean.to_excel(writer, sheet_name="Movie(English)", index=False)
        shows_clean.to_excel(writer,  sheet_name="Shows(English)", index=False)

    print(f"\n{'='*50}")
    print(f"  Cleaned file saved → {output_file}")
    print(f"  Movies rows: {len(movies_clean)}")
    print(f"  Shows rows:  {len(shows_clean)}")
    print("  Done ✓")


if __name__ == "__main__":
    main()
