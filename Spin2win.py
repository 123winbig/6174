import streamlit as st
import pandas as pd
import random

# 🎛 Sidebar Controls
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# ✅ Session Initialization
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.kaprekar_log = []
    st.session_state.bet_sizes = []
    st.session_state.bank_history = [starting_bank]
elif not st.session_state.spins and st.session_state.bank != starting_bank:
    st.session_state.bank = starting_bank

# 🔄 Manual Reset
if st.sidebar.button("🔄 Manual Reset"):
    st.session_state.spins.clear()
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.kaprekar_log.clear()
    st.session_state.bet_sizes.clear()
    st.session_state.bank_history = [starting_bank]
    st.stop()

# 🎡 Realistic Roulette Wheel Grouping (European-style)
roulette_groups = {
    "G1": [32, 15, 19],
    "G2": [4, 21, 2],
    "G3": [25, 17, 34],
    "G4": [6, 27, 13],
    "G5": [36, 11, 30],
    "G6": [8, 23, 10],
    "G7": [5, 24, 16],
    "G8": [33, 1, 20],
    "G9": [14, 31, 9],
    "G10": [22, 18, 29],
    "G11": [7, 28, 12],
    "G12": [35, 3, 26],
    "G0": [0]
}
digit_to_group = {i: f"G{i}" for i in range(1, 13)}
fib_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34]

# 🧠 Utility Functions
def get_group(num):
    for g, nums in roulette_groups.items():
        if num in nums:
            return g
    return None

def build_kaprekar_input(spins):
    digits = []
    for s in spins[-4:]:
        g = get_group(s)
        gnum = [k for k, v in digit_to_group.items() if v == g]
        digits.append(gnum[0] if gnum else random.randint(1, 12))
    while len(digits) < 4:
        digits.append(random.randint(1, 12))
    return digits[:4]

# 🧩 Page Setup
st.set_page_config(page_title="Spin2Win — Real Wheel Kaprekar", layout="wide")
st.title("🎲 Spin2Win — Live Kaprekar Strategy (Real Wheel)")

# 🎯 Spin Input
spin_input = st.number_input("Enter Spin (0–36)", min_value=0, max_value=36)
if st.button("📩 Submit Spin"):
    st.session_state.spins.append(spin_input)
    st.success(f"✅ Spin `{spin_input}` recorded.")

    # 🧬 Trigger Seed Generation
    if len(st.session_state.spins) >= 4:
        digits = build_kaprekar_input(st.session_state.spins)
        seed = int("".join(map(str, digits)))
        unique_digits = sorted(set(digits))
        group_labels = [digit_to_group.get(d, "G?") for d in unique_digits]
        bet_nums = [num for g in group_labels for num in roulette_groups.get(g, [])]
        st.session_state.kaprekar_log.append((seed, digits))

        # 🎯 Hit Evaluation
        latest_spin = st.session_state.spins[-1]
        hit = latest_spin in bet_nums
        bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq)-1)]
        payout = bet_unit * 2 if hit else 0
        st.session_state.bank += payout - bet_unit
        st.session_state.bank_history.append(st.session_state.bank)
        st.session_state.bet_sizes.append(bet_unit)

        if hit:
            st.success(f"🎯 HIT! Spin `{latest_spin}` matched the suggested numbers.")
            st.session_state.spins.clear()
            st.session_state.fib_step = 0
            st.session_state.kaprekar_log.clear()
            st.session_state.bet_sizes.clear()
            st.session_state.bank_history = [st.session_state.bank]
            st.stop()
        else:
            st.info(f"❌ No match on `{latest_spin}`.")
            st.session_state.fib_step += 1

        # 📊 Display Seed Info
        st.subheader("🧬 Kaprekar Seed & Strategy")
        st.markdown(f"**Seed:** `{seed}`")
        st.markdown(f"**Unique Digits:** `{unique_digits}` → Groups: {group_labels}")
        st.markdown(f"**Suggested Numbers to Bet:** {sorted(bet_nums)}")
    else:
        st.warning("🕓 Waiting for 4 spins to activate Kaprekar strategy...")

# 💰 Bank Summary
st.subheader("💰 Bank Status")
st.markdown(f"### Bank: **€{st.session_state.bank}**")

# 📐 Fibonacci Progression
st.subheader("📐 Betting Progress (Fibonacci)")
step = st.session_state.fib_step
max_step = len(fib_seq) - 1
st.progress(min(step / max_step, 1.0))
st.markdown(f"**Step:** `{step}` of `{max_step}` → Bet Unit: `{fib_seq[min(step, max_step)]}`")

# 🕹️ Spin History
st.subheader("🕹️ Recent Spins")
spins = st.session_state.spins[-10:]
groups = [get_group(s) for s in spins]
group_nums = [int(g[1:]) if g and g.startswith("G") else None for g in groups]
df = pd.DataFrame({
    "Spin": spins,
    "Group": groups,
    "Group #": group_nums
})
st.dataframe(df, use_container_width=True)
