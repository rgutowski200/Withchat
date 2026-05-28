#!/usr/bin/env python3
"""
Retirement Blueprint 101 - baseline hotfix patch

How to use:
1. Put this file in the same folder as your Streamlit app file.
2. Run:
   python apply_retirement_blueprint_101_fixes.py app.py

What it fixes:
- Changes go_to_page("Action Plan") to go_to_page("Recommendations")
- Replaces ss_start_age lookups with user_ss_age lookups
- Replaces Projection page "Portfolio Need" references with "Portfolio Withdrawal"
- Adds a compatibility alias so old code looking for "Portfolio Need" still works
"""

from pathlib import Path
import sys
from datetime import datetime


def apply_fixes(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Could not find file: {path}")

    text = path.read_text(encoding="utf-8")
    original = text

    replacements = [
        ('go_to_page("Action Plan")', 'go_to_page("Recommendations")'),
        ('st.session_state.get("ss_start_age", 62)', 'st.session_state.get("user_ss_age", 62)'),
        ('df["Portfolio Need"].sum() if "Portfolio Need" in df.columns else 0',
         'df["Portfolio Withdrawal"].sum() if "Portfolio Withdrawal" in df.columns else 0'),
        ('"Portfolio Need",\n            "Estimated Federal Tax",',
         '"Portfolio Withdrawal",\n            "Estimated Federal Tax",'),
        ('"Portfolio Need": "From Savings",',
         '"Portfolio Withdrawal": "From Savings",'),
    ]

    changes = []
    for old, new in replacements:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
        changes.append((old, count))

    alias_marker = '# Compatibility alias for older UI sections that still reference "Portfolio Need".'
    if alias_marker not in text:
        target = """try:
    df = run_projection() if can_run else pd.DataFrame()
except Exception as _projection_error:
    df = pd.DataFrame()
    can_run = False
"""
        replacement = target + """
# Compatibility alias for older UI sections that still reference "Portfolio Need".
# The projection engine's real withdrawal column is "Portfolio Withdrawal".
if isinstance(df, pd.DataFrame) and not df.empty and "Portfolio Withdrawal" in df.columns and "Portfolio Need" not in df.columns:
    df["Portfolio Need"] = df["Portfolio Withdrawal"]
"""
        if target in text:
            text = text.replace(target, replacement, 1)
            changes.append(("Added Portfolio Need compatibility alias", 1))
        else:
            changes.append(("Added Portfolio Need compatibility alias", 0))

    if text == original:
        print("No changes were made. The file may already be patched.")
        return

    backup = path.with_suffix(path.suffix + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup.write_text(original, encoding="utf-8")
    path.write_text(text, encoding="utf-8")

    print(f"Patched: {path}")
    print(f"Backup saved: {backup}")
    print("\nChange summary:")
    for old, count in changes:
        label = old if len(old) < 85 else old[:82] + "..."
        print(f"- {label}: {count}")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("app.py")
    apply_fixes(target)
