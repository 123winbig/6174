import streamlit as st

# 🎡 European roulette layout grouped
roulette_groups = {
    "G1": [32, 15, 19], "G2": [4, 21, 2], "G3": [25, 17, 34], "G4": [6, 27, 13],
    "G5": [36, 11, 30], "G6": [8, 23, 10], "G7": [5, 24, 16], "G8": [33, 1, 20],
    "G9": [14, 31, 9], "G10": [22, 18, 29], "G11": [7, 28, 12], "G12": [35, 3, 26], "G0": [0]
}

# 🔁 Reverse map: number → group digit
number_to_digit = {
    num: int(group[1:]) if group != "G0" else 0
    for group, nums in roulette_groups.items()
    for num in nums
}

# 🎛️ Sidebar betting setup
st.sidebar.header("🎛️ Betting Parameters")
base_unit = st.sidebar.number_input("Base Unit (€)", min_value=1, value=2)
initial_bankroll = st.sidebar.number_input("Starting Bankroll (€)", min_value=100, value=1000)

# 🧠 Initialize session state
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.bankroll = initial_bankroll
    st.session_state.unit = base_unit
    st.session_state.loss_streak = 0
    st.session_state.predicted_numbers = []
    st.session_state.seed = None
    st.session_state.bet_history = []

# 🧾 Input new spin
st.title("🎰 Live Seed-Based Roulette Predictor")
new_spin = st.number_input("Enter roulette result:", min_value=0, max_value=36, step=1)

if st.button("➕ Add Spin"):
    spin = int(new_spin)
    st.session_state.spins.append(spin)

    # Evaluate bet if predictions exist
    if st.session_state.predicted_numbers:
        if spin in st.session_state.predicted_numbers:
            win = st.session_state.unit * 36
            net = win - st.session_state.unit * len(st.session_state.predicted_numbers)
            st.session_state.bankroll += win
            st.session_state.unit = base_unit
            st.session_state.loss_streak = 0
            st.session_state.bet_history.append(("✅", spin, net))
        else:
            loss = st.session_state.unit * len(st.session_state.predicted_numbers)
            st.session_state.bankroll -= loss
            st.session_state.loss_streak += 1
            net = -loss
            st.session_state.bet_history.append(("❌", spin, net))
            if st.session_state.loss_streak >= 2:
                st.session_state.unit *= 2

    # Generate prediction only after 12 spins
    if len(st.session_state.spins) >= 12:
        last_12 = st.session_state.spins[-12:]
        digits = [number_to_digit.get(n, 0) for n in last_12]
        seed_digits = digits[-4:]
        seed = int("".join(map(str, seed_digits)))
        unique_digits = sorted(set(seed_digits))
        predictions = []
        for d in unique_digits:
            if d != 0:
                predictions.extend(roulette_groups[f"G{d}"])
        st.session_state.seed = seed
        st.session_state.predicted_numbers = sorted(set(predictions))

# 🔮 Prediction summary
if st.session_state.seed:
    st.subheader("🔮 Current Prediction")
    st.write(f"**Seed Number:** `{st.session_state.seed}`")
    digits_in_seed = [int(d) for d in str(st.session_state.seed)]
    st.write(f"**Group Digits (unique):** `{sorted(set(digits_in_seed))}`")
    st.write(f"**Roulette Numbers Bet On:** `{st.session_state.predicted_numbers}`")

# 📊 Bankroll overview
st.subheader("📊 Strategy Dashboard")
st.write(f"Spins Entered: `{len(st.session_state.spins)}`")
st.write(f"Bankroll: `€{st.session_state.bankroll}`")
st.write(f"Current Bet Size: `€{st.session_state.unit}`")
hits = sum(1 for r, _, _ in st.session_state.bet_history if r == "✅")
misses = sum(1 for r, _, _ in st.session_state.bet_history if r == "❌")
st.write(f"Total Hits: `{hits}` | Total Misses: `{misses}`")

# 📋 Recent result log
if st.session_state.bet_history:
    st.subheader("📋 Recent Bet Outcomes")
    for result, spin, net in reversed(st.session_state.bet_history[-10:]):
        st.write(f"{result} → Spin `{spin}` | Net: {'+' if net >= 0 else ''}€{net}")
