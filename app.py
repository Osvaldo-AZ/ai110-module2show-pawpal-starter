import streamlit as st
from datetime import time

from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    TaskCategory, Priority,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pets" not in st.session_state:
    st.session_state.pets = []   # list[Pet]

if "schedule" not in st.session_state:
    st.session_state.schedule = None

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------

st.header("1. Owner Info")

with st.form("owner_form"):
    owner_name   = st.text_input("Your name", value="Jordan")
    avail_min    = st.number_input("Available minutes today", min_value=10, max_value=480, value=90)
    start_hour   = st.number_input("Start hour (24h)", min_value=0, max_value=23, value=7)
    start_minute = st.selectbox("Start minute", [0, 15, 30, 45], index=2)
    save_owner   = st.form_submit_button("Save owner")

if save_owner:
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes_per_day=int(avail_min),
        start_time=time(int(start_hour), int(start_minute)),
    )
    st.success(f"Owner '{owner_name}' saved.")

if st.session_state.owner:
    o = st.session_state.owner
    st.caption(f"Current owner: **{o.name}** — {o.available_minutes_per_day} min/day, starts at {o.start_time.strftime('%I:%M %p')}")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a pet
# ---------------------------------------------------------------------------

st.header("2. Add a Pet")

if st.session_state.owner is None:
    st.info("Save an owner above before adding pets.")
else:
    with st.form("pet_form"):
        pet_name = st.text_input("Pet name", value="Mochi")
        species  = st.selectbox("Species", ["dog", "cat", "other"])
        breed    = st.text_input("Breed (optional)")
        age      = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
        add_pet  = st.form_submit_button("Add pet")

    if add_pet:
        new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(age))
        st.session_state.pets.append(new_pet)
        st.session_state.owner.pets = st.session_state.pets
        st.success(f"Pet '{pet_name}' added.")

    if st.session_state.pets:
        st.write("**Your pets:**")
        for p in st.session_state.pets:
            task_count = len(p.tasks)
            st.markdown(f"- **{p.name}** ({p.species}, age {p.age}) — {task_count} task(s)")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add a task
# ---------------------------------------------------------------------------

st.header("3. Add a Task")

if not st.session_state.pets:
    st.info("Add at least one pet before adding tasks.")
else:
    with st.form("task_form"):
        pet_names   = [p.name for p in st.session_state.pets]
        target_pet  = st.selectbox("Assign to pet", pet_names)
        task_name   = st.text_input("Task name", value="Morning Walk")
        category    = st.selectbox("Category", [c.value for c in TaskCategory])
        priority    = st.selectbox("Priority", ["high", "medium", "low"])
        duration    = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        pref_time   = st.selectbox("Preferred time of day", ["morning", "afternoon", "evening", ""])
        is_required = st.checkbox("Required (must be scheduled)")
        add_task    = st.form_submit_button("Add task")

    if add_task:
        new_task = Task(
            name=task_name,
            category=TaskCategory(category),
            priority=Priority[priority.upper()],
            duration_minutes=int(duration),
            preferred_time_of_day=pref_time,
            is_required=is_required,
        )
        pet = next(p for p in st.session_state.pets if p.name == target_pet)
        pet.tasks.append(new_task)
        st.success(f"Task '{task_name}' added to {target_pet}.")

    for pet in st.session_state.pets:
        if pet.tasks:
            st.write(f"**{pet.name}'s tasks:**")
            st.table([t.to_dict() for t in pet.tasks])

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------

st.header("4. Generate Schedule")

ready = (
    st.session_state.owner is not None
    and any(len(p.tasks) > 0 for p in st.session_state.pets)
)

if not ready:
    st.info("Add an owner, at least one pet, and at least one task first.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler(owner=st.session_state.owner)
        st.session_state.schedule = scheduler.generate_plan()

    if st.session_state.schedule:
        plan = st.session_state.schedule
        st.subheader("Today's Schedule")
        st.text(plan.get_summary())

        with st.expander("Why this plan?"):
            st.text(plan.explain())
