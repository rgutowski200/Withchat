from pathlib import Path

APP = Path('app.py')
if not APP.exists():
    raise FileNotFoundError('app.py not found. Put this file in the same folder as app.py, then run: python add_start_blueprint_income_toggle.py')

text = APP.read_text(encoding='utf-8')
backup = Path('app_backup_before_income_toggle.py')
backup.write_text(text, encoding='utf-8')

insert_block = r'''
        # ---------------------------------------------------------
        # Start My Blueprint: Income entry toggle
        # ---------------------------------------------------------
        # This mirrors the Spending Plan segmented selector. It stays OUTSIDE
        # the main Start My Blueprint form so switching between Simple and
        # Detailed income updates immediately when clicked.
        st.subheader("Income")
        st.caption("Choose a quick income entry or build a detailed income list right here on Start My Blueprint.")

        current_income_mode = st.session_state.get("income_mode", "Simple income")
        income_display_default = "Detailed income" if current_income_mode == "Advanced income builder" else "Simple income"

        start_income_display_mode = st.radio(
            "How do you want to enter income?",
            ["Simple income", "Detailed income"],
            index=0 if income_display_default == "Simple income" else 1,
            key="start_blueprint_income_mode_selector",
            horizontal=True,
            help="Simple income is best for one pension, side gig, rental, or other income estimate. Detailed income lets you enter multiple income sources."
        )

        if start_income_display_mode == "Simple income":
            st.session_state.income_mode = "Simple income"
            st.info("Simple income selected. Enter one other income source, such as pension, rental income, part-time work, or consulting income.")

            with st.form("start_blueprint_simple_income_form"):
                si1, si2, si3 = st.columns(3)
                start_simple_income = si1.number_input(
                    "Other annual income before taxes",
                    min_value=0,
                    value=int(st.session_state.simple_income),
                    step=1000,
                    help=FIELD_HELP["simple_income"]
                )
                start_simple_income_start = si2.number_input(
                    "Income start age",
                    min_value=0,
                    max_value=110,
                    value=int(st.session_state.simple_income_start),
                    help=FIELD_HELP["simple_income_start"]
                )
                start_simple_income_end = si3.number_input(
                    "Income end age, use 0 if lifelong",
                    min_value=0,
                    max_value=120,
                    value=int(st.session_state.simple_income_end),
                    help=FIELD_HELP["simple_income_end"]
                )

                si4, si5 = st.columns(2)
                start_simple_income_inflation = si4.checkbox(
                    "Inflation adjusted?",
                    value=bool(st.session_state.simple_income_inflation),
                    help=FIELD_HELP["simple_income_inflation"]
                )
                start_simple_income_reliability = si5.selectbox(
                    "Reliability",
                    ["Guaranteed", "Variable"],
                    index=0 if st.session_state.simple_income_reliability == "Guaranteed" else 1,
                    help=FIELD_HELP["simple_income_reliability"]
                )

                save_start_simple_income = st.form_submit_button(
                    "Save simple income",
                    type="primary",
                    use_container_width=True
                )

            if save_start_simple_income:
                st.session_state.income_mode = "Simple income"
                st.session_state.simple_income = start_simple_income
                st.session_state.simple_income_start = start_simple_income_start
                st.session_state.simple_income_end = start_simple_income_end
                st.session_state.simple_income_inflation = start_simple_income_inflation
                st.session_state.simple_income_reliability = start_simple_income_reliability
                st.success("Simple income saved.")

        else:
            st.session_state.income_mode = "Advanced income builder"
            st.info("Detailed income selected. Add each income source separately. Use 0 for end age if the income is lifelong.")

            start_income_editor = st.data_editor(
                st.session_state.income_sources_df,
                num_rows="dynamic",
                use_container_width=True,
                key="start_blueprint_income_editor",
                column_config={
                    "Name": st.column_config.TextColumn("Income name"),
                    "Annual Amount": st.column_config.NumberColumn("Annual amount", min_value=0, step=1000),
                    "Start Age": st.column_config.NumberColumn("Start age", min_value=0, max_value=110, step=1),
                    "End Age": st.column_config.NumberColumn("End age", min_value=0, max_value=120, step=1, help="Use 0 if lifelong"),
                    "Inflation Adjusted": st.column_config.CheckboxColumn("Inflation adjusted?"),
                    "Taxable": st.column_config.CheckboxColumn("Taxable?"),
                    "Owner": st.column_config.SelectboxColumn("Owner", options=["User", "Spouse", "Joint"]),
                    "Reliability": st.column_config.SelectboxColumn("Reliability", options=["Guaranteed", "Variable"]),
                    "Continues After First Death": st.column_config.CheckboxColumn("Continues after first death?"),
                },
            )

            if st.button("Save detailed income sources", type="primary", use_container_width=True, key="save_start_blueprint_detailed_income"):
                st.session_state.income_mode = "Advanced income builder"
                st.session_state.income_sources_df = start_income_editor
                st.success("Detailed income sources saved.")

        st.divider()
'''

needle = '    else:\n        with st.form("guided_form"):'
if needle not in text:
    raise RuntimeError('Could not find the Start My Blueprint detailed form insertion point. Search for: else: followed by with st.form("guided_form")')

text = text.replace(needle, '    else:\n' + insert_block + '        with st.form("guided_form"):', 1)

# Optional: make the main detailed form income wording clear if users still use Income Plan page.
# No destructive changes to the existing Income Builder page.

Path('app_fixed.py').write_text(text, encoding='utf-8')
print('Done. Created app_fixed.py and backup app_backup_before_income_toggle.py')
print('Next: test app_fixed.py locally or rename it to app.py and commit to GitHub.')
