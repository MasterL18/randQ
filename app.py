import random
import time

import streamlit as st

from randq.selector import rand_draw


FLASH_SECONDS = 3.0
FLASH_INTERVAL_SECONDS = 0.15


def initialize_state():
    defaults = {
        "names": [],
        "questions": [],
        "used_pairs": set(),
        "pending_pair": None,
        "displayed_pair": None,
        "flash_pair": None,
        "flash_until": 0.0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def clear_draw_state():
    st.session_state.pending_pair = None
    st.session_state.displayed_pair = None
    st.session_state.flash_pair = None
    st.session_state.flash_until = 0.0


def add_entry(target, value):
    entry = value.strip()
    if not entry:
        return False
    st.session_state[target].append(entry)
    clear_draw_state()
    return True


def draw_pair(no_repeats):
    excluded_pairs = st.session_state.used_pairs if no_repeats else set()
    return rand_draw(
        st.session_state.names,
        st.session_state.questions,
        random,
        excluded_pairs,
    )


st.set_page_config(page_title="Random Question Draw", page_icon="?")
initialize_state()
st.title("Random Question Draw")
st.write("Build your roster and question bank, then draw a pair.")

name_column, question_column = st.columns(2)

with name_column:
    st.subheader("Roster")
    with st.form("add_name_form", clear_on_submit=True):
        name_value = st.text_input("Name", placeholder="Add one name")
        add_name = st.form_submit_button("Add")
    if add_name:
        if not add_entry("names", name_value):
            st.warning("Enter a name before adding it.")

with question_column:
    st.subheader("Questions")
    with st.form("add_question_form", clear_on_submit=True):
        question_value = st.text_input("Question", placeholder="Add one question")
        add_question = st.form_submit_button("Add")
    if add_question:
        if not add_entry("questions", question_value):
            st.warning("Enter a question before adding it.")

list_column, settings_column = st.columns(2)
with list_column:
    st.subheader("Current lists")
    st.write("Names")
    if st.session_state.names:
        st.write(st.session_state.names)
    else:
        st.caption("No names added yet.")
    st.write("Questions")
    if st.session_state.questions:
        st.write(st.session_state.questions)
    else:
        st.caption("No questions added yet.")

with settings_column:
    st.subheader("Draw")
    no_repeats = st.checkbox("No repeats", key="no_repeats")
    is_flashing = (
        st.session_state.pending_pair is not None
        and time.monotonic() < st.session_state.flash_until
    )
    draw_clicked = st.button("Draw", type="primary", disabled=is_flashing)
    if draw_clicked:
        if not st.session_state.names:
            st.error("Add at least one name before drawing.")
        elif not st.session_state.questions:
            st.error("Add at least one question before drawing.")
        else:
            try:
                selected_pair = draw_pair(no_repeats)
            except ValueError:
                st.error("All name/question pairs have been used. Turn off no repeats or add more entries.")
            else:
                st.session_state.pending_pair = selected_pair
                st.session_state.used_pairs.add(selected_pair)
                st.session_state.flash_pair = selected_pair
                st.session_state.flash_until = time.monotonic() + FLASH_SECONDS
                st.rerun()

if st.session_state.pending_pair is not None:
    if time.monotonic() < st.session_state.flash_until:
        st.session_state.flash_pair = rand_draw(
            st.session_state.names,
            st.session_state.questions,
            random,
        )
        st.subheader("Selecting...")
        st.info(
            f"{st.session_state.flash_pair[0]}\n\n"
            f"{st.session_state.flash_pair[1]}"
        )
        time.sleep(FLASH_INTERVAL_SECONDS)
        st.rerun()
    else:
        st.session_state.displayed_pair = st.session_state.pending_pair
        st.session_state.pending_pair = None
        st.session_state.flash_pair = None
        st.session_state.flash_until = 0.0
        st.rerun()

if st.session_state.displayed_pair is not None:
    chosen_name, chosen_question = st.session_state.displayed_pair
    st.subheader("Your draw")
    st.success(f"{chosen_name}\n\n{chosen_question}")
