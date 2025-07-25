import random

# 🎡 Group mapping based on European wheel layout
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

# 📦 Reverse mapping: number → group digit (1–12)
number_to_digit = {}
for key, values in roulette_groups.items():
    if key != "G0":
        digit = int(key[1:])
        for num in values:
            number_to_digit[num] = digit
    else:
        for num in values:
            number_to_digit[num] = 0

# 💰 Manual bank setup
bankroll = 500  # Set initial bankroll
bet_unit = 2    # Fixed bet per number

# ⏱ Seed & evaluation tracking
spin_history = []
seeds = []
total_hits = total_misses = total_profit = 0

def map_seed_from_spins(spins):
    digits = [number_to_digit.get(num, 0) for num in spins[-12:]]
    seed = int("".join(map(str, digits[-4:])))
    unique_digits = set(digits)
    bet_numbers = []
    for group_key in [f"G{d}" for d in unique_digits if d != 0]:
        bet_numbers.extend(roulette_groups.get(group_key, []))
    return seed, bet_numbers

def evaluate_spin(spin, bet_numbers):
    global bankroll, total_hits, total_misses, total_profit
    if spin in bet_numbers:
        payout = bet_unit * 36
        bankroll += payout
        total_profit += (payout - bet_unit)
        total_hits += 1
        return True, payout - bet_unit
    else:
        bankroll -= bet_unit
        total_profit -= bet_unit
        total_misses += 1
        return False, -bet_unit

def display_seed_stats(seed_num, bet_numbers, hits, misses, profit):
    total = hits + misses
    win_rate = (hits / total) * 100 if total else 0
    print("\n📦 Seed Summary Box")
    print(f"Seed #: {seed_num}")
    print(f"Predicted: {bet_numbers}")
    print(f"Hits: {hits}   Misses: {misses}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Profit: {'+' if profit >= 0 else ''}€{profit}")

# 🌀 Main simulation loop
def simulate_spin(spin):
    spin_history.append(spin)

    if len(spin_history) >= 12:
        if len(seeds) == 0 or len(spin_history) % 12 == 0:
            seed_num, predicted_bets = map_seed_from_spins(spin_history)
            seeds.append({
                'seed': seed_num,
                'bets': predicted_bets,
                'hits': 0,
                'misses': 0,
                'profit': 0
            })

        current_seed = seeds[-1]
        hit, profit = evaluate_spin(spin, current_seed['bets'])
        if hit:
            current_seed['hits'] += 1
        else:
            current_seed['misses'] += 1
        current_seed['profit'] += profit
        display_seed_stats(current_seed['seed'], current_seed['bets'],
                           current_seed['hits'], current_seed['misses'],
                           current_seed['profit'])

    print(f"\n🎯 Spin Entered: {spin}")
    print(f"💰 Bankroll: €{bankroll}")

# 👇 Example usage
sample_spins = [32, 4, 25, 6, 36, 8, 5, 33, 14, 22, 7, 35, 13, 19, 21, 17]

for s in sample_spins:
    simulate_spin(s)

# 📊 Final Stats
print("\n🔚 FINAL RESULTS")
print(f"Total Spins: {len(spin_history)}")
print(f"Hits: {total_hits}  Misses: {total_misses}")
print(f"Final Bankroll: €{bankroll}")
print(f"Net Profit: {'+' if total_profit >=0 else ''}€{total_profit}")
