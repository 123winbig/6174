import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# 🎛 Sidebar configuration
st.sidebar.header("🎛 Session Controls")

spin_window = st.sidebar.selectbox("🧩 Spins used for Kaprekar seed", [1, 2, 3, 4])
starting_bank = st.sidebar.number_input("🏦 Starting Bank (€)", min_value=100, value=500, step=50)

# Initialize session state
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.kaprekar_log = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes = []

# 🔄 Reset button
if st.sidebar.button("🔄 Reset Session"):
    st.session_state.spins = []
    st.session_state.kaprekar_log = []
    st.session_state.fib_step = 0
    st.session_state.bank = starting_bank
    st.session_state.bank_history = [starting_bank]
    st.session_state.bet_sizes = []
    st.experimental_rerun()

# 🎲 Wheel group mapping
roulette_groups = {
    "A": [32, 15, 19, 4],
    "B": [21, 2, 25, 17],
    "C": [34, 6, 27, 13],
    "D": [36, 11, 30, 8],
    "E": [23, 10, 5, 24],
    "F": [16, 33, 1, 20],
    "G": [14, 31, 9, 22],
    "H": [18, 29, 7, 28],
    "I": [12, 35, 3, 26],
    "Z": [0]  # Zero group (mirror mode)
}
group_digit_map = {group: i + 1 for i, group in enumerate("ABCDEFGHI")}
fib_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34]

# 🔍 Helper functions
def get_group(num):
    for group, nums in roulette_groups.items():
        if num in nums:
            return group
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

# 🧠 Main display
st.set_page_config(page_title="Spin2Win: Kaprekar Roulette Tracker", layout="wide")
st.title("🎲 Spin2Win: Kaprekar Roulette Tracker")

# 👉 Manual spin input
spin_input = st.number_input("🎯 Enter Live Spin (0–36)", min_value=0, max_value=36)
if st.button("📩 Submit Spin"):
    st.session_state.spins.append(spin_input)

    if len(st.session_state.spins) >= spin_window:
        recent_spins = st.session_state.spins[-spin_window:]
        digits = build_kaprekar_input(recent_spins)

        if 0 in recent_spins:
            digits = apply_mirror_mode(digits)

        seed = int("".join(map(str, digits)))
        steps = kaprekar_transform(seed)
        st.session_state.kaprekar_log.append((seed, steps))

        # Simulate betting logic
        bet_unit = fib_seq[min(st.session_state.fib_step, len(fib_seq) - 1)]
        hit = spin_input in random.sample(range(1, 37), 12)
        payout = bet_unit * 2 if hit else 0
        st.session_state.bank += payout - bet_unit
        st.session_state.bank_history.append(st.session_state.bank)
        st.session_state.bet_sizes.append(bet_unit)
        st.session_state.fib_step = 0 if hit else st.session_state.fib_step + 1

# 💬 Show recent spins
st.subheader("🕹️ Recent Spins")
df = pd.DataFrame({"Spin": st.session_state.spins})
df["Group"] = df["Spin"].apply(get_group)
st.dataframe(df.tail(4), use_container_width=True)

# 💡 Show current Kaprekar seed
st.subheader("🧬 Kaprekar Seed")
if st.session_state.kaprekar_log:
    last_seed, _ = st.session_state.kaprekar_log[-1]
    st.markdown(f"### 🎯 **Seed Number:** `{last_seed}`")

# 📊 Bank + Bet Progress
st.subheader("📈 Bank & Bet Tracker")
fig, ax = plt.subplots()
ax.plot(st.session_state.bank_history, label="Bank (€)", color="green")
ax.plot(st.session_state.bet_sizes, label="Fibonacci Bet", linestyle='--', color="orange")
ax.legend()
st.pyplot(fig)

# 🔮 Predict most frequent group
if len(st.session_state.spins) >= 36:
    st.subheader("🔮 Prediction Zone")
    group_series = df["Group"].value_counts().sort_values(ascending=False)
    st.write("Most frequent groups:")
    st.dataframe(group_series)
