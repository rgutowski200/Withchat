from pathlib import Path
import re
import shutil
import sys

SOURCE = Path("app.py")
OUTPUT = Path("app_fixed.py")
BACKUP = Path("app_backup_before_spouse_fix.py")

if not SOURCE.exists():
    print("ERROR: Put this file in the same folder as your current app.py, then run it again.")
    sys.exit(1)

text = SOURCE.read_text(encoding="utf-8")
original = text

# Make a backup first.
if not BACKUP.exists():
    shutil.copy2(SOURCE, BACKUP)

insert_pattern = '''    else:\n        with st.form("guided_form"):\n            st.subheader("Timeline")'''
insert_replacement = '''    else:\n        # Household checkbox lives OUTSIDE the form so spouse fields appear immediately.\n        # Streamlit forms only rerun after submit, which made the checkbox look selected\n        # while the spouse fields stayed hidden.\n        st.subheader("Household")\n\n        if "has_spouse_live" not in st.session_state:\n            st.session_state.has_spouse_live = bool(st.session_state.get("has_spouse", False))\n\n        has_spouse_live = st.checkbox(\n            "Include spouse or partner in this blueprint?",\n            value=bool(st.session_state.has_spouse_live),\n            key="has_spouse_live",\n            help="Turn this on if the retirement plan should include a spouse or partner. Leave it off for an individual plan."\n        )\n\n        st.session_state.has_spouse = bool(has_spouse_live)\n\n        if has_spouse_live:\n            st.info("Spouse / partner fields are included in this blueprint. Complete the spouse fields below, then click Save main answers.")\n        else:\n            st.caption("Individual plan selected. Spouse / partner fields are hidden and will not affect the projection.")\n\n        with st.form("guided_form"):\n            st.subheader("Timeline")'''

if insert_pattern not in text:
    print("ERROR: Could not find the Guided Questions form start. Your app.py may have changed.")
    sys.exit(1)

text = text.replace(insert_pattern, insert_replacement, 1)

# Replace the duplicate in-form spouse checkbox with a plain value read.
# This keeps the spouse fields inside the form, but the on/off control is outside the form.
form_block_pattern = re.compile(
    r'''\n\s{12}st\.subheader\("Household"\)\n\s{12}has_spouse = st\.checkbox\(\n\s{16}"Include spouse or partner in this blueprint\?",\n\s{16}value=st\.session_state\.has_spouse,\n\s{16}help="Turn this on if the retirement plan should include a spouse or partner\. Leave it off for an individual plan\."\n\s{12}\)\n\n\s{12}if has_spouse:''',
    re.MULTILINE,
)

replacement = '''\n            has_spouse = bool(st.session_state.get("has_spouse", False))\n\n            if has_spouse:'''

text, count = form_block_pattern.subn(replacement, text, count=1)

if count != 1:
    print("ERROR: Could not remove the in-form spouse checkbox. Your app.py may have changed.")
    sys.exit(1)

# Optional: keep the two state keys synced after the user saves the form.
# This prevents future mismatches if older saved scenarios update only has_spouse.
save_anchor = '''                "has_spouse": has_spouse,'''
if save_anchor not in text:
    print("WARNING: Could not find save dictionary anchor. The main fix was still applied.")
else:
    # No code change needed here; has_spouse variable now reads from session_state.
    pass

OUTPUT.write_text(text, encoding="utf-8")

print("Done. Created app_fixed.py")
print("Backup created as app_backup_before_spouse_fix.py")
print("Next: upload app_fixed.py to GitHub as app.py, or rename app_fixed.py to app.py.")
