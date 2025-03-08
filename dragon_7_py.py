import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time  

st.set_page_config(page_title="Dragon 7 Betting Simulator", layout="wide")

class Dragon7Simulator:
    def __init__(self, total_decks=8, bankroll=1000):
        self.running_count = 0
        self.total_decks = total_decks
        self.remaining_decks = total_decks
        self.cards_dealt = 0
        self.history = []
        self.dragon7_occurrences = []
        self.current_hand = {"Player": [], "Banker": []}
        self.remaining_cards = {i: 4 * 8 for i in range(1, 11)}
        self.bankroll = bankroll
        self.bet_amount = 25  
        self.auto_bet = False  

    def update_count(self, card):
        card_values = {1: 0, 2: 0, 3: 0, 4: -1, 5: -1, 6: -1, 7: -1, 8: 2, 9: 2, 10: 0}
        self.running_count += card_values.get(card, 0)
        self.cards_dealt += 1
        self.update_decks()
        if self.remaining_cards[card] > 0:
            self.remaining_cards[card] -= 1

    def update_decks(self):
        self.remaining_decks = max(1, self.total_decks - (self.cards_dealt / 52))

    def get_true_count(self):
        return self.running_count / self.remaining_decks

    def get_dragon7_probability(self):
        base_probability = 2.3  
        tc_factor = self.get_true_count() * 1.5  
        key_card_weight = sum(self.remaining_cards[i] for i in [8, 9]) / (self.remaining_decks * 52) * 10  
        probability = min(base_probability + tc_factor + key_card_weight, 25)  
        return probability

    def predict_dragon7(self):
        if self.get_true_count() >= 4:
            return "🔥 BET NOW! (TC ≥ 4, +8.03% Edge)"
        elif self.get_true_count() >= 3:
            return "⚠️ Almost There! (TC = 3)"
        else:
            return "❌ Not Yet"

    def place_bet(self):
        if self.get_true_count() >= 4:
            bet_result = "✅ WIN" if self.check_dragon7() else "❌ LOSE"
            win_amount = self.bet_amount * 40 if bet_result == "✅ WIN" else -self.bet_amount
            self.bankroll += win_amount

            self.history.append({
                "Bet Amount": self.bet_amount,
                "Result": bet_result,
                "New Bankroll": self.bankroll
            })

    def check_dragon7(self):
        banker_hand = self.current_hand["Banker"]
        return len(banker_hand) == 3 and sum(banker_hand) % 10 == 7

    def add_card_to_hand(self, role, card):
        if role in self.current_hand:
            self.current_hand[role].append(card)
            self.update_count(card)

    def finalize_hand(self):
        banker_hand = self.current_hand["Banker"]
        player_hand = self.current_hand["Player"]
        banker_total = sum(banker_hand) % 10  
        player_total = sum(player_hand) % 10

        winner = "Banker" if banker_total > player_total else "Player" if player_total > banker_total else "Tie"
        is_dragon7 = self.check_dragon7()

        if self.auto_bet and self.get_true_count() >= 4:
            self.place_bet()

        self.history.append({
            "Hand": len(self.history) + 1,
            "Player Cards": str(player_hand),
            "Banker Cards": str(banker_hand),
            "Player Total": player_total,
            "Banker Total": banker_total,
            "Winner": winner,
            "Dragon 7": "✅ Yes" if is_dragon7 else "❌ No",
            "True Count": self.get_true_count()
        })

        self.current_hand = {"Player": [], "Banker": []}

# Streamlit UI
st.title("🐉 Dragon 7 Betting Simulator")
st.write("Track baccarat hands, place bets, and manage your bankroll!")

if "simulator" not in st.session_state:
    st.session_state.simulator = Dragon7Simulator()

simulator = st.session_state.simulator

# Bankroll & Betting UI
st.subheader(f"💰 Bankroll: ${simulator.bankroll}")
bet_options = [10, 25, 50, 100, 200]
simulator.bet_amount = st.radio("🎲 Select Bet Amount:", bet_options, index=1)
simulator.auto_bet = st.checkbox("🔄 Auto-Bet When TC ≥ 4")

st.subheader(f"📉 True Count: {simulator.get_true_count():.2f}")
st.subheader(f"🎯 Dragon 7 Prediction: {simulator.predict_dragon7()}")
st.progress(simulator.get_dragon7_probability() / 25)

# Hand Display
st.write("### 🃏 Current Hand")
st.write(f"**Player:** {simulator.current_hand['Player']}")
st.write(f"**Banker:** {simulator.current_hand['Banker']}")

# Add Cards UI
st.write("### ✏️ Add Cards")
col1, col2 = st.columns(2)
with col1:
    st.write("**Player:**")
    for card in range(1, 11):
        if st.button(str(card), key=f"p{card}"):
            simulator.add_card_to_hand("Player", card)
            st.rerun()
with col2:
    st.write("**Banker:**")
    for card in range(1, 11):
        if st.button(str(card), key=f"b{card}"):
            simulator.add_card_to_hand("Banker", card)
            st.rerun()

# Finalize Hand
if st.button("✅ Finalize Hand"):
    with st.spinner("Processing..."):
        time.sleep(0.3)  
        simulator.finalize_hand()
        st.rerun()

# Betting History
with st.expander("📜 Betting History", expanded=False):
    if simulator.history:
        df = pd.DataFrame(simulator.history)
        st.dataframe(df, height=200)

# Reset Game
if st.button("🔄 Reset"):
    with st.spinner("Resetting..."):
        time.sleep(0.3)
        st.session_state.simulator = Dragon7Simulator()
        st.rerun()
