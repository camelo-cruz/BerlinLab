#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import pandas as pd


def is_filled(x) -> bool:
    """Check whether a cell value is filled (non-empty and non-NaN)."""
    if pd.isna(x):
        return False
    if isinstance(x, str):
        return x.strip() != ""
    return True


def duplicate_to_recording2(df: pd.DataFrame, col_rec="recording", col_rec2="recording2") -> pd.DataFrame:
    """After each filled 'recording' row, insert a copy with 'recording' blank and 'recording2' set."""
    if col_rec not in df.columns:
        raise ValueError(f"Missing required column: {col_rec}")

    df = df.copy()

    # Ensure columns exist
    if "pos_neg" not in df.columns:
        df["pos_neg"] = ""
    if col_rec2 not in df.columns:
        df[col_rec2] = ""

    # Reorder so recording2 is immediately after recording
    cols = list(df.columns)
    cols.remove(col_rec2)
    insert_idx = cols.index(col_rec) + 1
    cols.insert(insert_idx, col_rec2)
    df = df[cols]

    rows_out = []

    for row in df.to_dict(orient="records"):
        rec_val = row.get(col_rec)

        if is_filled(rec_val):
            # Original row marked as positive
            row["pos_neg"] = "pos"
            rows_out.append(row)

            # Copy row marked as negative
            new_row = row.copy()
            new_row[col_rec] = ""
            new_row["pos_neg"] = "neg"
            new_row["automatic_transcription"] = ""
            new_row["latin_transcription_everything"] = ""
            rows_out.append(new_row)
        else:
            # Keep untouched row with empty pos_neg
            row["pos_neg"] = ""
            rows_out.append(row)

    return pd.DataFrame(rows_out, columns=cols)


def process_excel(path: Path, inplace: bool):
    """Read, transform, and write an Excel file."""
    try:
        df = pd.read_excel(path)
    except Exception as e:
        print(f"[read fail] {path}: {e}")
        return

    try:
        new_df = duplicate_to_recording2(df, "recording", "recording2")
    except Exception as e:
        print(f"[transform skip] {path}: {e}")
        return

    # Always rename original to *_original before saving the new one
    original_path = path.with_name(f"original{path.suffix}")
    out_path = path  # final processed file keeps original name

    try:
        # Rename original file if not already renamed
        if not original_path.exists():
            path.rename(original_path)
            print(f"[renamed] {path.name} -> {original_path.name}")
        else:
            print(f"[skip rename] {original_path.name} already exists")

        # Apply red text color to transcription columns (if any)
        def red_text(val):
            return "color: red"

        highlight_cols = [
            c for c in ["transcription_original_script", "latin_transcription_everything"]
            if c in new_df.columns
        ]

        if highlight_cols:
            styler = new_df.style.applymap(red_text, subset=highlight_cols)
            styler.to_excel(out_path, index=False, engine="openpyxl")
        else:
            new_df.to_excel(out_path, index=False, engine="openpyxl")

        print(f"[saved] {out_path}")
    except Exception as e:
        print(f"[write fail] {out_path}: {e}")


def process_session_dir(session_dir: Path, inplace: bool):
    """Process a single session directory."""
    worked = False
    for ext in (".xlsx", ".xls"):
        path = session_dir / f"trials_and_sessions_annotated{ext}"
        if path.exists():
            process_excel(path, inplace)
            worked = True
    if not worked:
        print(f"[no file] {session_dir}/trials_and_sessions_annotated(.xlsx|.xls) not found")


def main():
    parser = argparse.ArgumentParser(
        description="After each filled 'recording' row, insert a new row with 'recording' blank and 'recording2' set to the original value."
    )
    parser.add_argument("root", help="Path to a session_* folder OR a folder containing session_* subfolders.")
    parser.add_argument("--inplace", action="store_true", help="Overwrite original Excel files instead of creating _pos_neg versions.")
    args = parser.parse_args()

    root_path = Path(args.root).expanduser()

    if not root_path.exists():
        print(f"[error] Root path does not exist: {root_path}")
        return

    # Case 1: root is a session_* folder
    if root_path.is_dir() and root_path.name.lower().startswith("session_"):
        print(f"[process] session folder: {root_path}")
        process_session_dir(root_path, args.inplace)
        return

    # Case 2: root contains session_* subfolders
    any_found = False
    for entry in os.listdir(root_path):
        folder_path = root_path / entry
        if folder_path.is_dir() and entry.lower().startswith("session_"):
            any_found = True
            print(f"[process] session folder: {folder_path}")
            process_session_dir(folder_path, args.inplace)

    if not any_found:
        print(f"[info] No session_* folders under: {root_path}")


if __name__ == "__main__":
    main()
