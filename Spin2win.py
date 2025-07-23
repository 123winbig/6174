import streamlit as st
import pandas as pd
import random

# 🎛 Initial Setup
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# ✅ Session State
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.kaprekar_log = []
    st.session_state.bet_sizes = []
    st.session_state.bank_history = [starting_bank]

# 🔄 Manual Reset
if st.sidebar.button("🔄 Manual Reset"):
    st.session_state.spins.clear()
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.kaprekar_log.clear()
    st.session_state.bet_sizes.clear()
    st.session_state.bank_history = [starting_bank]
    st.stop()

# 🎰 Group Definitions
roulette_groups = {
    "G1": [1, 2, 3], "G2": [4, 5, 6], "G3": [7, 8, 9],
    "G4": [10,11,12], "G5": [13,14,15], "G6": [16,17,18],
    "G7": [19,20,21], "G8": [22,23,24], "G9": [25,26,27],
    "G10": [28,29,30], "G11": [31,32,33], "G12": [34,35,36],
    "G0": [0]
}
digit_to_group = {i: f"G{i}" for i in range(1, 13)}
fib_seq = [1,1,2,3,5,8,13,21,34]

# 🧠 Utility Functions
def get_group(num):
    for g, nums in roulette_groups.items():
        if num in nums:
            return g
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

# 🧩 Page Setup
st.set_page_config(page_title="Spin2Win — Fixed Seed Mode", layout="wide")
st.title("🎲 Spin2Win — 36-Spin Kaprekar System")

# 🎯 Spin Entry
spin_input = st.number_input("Enter Spin (0–36)", min_value=0, max_value=36)
if st.button("📩 Submit Spin"):
    st.session_state.spins.append(spin_input)
    st.success(f"✅ Spin `{spin_input}` saved.")

# 💬 Check for Seed Activation
kaprekar_ready = len(st.session_state.spins) >= 36
if not kaprekar_ready:
    st.warning(f"🕓 {len(st.session_state.spins)}/36 spins entered. Waiting for full history to activate strategy.")
else:
    # Generate Seed Logic
    recent_spins = st.session_state.spins[-36:]
    digits = build_kaprekar_input(recent_spins)
    seed = int("".join(map(str, digits)))
    unique_digits = sorted(set(digits))
    group_labels = [digit_to_group.get(d, "G?") for d in unique_digits]
    bet_nums = [num for g in group_labels for num in roulette_groups.get(g, [])]
st.subheader("🧬 Kaprekar Seed & Betting Breakdown")
st.markdown(f"**Seed:** `{seed}`")
st.markdown(f"**Unique Digits:** `{unique_digits}` → Groups: {group_labels}")
st.markdown(f"**Suggested Numbers to Bet:** {sorted(bet_nums)}")    
    st.session_state.kaprekar_log.append((seed, digits))

    # ✅ HIT Logic — Only After Seed
    latest_spin = st.session_state.spins[-1]
    hit = latest_spin in bet_nums

    bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq)-1)]
    payout = bet_unit * 2 if hit else 0
    st.session_state.bank += payout - bet_unit
    st.session_state.bank_history.append(st.session_state.bank)
    st.session_state.bet_sizes.append(bet_unit)

    if hit:
        st.success(f"🎯 HIT! Spin `{latest_spin}` matched your bets.")
        st.session_state.spins.clear()
        st.session_state.fib_step = 0
        st.session_state.kaprekar_log.clear()
        st.session_state.bet_sizes.clear()
        st.session_state.bank_history = [st.session_state.bank]
        st.stop()
    else:
        st.info(f"❌ No match on `{latest_spin}`.")
        st.session_state.fib_step += 1

# 💰 Bank Summary
st.subheader("💰 Bank Summary")
st.markdown(f"### Bank: **€{st.session_state.bank}**")

# 📐 Fibonacci Tracker
st.subheader("📐 Fibonacci Progress")
step = st.session_state.fib_step
max_step = len(fib_seq) - 1
st.progress(min(step / max_step, 1.0))
st.markdown(f"**Step:** `{step}` of `{max_step}` → Bet Unit: `{fib_seq[min(step, max_step)]}`")
