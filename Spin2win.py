import streamlit as st
import pandas as pd
import random

# 🎛 Sidebar Controls
st.sidebar.header("🎛 Session Controls")
spin_window = st.sidebar.selectbox("🧩 Spins for Kaprekar seed", [1, 2, 3, 4])
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# ✅ Session Init & Bank Sync
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.kaprekar_log = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes = []
elif not st.session_state.spins and st.session_state.bank != starting_bank:
    st.session_state.bank = starting_bank

# 🔄 Manual Reset
if st.sidebar.button("🔄 Manual Reset", key="manual_reset"):
    st.session_state.spins.clear()
    st.session_state.kaprekar_log.clear()
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes.clear()
    st.stop()

# 🎰 Define 12 Groups + Zero
roulette_groups = {
    "G1": [1, 2, 3], "G2": [4, 5, 6], "G3": [7, 8, 9],
    "G4": [10,11,12], "G5": [13,14,15], "G6": [16,17,18],
    "G7": [19,20,21], "G8": [22,23,24], "G9": [25,26,27],
    "G10": [28,29,30], "G11": [31,32,33], "G12": [34,35,36],
    "G0": [0]
}
digit_to_group = {i: f"G{i}" for i in range(1, 13)}
fib_seq = [1,1,2,3,5,8,13,21,34]

# 🧠 Helpers
def get_group(num):
    for group, nums in roulette_groups.items():
        if num in nums:
            return group
    return None

def build_kaprekar_input(spins):
    digits = []
    for s in spins:
        g = get_group(s)
        gnum = [k for k, v in digit_to_group.items() if v == g]
        digits.append(gnum[0] if gnum else random.randint(1, 12))
    while len(digits) < 4:
        digits.append(random.randint(1, 12))
    return digits[:4]

def apply_mirror_mode(digits):
    return digits[::-1]

# 🧩 Layout
st.set_page_config(page_title="Spin2Win: 12-Group Mode", layout="wide")
st.title("🎲 Spin2Win — 12-Group Kaprekar Mode")

# 🎯 Spin Input
spin_input = st.number_input("Enter Live Spin (0–36)", min_value=0, max_value=36)
bet_nums = []

if st.button("📩 Submit Spin", key="submit_spin"):
    st.session_state.spins.append(spin_input)

    if len(st.session_state.spins) >= spin_window:
        recent = st.session_state.spins[-spin_window:]
        digits = build_kaprekar_input(recent)
        if 0 in recent:
            digits = apply_mirror_mode(digits)

        seed = int("".join(map(str, digits)))
        st.session_state.kaprekar_log.append((seed, digits))

        # Remove duplicate digits for unique group mapping
        unique_digits = list(sorted(set(digits)))
        group_labels = [digit_to_group.get(d, "G?") for d in unique_digits]
        bet_nums = []
        for g in group_labels:
            bet_nums.extend(roulette_groups.get(g, []))

        # ✅ Accurate Hit Detection (no randomness)
        hit = spin_input in bet_nums

        # 💵 Betting Outcome
        bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq)-1)]
        payout = bet_unit * 2 if hit else 0
        st.session_state.bank += payout - bet_unit
        st.session_state.bank_history.append(st.session_state.bank)
        st.session_state.bet_sizes.append(bet_unit)

        if hit:
            st.success("🎉 HIT! You matched a suggested number.")
            st.session_state.spins.clear()
            st.session_state.kaprekar_log.clear()
            st.session_state.fib_step = 0
            st.session_state.bank_history = [st.session_state.bank]
            st.session_state.bet_sizes.clear()
            st.stop()
        else:
            st.session_state.fib_step += 1

# 💰 Bank Display
st.subheader("💰 Bank Summary")
st.markdown(f"### **€{st.session_state.bank}** remaining")

# 📐 Fibonacci Progression
st.subheader("📐 Fibonacci Betting Progress")
step = st.session_state.fib_step
max_step = len(fib_seq) - 1
progress = min(step / max_step, 1.0)
st.progress(progress)
st.markdown(f"**Step:** `{step}` of `{max_step}` → Bet Unit: `{fib_seq[min(step, max_step)]}`")
st.caption(f"Sequence: {fib_seq}")

# 🧬 Kaprekar Seed Breakdown
st.subheader("🧬 Kaprekar Seed Breakdown")
if st.session_state.kaprekar_log:
    seed, digits = st.session_state.kaprekar_log[-1]
    unique_digits = list(sorted(set(digits)))
    group_labels = [digit_to_group.get(d, "G?") for d in unique_digits]
    st.markdown(f"**Seed:** `{seed}` → Unique Digits → Groups: {group_labels}")

    # 🎯 Suggested Numbers to Bet
    st.subheader("🎯 Suggested Numbers to Bet")
    bet_nums = []
    for g in group_labels:
        bet_nums.extend(roulette_groups.get(g, []))
    st.markdown(f"**Groups:** {', '.join(group_labels)}")
    st.markdown(f"**Numbers:** {sorted(bet_nums)}")

# 🕹️ Last 4 Spins
st.subheader("🕹️ Last 4 Spins")
spins = st.session_state.spins[-4:]
groups = [get_group(s) for s in spins]
g_digits = [int(g[1:]) if g and g.startswith("G") else 0 for g in groups]

df = pd.DataFrame({
    "Spin": spins,
    "Group": groups,
    "Group Number": g_digits
})
st.dataframe(df, use_container_width=True)

# 🔮 Prediction Zone
if len(st.session_state.spins) >= 36:
    st.subheader("🔮 Prediction Zone")
    group_counts = pd.Series(groups).value_counts()
    st.dataframe(group_counts)
