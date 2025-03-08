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

    def add_card_to_hand(self, role, card):
        if role in self.current_hand:
            self.current_hand[role].append(card)
            self.update_count(card)

    def predict_winner(self):
        """ Uses official EZ Baccarat rules to predict the winner """
        player_hand = self.current_hand["Player"]
        banker_hand = self.current_hand["Banker"]

        if not player_hand or not banker_hand:
            return "Waiting for more cards..."

        player_total = sum(player_hand) % 10
        banker_total = sum(banker_hand) % 10

        # **Natural Win (8 or 9)**
        if player_total in [8, 9] or banker_total in [8, 9]:
            if player_total > banker_total:
                return "🏆 **Predicted Winner: Player (Natural Win)**"
            elif banker_total > player_total:
                return "🏆 **Predicted Winner: Banker (Natural Win)**"
            else:
                return "🔄 **Predicted Result: Tie (Both Natural)**"

        # **Third Card Drawing Rules for Player**
        if len(player_hand) == 2:
            if player_total in [0, 1, 2, 3, 4, 5]:
                return "👀 **Prediction Pending: Player Draws Third Card**"
            elif player_total in [6, 7]:
                if banker_total <= 5:
                    return "👀 **Prediction Pending: Banker Draws Third Card**"
                return "🏆 **Predicted Winner: Player (Stands at 6 or 7)**"

        # **Third Card Drawing Rules for Banker**
        if len(player_hand) == 3:
            player_third_card = player_hand[2]

            banker_draws = False
            if banker_total <= 2:
                banker_draws = True
            elif banker_total == 3 and player_third_card != 8:
                banker_draws = True
            elif banker_total == 4 and player_third_card in [2, 3, 4, 5, 6, 7]:
                banker_draws = True
            elif banker_total == 5 and player_third_card in [4, 5, 6, 7]:
                banker_draws = True
            elif banker_total == 6 and player_third_card in [6, 7]:
                banker_draws = True

            if banker_draws:
                return "👀 **Prediction Pending: Banker Draws Third Card**"
            else:
                if player_total > banker_total:
                    return "🏆 **Predicted Winner: Player**"
                elif banker_total > player_total:
                    return "🏆 **Predicted Winner: Banker**"
                else:
                    return "🔄 **Predicted Result: Tie**"

        return "🔄 **Waiting for third card rules to apply**"

# Streamlit UI
st.title("🐉 Dragon 7!")
st.write("Track baccarat hands, predict winners, and manage your bankroll!")

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

# **Winner Prediction**
st.write("### 🔮 Predicted Winner")
st.subheader(simulator.predict_winner())

# **Easier Card Input Grid**
st.write("### ✏️ Add Cards Quickly")

col1, col2 = st.columns(2)
with col1:
    st.write("**Player Cards**")
    card = st.radio("Select Card", list(range(1, 11)), horizontal=True, key="p_select")
    if st.button("➕ Add to Player"):
        simulator.add_card_to_hand("Player", card)
        st.rerun()

with col2:
    st.write("**Banker Cards**")
    card = st.radio("Select Card", list(range(1, 11)), horizontal=True, key="b_select")
    if st.button("➕ Add to Banker"):
        simulator.add_card_to_hand("Banker", card)
        st.rerun()

# Reset Game
if st.button("🔄 Reset"):
    st.session_state.simulator = Dragon7Simulator()
    st.rerun()
