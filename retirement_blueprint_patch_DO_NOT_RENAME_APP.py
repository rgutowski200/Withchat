#!/usr/bin/env python3
"""
Retirement Blueprint 101 safe patch script.

IMPORTANT:
- Do NOT rename this file to app.py.
- Keep your real Streamlit app as app.py.
- Run this script against app.py:

    python retirement_blueprint_patch_DO_NOT_RENAME_APP.py app.py
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
from datetime import datetime


def apply_patch(app_path: pathlib.Path) -> None:
    if not app_path.exists():
        raise FileNotFoundError(f"Could not find {app_path}")

    text = app_path.read_text(encoding="utf-8")
    original = text

    # Safety check: stop if app.py appears to be this patch script instead of the Streamlit app.
    if "Retirement Blueprint 101 safe patch script" in text or "def apply_patch(app_path" in text:
        raise RuntimeError(
            "This app.py appears to contain the patch script, not the Streamlit app. "
            "Restore the real app.py from GitHub history first, then run this patch script as a separate file."
        )

    backup = app_path.with_suffix(app_path.suffix + ".backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(app_path, backup)
    print(f"Backup created: {backup}")

    replacements = [
        ('go_to_page("Action Plan")', 'go_to_page("Recommendations")', "Bad navigation target"),
        ('get("ss_start_age", 62)', 'get("user_ss_age", 62)', "Social Security age key"),
        ('["Portfolio Need"]', '["Portfolio Withdrawal"]', "Old dataframe bracket column"),
        ('"Portfolio Need"', '"Portfolio Withdrawal"', "Old dataframe string column"),
    ]

    for old, new, label in replacements:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
        print(f"{label}: {count} replacement(s)")

    # Add compatibility alias to every projection function that returns pd.DataFrame(rows).
    old_return = "    return pd.DataFrame(rows)"
    new_return = (
        "    out = pd.DataFrame(rows)\n"
        "    if not out.empty and \"Portfolio Withdrawal\" in out.columns and \"Portfolio Need\" not in out.columns:\n"
        "        out[\"Portfolio Need\"] = out[\"Portfolio Withdrawal\"]\n"
        "    return out"
    )
    count = text.count(old_return)
    if count:
        text = text.replace(old_return, new_return)
    print(f"Projection compatibility aliases: {count} replacement(s)")

    # Make Quick Blueprint spending feed the real projection spending fields.
    quick_anchor = "            st.session_state.monthly_spending = quick_monthly_spending\n"
    quick_insert = (
        "            st.session_state.monthly_spending = quick_monthly_spending\n"
        "            st.session_state.budget_mode = \"Flat monthly number\"\n"
        "            st.session_state.flat_monthly_spending = quick_monthly_spending\n"
    )
    if "st.session_state.flat_monthly_spending = quick_monthly_spending" not in text:
        if quick_anchor in text:
            text = text.replace(quick_anchor, quick_insert, 1)
            print("Quick Blueprint spending save: 1 insertion")
        else:
            print("Quick Blueprint spending save: anchor not found")
    else:
        print("Quick Blueprint spending save: already present")

    if text == original:
        print("No changes were made. File may already be patched.")
    else:
        app_path.write_text(text, encoding="utf-8")
        print(f"Patched file written: {app_path}")

    print("\nNow run: streamlit run app.py")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("app_file", nargs="?", default="app.py")
    args = parser.parse_args()
    try:
        apply_patch(pathlib.Path(args.app_file))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

