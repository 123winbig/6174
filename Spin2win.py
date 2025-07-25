import random

# 🎡 Group layout based on European roulette wheel
roulette_groups = {
    "G1": [32, 15, 19], "G2": [4, 21, 2], "G3": [25, 17, 34], "G4": [6, 27, 13],
    "G5": [36, 11, 30], "G6": [8, 23, 10], "G7": [5, 24, 16], "G8": [33, 1, 20],
    "G9": [14, 31, 9], "G10": [22, 18, 29], "G11": [7, 28, 12], "G12": [35, 3, 26], "G0": [0]
}

# 🔁 Reverse map: number → group digit
number_to_digit = {}
for group, numbers in roulette_groups.items():
    digit = int(group[1:]) if group != "G0" else 0
    for num in numbers:
        number_to_digit[num] = digit

# 🎲 Your actual live spins
live_spins = [
    33,19,36,17,11,35,3,29,0,9,18,29,0,13,14,10,36,14,6,33,16,34,9,28,24,11,20,
    29,2,31,35,11,3,26,18,22,28,14,3,11,29,26,18,27,14,4,4,36,16,1,10,24,33,10,
    9,12,12,11,34,1,33,0,22,30,21,35,22,28,8,4,36,24,19,25,16,3,18,19,4,15,2,20,
    4,24,17,12,21,3,21,29,12,1,17,9,11,24,18,35,25,15,14,27,13,14,22,17,34,0,24,
    36,26,22,35,9,17,1,24,8,25,12,27,16,15,15,30,31,34,28,9,35,3,29,12,21,10,2,
    20,11,17,32,11,29,9,15
]

# 💰 Betting parameters
base_unit = 2
bankroll = 1000
current_unit = base_unit
loss_streak = 0
lowest_bankroll = bankroll
highest_bankroll = bankroll

# 📊 Performance tracking
spin_history = []
seeds = []
total_hits = total_misses = 0

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
    global bankroll, loss_streak, current_unit, total_hits, total_misses
    if spin in bets:
        win = current_unit * 36
        bankroll += win
        loss_streak = 0
        current_unit = base_unit
        total_hits += 1
        return True, win - (current_unit * len(bets))
    else:
        bankroll -= current_unit * len(bets)
        loss_streak += 1
        total_misses += 1
        if loss_streak >= 2:
            current_unit *= 2
        return False, -(current_unit * len(bets))

# 🌀 Simulation
for idx, spin in enumerate(live_spins):
    spin_history.append(spin)

    if len(spin_history) >= 12:
        if idx % 12 == 0:
            seed, predictions = build_seed(spin_history)
            seeds.append((seed, predictions))

        current_seed, current_bets = seeds[-1]
        hit, net = apply_bet(spin, current_bets)
        bankroll_change = f"{'+' if net >= 0 else ''}€{net}"
        print(f"🎰 Spin: {spin} → {'HIT' if hit else 'MISS'} | {bankroll_change} | Bankroll: €{bankroll}")
        lowest_bankroll = min(lowest_bankroll, bankroll)
        highest_bankroll = max(highest_bankroll, bankroll)

# 📦 Final Results
print("\n📊 FINAL STRATEGY SUMMARY")
print(f"Total Spins Evaluated: {len(live_spins)}")
print(f"Total Hits: {total_hits} | Total Misses: {total_misses}")
print(f"Lowest Bankroll: €{lowest_bankroll}")
print(f"Highest Bankroll: €{highest_bankroll}")
print(f"Final Bankroll: €{bankroll}")
print(f"Net Profit: {'+' if bankroll - 1000 >= 0 else ''}€{bankroll - 1000}")
