
"""
Retirement Blueprint 101 - spouse checkbox fix

IMPORTANT:
- Do NOT upload this file as app.py.
- Put this file in the same folder as your real app.py.
- Run: python apply_spouse_fix.py
- It will make a backup named app_before_spouse_fix.py and update app.py.

What it fixes:
The spouse checkbox was inside st.form("guided_form"), so Streamlit did not refresh the spouse fields immediately.
This patch moves the spouse/partner checkbox outside the form and uses the saved session_state value inside the form.
"""

from pathlib import Path
import sys

APP_PATH = Path("app.py")
BACKUP_PATH = Path("app_before_spouse_fix.py")

if not APP_PATH.exists():
    raise FileNotFoundError("Could not find app.py in this folder. Put this script next to your real app.py and run it again.")

text = APP_PATH.read_text(encoding="utf-8")

if "spouse_live_selector" in text:
    print("Spouse fix already appears to be installed. No changes made.")
    sys.exit(0)

# Make backup first.
BACKUP_PATH.write_text(text, encoding="utf-8")

# 1) Move the live spouse checkbox outside the guided_form.
needle = 'else:\n        with st.form("guided_form"):'
replacement = '''else:
        # Live spouse/partner selector.
        # This stays OUTSIDE st.form so the spouse fields appear/disappear immediately when clicked.
        st.subheader("Household")
        has_spouse_live = st.checkbox(
            "Include spouse or partner in this blueprint?",
            value=bool(st.session_state.get("has_spouse", False)),
            help="Turn this on if the retirement plan should include a spouse or partner. Leave it off for an individual plan.",
            key="spouse_live_selector",
        )
        st.session_state.has_spouse = has_spouse_live

        with st.form("guided_form"):'''

if needle not in text:
    raise RuntimeError(
        'Could not find the Detailed Blueprint form start. Expected to find: else:\\n        with st.form("guided_form"):'
    )

text = text.replace(needle, replacement, 1)

# 2) Inside the form, remove the form-contained checkbox and read the live value instead.
form_start = text.find('with st.form("guided_form"):')
household_start = text.find('            st.subheader("Household")', form_start)
if household_start == -1:
    raise RuntimeError('Could not find the Household section inside st.form("guided_form").')

if_start = text.find('            if has_spouse:', household_start)
if if_start == -1:
    raise RuntimeError('Could not find "if has_spouse:" after the Household section.')

new_block = '''            st.subheader("Household")
            has_spouse = bool(st.session_state.get("has_spouse", False))

'''

# Replace only this first Household block inside the guided form.
text = text[:household_start] + new_block + text[if_start:]

# 3) Optional safety: make sure no duplicate old checkbox remains inside guided_form before spouse fields.
remaining_segment = text[form_start: text.find('            if has_spouse:', form_start)]
if 'st.checkbox(\n                "Include spouse or partner in this blueprint?"' in remaining_segment:
    raise RuntimeError("Patch safety check failed: old spouse checkbox still appears inside the form.")

APP_PATH.write_text(text, encoding="utf-8")

print("Success. app.py has been updated.")
print(f"Backup saved as: {BACKUP_PATH}")
print("Now commit app.py. Keep or delete the backup file.")
