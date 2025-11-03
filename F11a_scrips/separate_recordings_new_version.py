#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import pandas as pd


def is_filled(x) -> bool:
    """Return True if the value is non-empty and non-NaN."""
    if pd.isna(x):
        return False
    if isinstance(x, str):
        return x.strip() != ""
    return True  # numbers, bools, etc.


def split_rows(df: pd.DataFrame, col1="recording1", col2="recording2") -> pd.DataFrame:
    """If both recording1 and recording2 are filled, split into two rows (pos/neg)."""
    missing = [c for c in (col1, col2) if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    if "pos_neg" not in df.columns:
        df["pos_neg"] = ""

    rows_out = []
    cols = list(df.columns)

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        rec1, rec2 = row_dict.get(col1), row_dict.get(col2)
        has1, has2 = is_filled(rec1), is_filled(rec2)

        if has1 and has2:
            # Row A: keep recording1, blank recording2
            row_a = row_dict.copy()
            row_a[col2] = ""
            row_a["pos_neg"] = "pos"
            rows_out.append(row_a)

            # Row B: keep recording2, blank recording1
            row_b = row_dict.copy()
            row_b[col1] = ""
            row_b["pos_neg"] = "neg"
            rows_out.append(row_b)
        else:
            # Unchanged row (no splitting)
            row_dict["pos_neg"] = ""
            rows_out.append(row_dict)

    return pd.DataFrame(rows_out, columns=cols)


def process_excel(path: Path, inplace: bool):
    """Read, process, and save Excel file (renaming original first)."""
    try:
        df = pd.read_excel(path)
    except Exception as e:
        print(f"[read fail] {path}: {e}")
        return

    try:
        new_df = split_rows(df, "recording1", "recording2")
    except Exception as e:
        print(f"[transform skip] {path}: {e}")
        return

    # Always rename original before writing
    original_path = path.with_name(f"original{path.suffix}")
    out_path = path  # processed file keeps original name

    try:
        if not original_path.exists():
            path.rename(original_path)
            print(f"[renamed] {path.name} -> {original_path.name}")
        else:
            print(f"[skip rename] {original_path.name} already exists")

        new_df.to_excel(out_path, index=False, engine="openpyxl")
        added_rows = len(new_df) - len(df)
        print(f"[saved] {out_path} (+{added_rows} rows)")
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
