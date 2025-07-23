import streamlit as st
import pandas as pd
import random

# 🎛 Sidebar Settings
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# 🌟 Session Setup
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.kaprekar_log = []
    st.session_state.bet_sizes = []
    st.session_state.bank_history = [starting_bank]
elif not st.session_state.spins and st.session_state.bank != starting_bank:
    st.session_state.bank = starting_bank

# 🔄 Reset Button
if st.sidebar.button("🔄 Manual Reset"):
    st.session_state.spins.clear()
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.kaprekar_log.clear()
    st.session_state.bet_sizes.clear()
    st.session_state.bank_history = [starting_bank]
    st.stop()

# 🎡 Wheel-Based Group Mapping (European-style layout)
roulette_groups = {
    "G1": [32, 15, 19],     # Cluster near top right
    "G2": [4, 21, 2],       # Black-Red alternation
    "G3": [25, 17, 34],     # Spaced opposite 19
    "G4": [6, 27, 13],      # Low-mid black/red pairings
    "G5": [36, 11, 30],     # Outer red arc cluster
    "G6": [8, 23, 10],      # Near left of wheel center
    "G7": [5, 24, 16],      # Black sector grouping
    "G8": [33, 1, 20],      # Near zero cluster
    "G9": [14, 31, 9],      # Red-heavy set
    "G10": [22, 18, 29],    # Opposite green zones
    "G11": [7, 28, 12],     # Balanced low-mid
    "G12": [35, 3, 26],     # Spaced lower reds
    "G0": [0]               # Single green zero
}

digit_to_group = {i: f"G{i}" for i in range(1, 13)}
fib_seq = [1,1,2,3,5,8,13,21,34]

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

# 🎲 Page Setup
st.set_page_config(page_title="Spin2Win — Live Mode", layout="wide")
st.title("🎰 Spin2Win — Real-Time Kaprekar Strategy")

# 🎯 Spin Input
spin_input = st.number_input("Enter Spin (0–36)", min_value=0, max_value=36)
if st.button("📩 Submit Spin"):
    st.session_state.spins.append(spin_input)

    # 🧬 Trigger Seed Generation if 4+ Spins
    if len(st.session_state.spins) >= 4:
        digits = build_kaprekar_input(st.session_state.spins)
        seed = int("".join(map(str, digits)))
        unique_digits = sorted(set(digits))
        group_labels = [digit_to_group.get(d, "G?") for d in unique_digits]
        bet_nums = [num for g in group_labels for num in roulette_groups.get(g, [])]
        st.session_state.kaprekar_log.append((seed, digits))

        # 🧮 Hit Evaluation
        latest_spin = st.session_state.spins[-1]
        hit = latest_spin in bet_nums
        bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq)-1)]
        payout = bet_unit * 2 if hit else 0
        st.session_state.bank += payout - bet_unit
        st.session_state.bank_history.append(st.session_state.bank)
        st.session_state.bet_sizes.append(bet_unit)

        # 🔁 Reset on Hit
        if hit:
            st.success(f"🎯 HIT! Spin `{latest_spin}` matched your suggested numbers.")
            st.session_state.spins.clear()
            st.session_state.fib_step = 0
            st.session_state.kaprekar_log.clear()
            st.session_state.bet_sizes.clear()
            st.session_state.bank_history = [st.session_state.bank]
            st.stop()
        else:
            st.info(f"❌ No match on `{latest_spin}`.")
            st.session_state.fib_step += 1

        # 📊 Display Seed & Bets
        st.subheader("🧬 Kaprekar Seed & Suggested Bets")
        st.markdown(f"**Seed:** `{seed}`")
        st.markdown(f"**Unique Digits:** `{unique_digits}` → Groups: {group_labels}")
        st.markdown(f"**Suggested Numbers to Bet:** {sorted(bet_nums)}")
    else:
        st.warning("🕓 Waiting for 4 spins to activate strategy...")

# 💰 Bank Display
st.subheader("💰 Bank Summary")
st.markdown(f"### Bank: **€{st.session_state.bank}**")

# 📐 Fibonacci Tracker
st.subheader("📐 Fibonacci Progress")
step = st.session_state.fib_step
max_step = len(fib_seq) - 1
st.progress(min(step / max_step, 1.0))
st.markdown(f"**Step:** `{step}` of `{max_step}` → Bet Unit: `{fib_seq[min(step, max_step)]}`")

# 🕹️ Spin History
st.subheader("🕹️ Spin History")
spins = st.session_state.spins[-10:]
groups = [get_group(s) for s in spins]
digits_view = [int(g[1:]) if g and g.startswith("G") else 0 for g in groups]
df = pd.DataFrame({
    "Spin": spins,
    "Group": groups,
    "Group Number": digits_view
})
st.dataframe(df, use_container_width=True)
