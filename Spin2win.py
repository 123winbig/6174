import streamlit as st
import pandas as pd
import random

# ⚙️ Sidebar Controls
st.sidebar.header("🎛 Session Controls")

# 🏦 Starting bank input (saved separately)
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# 🔄 Manual reset
if st.sidebar.button("🔄 Manual Reset"):
    st.session_state.spins = []
    st.session_state.kaprekar_log = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank  # pulled directly at reset moment
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes = []
    st.experimental_rerun()

# 🚀 Session Init
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.kaprekar_log = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes = []

# 🔁 Reset manually
if st.sidebar.button("🔄 Manual Reset"):
    st.session_state.spins = []
    st.session_state.kaprekar_log = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes = []
    st.experimental_rerun()

# 🎯 Group map
roulette_groups = {
    "A": [32,15,19,4],"B": [21,2,25,17],"C": [34,6,27,13],
    "D": [36,11,30,8],"E": [23,10,5,24],"F": [16,33,1,20],
    "G": [14,31,9,22],"H": [18,29,7,28],"I": [12,35,3,26],"Z": [0]
}
group_digit_map = {group: i+1 for i, group in enumerate("ABCDEFGHI")}
fib_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34]

# 🧠 Functions
def get_group(n):
    for g, nums in roulette_groups.items():
        if n in nums:
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

def apply_mirror_mode(digits): return digits[::-1]

def kaprekar_transform(n):
    steps = []
    current = str(n).zfill(4)
    while current != "6174":
        asc = "".join(sorted(current))
        desc = "".join(sorted(current, reverse=True))
        result = int(desc) - int(asc)
        steps.append((current, desc, asc, result))
        current = str(result).zfill(4)
        if result == 6174: break
    return steps

# 🎲 Page Setup
st.set_page_config(page_title="Spin2Win: Kaprekar Roulette", layout="wide")
st.title("🎲 Spin2Win Dashboard")

# 👆 Live Spin Input
spin_input = st.number_input("Enter Live Spin (0–36)", min_value=0, max_value=36)
if st.button("📩 Submit Spin"):
    st.session_state.spins.append(spin_input)

    if len(st.session_state.spins) >= spin_window:
        recent_spins = st.session_state.spins[-spin_window:]
        digits = build_kaprekar_input(recent_spins)
        if 0 in recent_spins:
            digits = apply_mirror_mode(digits)

        seed_num = int("".join(map(str, digits)))
        st.session_state.kaprekar_log.append((seed_num, digits))

        bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq)-1)]
        hit = spin_input in random.sample(range(1, 37), 12)
        payout = bet_unit * 2 if hit else 0
        st.session_state.bank += payout - bet_unit
        st.session_state.bank_history.append(st.session_state.bank)
        st.session_state.bet_sizes.append(bet_unit)

        # Auto reset system on hit
        if hit:
            st.success("🎉 Hit detected! Resetting system.")
            st.session_state.spins = []
            st.session_state.kaprekar_log = []
            st.session_state.fib_step = 0
            st.session_state.bank = starting_bank
            st.session_state.bank_history = [starting_bank]
            st.session_state.bet_sizes = []
            st.experimental_rerun()
        else:
            st.session_state.fib_step += 1

# 💰 Bank Display
st.subheader("💵 Bank Status")
st.markdown(f"### **€{st.session_state.bank}** remaining")

# 🧬 Kaprekar Seed Display (compact)
st.subheader("🧬 Kaprekar Seed")
if st.session_state.kaprekar_log:
    seed_num, seed_digits = st.session_state.kaprekar_log[-1]
    seed_groups = [get_group(int(d)) for d in seed_digits]
    st.markdown(f"Seed: `{seed_num}` → Groups: {', '.join(seed_groups)}")

# 🕹️ Recent Spins View
st.subheader("🕹️ Recent Spins")
df = pd.DataFrame({
    "Spin": st.session_state.spins[-4:],
    "Group": [get_group(s) for s in st.session_state.spins[-4:]]
})
st.dataframe(df, use_container_width=True)

# 🔮 Prediction Zone
if len(st.session_state.spins) >= 36:
    st.subheader("🔮 Prediction Zone")
    group_counts = pd.Series([get_group(s) for s in st.session_state.spins]).value_counts()
    st.write("Most frequent groups:")
    st.dataframe(group_counts)
