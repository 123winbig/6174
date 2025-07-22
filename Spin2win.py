import streamlit as st
import pandas as pd
import random

# 🎛 Sidebar Controls
st.sidebar.header("🎛 Session Controls")
spin_window = st.sidebar.selectbox("🧩 Spins for Kaprekar seed", [1, 2, 3, 4])
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# ✅ Reflect live bank update if session is fresh
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

# 🎰 Roulette Setup
roulette_groups = {
    "A": [32,15,19,4], "B": [21,2,25,17], "C": [34,6,27,13],
    "D": [36,11,30,8], "E": [23,10,5,24], "F": [16,33,1,20],
    "G": [14,31,9,22], "H": [18,29,7,28], "I": [12,35,3,26], "Z": [0]
}
group_digit_map = {g: i+1 for i, g in enumerate("ABCDEFGHI")}
fib_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34]

# 🧪 Helper Functions
def get_group(num):
    for g, nums in roulette_groups.items():
        if num in nums:
            return g
    return None

def build_kaprekar_input(spins):
    digits = []
    for s in spins:
        g = get_group(s)
        if g == "Z":
            st.sidebar.warning("🪞 Mirror Mode Triggered")
            continue
        digits.append(group_digit_map.get(g, 0))
    while len(digits) < 4:
        digits.append(random.randint(1, 9))
    return digits[:4]

def apply_mirror_mode(digits):
    return digits[::-1]

def kaprekar_transform(n):
    steps = []
    current = str(n).zfill(4)
    while current != "6174":
        asc = "".join(sorted(current))
        desc = "".join(sorted(current, reverse=True))
        result = int(desc) - int(asc)
        steps.append((current, desc, asc, result))
        current = str(result).zfill(4)
        if result == 6174:
            break
    return steps

# 📱 Layout Setup
st.set_page_config(page_title="Spin2Win: Kaprekar Roulette", layout="wide")
st.title("🎲 Spin2Win Dashboard")

# 🎯 Spin Input
spin_input = st.number_input("Enter Live Spin (0–36)", min_value=0, max_value=36)
if st.button("📩 Submit Spin", key="submit_spin"):
    st.session_state.spins.append(spin_input)

    if len(st.session_state.spins) >= spin_window:
        recent_spins = st.session_state.spins[-spin_window:]
        digits = build_kaprekar_input(recent_spins)
        if 0 in recent_spins:
            digits = apply_mirror_mode(digits)

        seed = int("".join(map(str, digits)))
        st.session_state.kaprekar_log.append((seed, digits))

        # 🧮 Bet Simulation
        bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq)-1)]
        hit = spin_input in random.sample(range(1, 37), 12)
        payout = bet_unit * 2 if hit else 0
        st.session_state.bank += payout - bet_unit
        st.session_state.bank_history.append(st.session_state.bank)
        st.session_state.bet_sizes.append(bet_unit)

        if hit:
            st.success("🎉 Hit! Resetting spins and bet sequence...")
            st.session_state.spins.clear()
            st.session_state.kaprekar_log.clear()
            st.session_state.fib_step = 0
            st.session_state.bank_history = [st.session_state.bank]
            st.session_state.bet_sizes.clear()
            st.stop()
        else:
            st.session_state.fib_step += 1

# 💰 Bank Summary
st.subheader("💰 Bank Summary")
st.markdown(f"### **€{st.session_state.bank}** remaining")

# 🧬 Kaprekar Seed
st.subheader("🧬 Kaprekar Seed")
if st.session_state.kaprekar_log:
    seed, digits = st.session_state.kaprekar_log[-1]
    digit_groups = [get_group(int(d)) for d in digits]
    digit_values = [group_digit_map.get(g, 0) for g in digit_groups]
    st.markdown(f"**Seed:** `{seed}` → Groups: {', '.join(digit_groups)} → Digits: {', '.join(map(str, digit_values))}")

# 🕹️ Last 4 Spins
st.subheader("🕹️ Last 4 Spins")
df = pd.DataFrame({
    "Spin": st.session_state.spins[-4:],
    "Group": [get_group(s) for s in st.session_state.spins[-4:]]
})
df["Digit"] = df["Group"].map(group_digit_map)
st.dataframe(df, use_container_width=True)

# 🔮 Prediction Zone
if len(st.session_state.spins) >= 36:
    st.subheader("🔮 Prediction Zone")
    group_counts = pd.Series([get_group(s) for s in st.session_state.spins]).value_counts()
    st.dataframe(group_counts)
