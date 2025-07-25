import streamlit as st

# 🎡 Roulette group layout (European wheel)
roulette_groups = {
    "G1": [32, 15, 19], "G2": [4, 21, 2], "G3": [25, 17, 34], "G4": [6, 27, 13],
    "G5": [36, 11, 30], "G6": [8, 23, 10], "G7": [5, 24, 16], "G8": [33, 1, 20],
    "G9": [14, 31, 9], "G10": [22, 18, 29], "G11": [7, 28, 12], "G12": [35, 3, 26], "G0": [0]
}

# 🔁 Map each number to its group digit
number_to_digit = {
    num: int(group[1:]) if group != "G0" else 0
    for group, nums in roulette_groups.items()
    for num in nums
}

# 🎛️ Sidebar settings
st.sidebar.header("Betting Parameters")
base_unit = st.sidebar.number_input("Base Unit (€)", min_value=1, value=2, step=1)
initial_bankroll = st.sidebar.number_input("Starting Bankroll (€)", min_value=100, value=1000, step=50)

# 📦 Session state
if "spins" not in st.session_state:
    st.session_state.spins = []
    st.session_state.bankroll = initial_bankroll
    st.session_state.unit = base_unit
    st.session_state.loss_streak = 0
    st.session_state.last_bets = []
    st.session_state.hit_log = []

# 🧾 Spin Input
st.title("🎰 Live Roulette Betting Predictor")
new_spin = st.number_input("Enter latest spin result:", min_value=0, max_value=36, step=1)

if st.button("➕ Add Spin"):
    st.session_state.spins.append(int(new_spin))

    # Apply bet if prediction is available
    if st.session_state.last_bets:
        if new_spin in st.session_state.last_bets:
            win = st.session_state.unit * 36
            net = win - (st.session_state.unit * len(st.session_state.last_bets))
            st.session_state.bankroll += win
            st.session_state.unit = base_unit
            st.session_state.loss_streak = 0
            st.session_state.hit_log.append(("✅", net))
        else:
            loss = st.session_state.unit * len(st.session_state.last_bets)
            st.session_state.bankroll -= loss
            st.session_state.loss_streak += 1
            net = -loss
            st.session_state.hit_log.append(("❌", net))
            if st.session_state.loss_streak >= 2:
                st.session_state.unit *= 2

# 🧬 Generate Prediction
if len(st.session_state.spins) >= 12:
    digits = [number_to_digit.get(s, 0) for s in st.session_state.spins[-12:]]
    seed = int("".join(map(str, digits[-4:])))
    unique_digits = sorted(set(digits))
    bet_numbers = []
    for d in unique_digits:
        if d != 0:
            bet_numbers.extend(roulette_groups[f"G{d}"])
    st.session_state.last_bets = bet_numbers

    # 🔮 Display Prediction Panel
    st.subheader("🔮 Betting Prediction")
    st.write(f"**Seed Number**: `{seed}`")
    st.write(f"**Group Digits Used**: `{unique_digits}`")
    st.write(f"**Roulette Numbers Being Bet On**: `{sorted(bet_numbers)}`")

# 📊 Summary Panel
st.subheader("📊 Bankroll Summary")
st.write(f"Spins Entered: {len(st.session_state.spins)}")
st.write(f"Current Bankroll: €{st.session_state.bankroll}")
st.write(f"Current Bet Size: €{st.session_state.unit}")
hits = sum(1 for result, _ in st.session_state.hit_log if result == "✅")
misses = sum(1 for result, _ in st.session_state.hit_log if result == "❌")
st.write(f"Total Hits: {hits}")
st.write(f"Total Misses: {misses}")

if st.session_state.hit_log:
    st.subheader("📋 Recent Bet Results")
    for idx, (result, net) in enumerate(reversed(st.session_state.hit_log[-10:]), 1):
        st.write(f"{idx}. {result} | Net: {'+' if net >=0 else ''}€{net}")
