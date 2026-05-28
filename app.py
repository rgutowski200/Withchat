#!/usr/bin/env python3
"""
Retirement Blueprint 101 - Fix Pack v2

Usage:
    python apply_retirement_blueprint_101_fixes_v2.py app.py

What this fixes:
1. Invalid navigation target: go_to_page("Action Plan") -> go_to_page("Recommendations")
2. Social Security age key mismatch: ss_start_age -> user_ss_age
3. Old projection column references: Portfolio Need -> Portfolio Withdrawal
4. Adds backward-compatible alias column: Portfolio Need = Portfolio Withdrawal
5. Quick Blueprint now saves spending into flat_monthly_spending and budget_mode so projections unlock.
6. Creates a timestamped backup before editing.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys
from datetime import datetime


def replace_once_or_report(text: str, old: str, new: str, label: str) -> tuple[str, int]:
    count = text.count(old)
    if count:
        text = text.replace(old, new)
    print(f"{label}: {count} replacement(s)")
    return text, count


def add_projection_aliases(text: str) -> tuple[str, int]:
    """Replace simple DataFrame returns from projection functions with alias-safe returns."""
    old = "    return pd.DataFrame(rows)"
    new = '''    out = pd.DataFrame(rows)
    if not out.empty and "Portfolio Withdrawal" in out.columns and "Portfolio Need" not in out.columns:
        out["Portfolio Need"] = out["Portfolio Withdrawal"]
    return out'''
    count = text.count(old)
    if count:
        text = text.replace(old, new)
    print(f"Projection alias return blocks: {count} replacement(s)")
    return text, count


def ensure_quick_blueprint_spending_saved(text: str) -> tuple[str, int]:
    """Make Quick Blueprint feed the same spending field the projection engine uses."""
    anchor = "            st.session_state.monthly_spending = quick_monthly_spending\n"
    insert = (
        "            st.session_state.monthly_spending = quick_monthly_spending\n"
        "            st.session_state.budget_mode = \"Flat monthly number\"\n"
        "            st.session_state.flat_monthly_spending = quick_monthly_spending\n"
    )

    if "st.session_state.flat_monthly_spending = quick_monthly_spending" in text:
        print("Quick Blueprint spending save: already present")
        return text, 0

    if anchor not in text:
        print("Quick Blueprint spending save: anchor not found")
        return text, 0

    text = text.replace(anchor, insert, 1)
    print("Quick Blueprint spending save: 1 insertion")
    return text, 1


def ensure_portfolio_withdrawal_total_safe(text: str) -> tuple[str, int]:
    """Make total withdrawals summary robust if older/newer column names are present."""
    old = '        total_withdrawals = float(df["Portfolio Withdrawal"].sum() if "Portfolio Withdrawal" in df.columns else 0)'
    new = '''        if "Portfolio Withdrawal" in df.columns:
            total_withdrawals = float(df["Portfolio Withdrawal"].sum())
        elif "Portfolio Need" in df.columns:
            total_withdrawals = float(df["Portfolio Need"].sum())
        else:
            total_withdrawals = 0.0'''
    if new in text:
        print("Projection total withdrawals fallback: already present")
        return text, 0
    count = text.count(old)
    if count:
        text = text.replace(old, new, 1)
    print(f"Projection total withdrawals fallback: {count} replacement(s)")
    return text, count


def patch_app(path: pathlib.Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Could not find file: {path}")

    original = path.read_text(encoding="utf-8")
    text = original

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(path.suffix + f".backup_{timestamp}")
    shutil.copy2(path, backup)
    print(f"Backup created: {backup}")

    text, _ = replace_once_or_report(
        text,
        'go_to_page("Action Plan")',
        'go_to_page("Recommendations")',
        "Navigation target fix",
    )

    text, _ = replace_once_or_report(
        text,
        'get("ss_start_age", 62)',
        'get("user_ss_age", 62)',
        "Social Security session key fix",
    )

    text, _ = replace_once_or_report(
        text,
        '["Portfolio Need"]',
        '["Portfolio Withdrawal"]',
        "Bracket Portfolio Need references",
    )

    text, _ = replace_once_or_report(
        text,
        '"Portfolio Need"',
        '"Portfolio Withdrawal"',
        "String Portfolio Need references",
    )

    # Re-add compatibility alias after broad replacement.
    text, _ = add_projection_aliases(text)

    text, _ = ensure_quick_blueprint_spending_saved(text)
    text, _ = ensure_portfolio_withdrawal_total_safe(text)

    if text == original:
        print("No changes were made. Your file may already be patched.")
    else:
        path.write_text(text, encoding="utf-8")
        print(f"Patched file written: {path}")

    print("\nNext steps:")
    print("1. Run: streamlit run app.py")
    print("2. Test Quick Blueprint -> Save Quick Blueprint -> View My Basic Blueprint")
    print("3. Test Dashboard -> See Action Plan")
    print("4. Test Projection page and confirm no Portfolio Need error appears")


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Retirement Blueprint 101 app.py")
    parser.add_argument("app_file", nargs="?", default="app.py", help="Path to your Streamlit app.py file")
    args = parser.parse_args()

    try:
        patch_app(pathlib.Path(args.app_file))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
