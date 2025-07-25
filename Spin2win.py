import streamlit as st
import pandas as pd
import random

# 🎡 Group layout based on European roulette wheel
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

# 🎲 User input from sidebar
st.sidebar.header("🎛️ Betting Parameters")
base_unit = st.sidebar.number_input("Base Unit (€)", min_value=1, value=2, step=1)
bankroll = st.sidebar.number_input("Starting Bankroll (€)", min_value=100, value=1000, step=50)

# 📊 App title
st.title("🎰 Spin2Win Roulette Simulator")

# 📦 Live spins (static for now, could be expanded to live input later)
live_spins = random.choices(list(number_to_digit.keys()), k=120)

# 📊 Initialize
current_unit = base_unit
loss_streak = 0
lowest_bankroll = highest_bankroll = bankroll
spin_history = []
seeds = []
hit_log = []
net_log = []

def build_seed(spins):
    digits = [number_to_digit.get(s, 0) for s in spins[-12:]]
    seed = int("".join(map(str, digits[-4:])))
    unique_digits = set(digits)
    bet_numbers = []
    for d in unique_digits:
        if d != 0:
            bet_numbers.extend(roulette_groups[f"G{d}"])
    return seed, bet_numbers

def apply_bet(spin, bets):
    global bankroll, loss_streak, current_unit
    if spin in bets:
        win = current_unit * 36
        bankroll += win
        loss_streak = 0
        net = win - (current_unit * len(bets))
        current_unit = base_unit
        return True, net
    else:
        bankroll -= current_unit * len(bets)
        loss_streak += 1
        if loss_streak >= 2:
            current_unit *= 2
        net = -(current_unit * len(bets))
        return False, net

# 🌀 Simulation loop
for idx, spin in enumerate(live_spins):
    spin_history.append(spin)

    if len(spin_history) >= 12:
        if idx % 12 == 0:
            seed, predictions = build_seed(spin_history)
            seeds.append((seed, predictions))
            if seeds:
    current_seed, current_bets = seeds[-1]
    hit, net = apply_bet(spin, current_bets)
    hit_log.append(hit)
    net_log.append(net)
    lowest_bankroll = min(lowest_bankroll, bankroll)
    highest_bankroll = max(highest_bankroll, bankroll)
current_seed, current_bets = seeds[-1]
        hit, net = apply_bet(spin, current_bets)
        hit_log.append(hit)
        net_log.append(net)
        lowest_bankroll = min(lowest_bankroll, bankroll)
        highest_bankroll = max(highest_bankroll, bankroll)

# 📈 Chart and summary
df = pd.DataFrame({
    "Spin": spin_history,
    "Hit": ["✅" if h else "❌" for h in hit_log],
    "Net": net_log
})

st.subheader("📊 Bankroll Over Time")
bankroll_values = [bankroll - sum(net_log[:i]) for i in range(len(net_log)+1)]
st.line_chart(bankroll_values)

st.subheader("📋 Strategy Summary")
st.write(f"Total Spins: {len(spin_history)}")
st.write(f"Total Hits: {sum(hit_log)}")
st.write(f"Total Misses: {len(hit_log) - sum(hit_log)}")
st.write(f"Lowest Bankroll: €{lowest_bankroll}")
st.write(f"Highest Bankroll: €{highest_bankroll}")
st.write(f"Final Bankroll: €{bankroll}")
net_profit = bankroll - st.sidebar.number_input("Initial Bankroll for Summary", value=1000)
st.write(f"Net Profit: {'+' if net_profit >= 0 else ''}€{net_profit}")
