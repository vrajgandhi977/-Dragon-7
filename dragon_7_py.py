import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time  

st.set_page_config(page_title="Dragon 7 Predictor", layout="wide")

# Custom Styling for Mobile Optimization
st.markdown(
    """
    <style>
    body { background-color: #121212; color: #ffffff; }
    .stButton>button { font-size: 24px; padding: 15px; width: 100%; }
    .stDataFrame { overflow-x: scroll; }
    .block-container { padding-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

class Dragon7Counter:
    def __init__(self, total_decks=8):
        self.running_count = 0
        self.total_decks = total_decks
        self.remaining_decks = total_decks
        self.cards_dealt = 0
        self.history = []
        self.dragon7_occurrences = []
        self.current_hand = {"Player": [], "Banker": []}
        self.remaining_cards = {i: 4 * 8 for i in range(1, 11)}  # 8 decks

    def update_count(self, card):
        """ Updates the running count using the optimized system """
        card_values = {1: 0, 2: 0, 3: 0, 4: -1, 5: -1, 6: -1, 7: -1, 8: 2, 9: 2, 10: 0}
        self.running_count += card_values.get(card, 0)
        
        self.cards_dealt += 1
        self.update_decks()

        if self.remaining_cards[card] > 0:
            self.remaining_cards[card] -= 1

    def update_decks(self):
        """ Updates the number of decks remaining in the shoe """
        self.remaining_decks = max(1, self.total_decks - (self.cards_dealt / 52))

    def get_true_count(self):
        """ Calculates the true count """
        return self.running_count / self.remaining_decks

    def get_dragon7_probability(self):
        """ Estimates the probability of a Dragon 7 occurring based on remaining cards """
        base_probability = 2.3  
        tc_factor = self.get_true_count() * 1.5  
        key_card_weight = sum(self.remaining_cards[i] for i in [8, 9]) / (self.remaining_decks * 52) * 10  
        probability = min(base_probability + tc_factor + key_card_weight, 25)  
        return probability

    def predict_dragon7(self):
        """ Predicts when to bet on Dragon 7 """
        if self.get_true_count() >= 4:
            return "🔥 BET NOW! (TC ≥ 4, +8.03% Edge)"
        elif self.get_true_count() >= 3:
            return "⚠️ Almost There! (TC = 3)"
        else:
            return "❌ Not Yet"

    def estimate_profit(self):
        """ Estimates expected profit based on past Dragon 7 bets """
        bets_placed = len([h for h in self.history if h["Dragon 7"] == "✅ Yes"])
        expected_profit = bets_placed * 59  # Assuming $100 bet per Dragon 7
        return expected_profit

    def add_card_to_hand(self, role, card):
        """ Adds a card to either the Player or Banker hand """
        if role in self.current_hand:
            self.current_hand[role].append(card)
            self.update_count(card)

    def finalize_hand(self):
        """ Determines the winner, detects Dragon 7, and saves the hand to history """
        banker_hand = self.current_hand["Banker"]
        player_hand = self.current_hand["Player"]
        banker_total = sum(banker_hand) % 10  
        player_total = sum(player_hand) % 10

        winner = "Banker" if banker_total > player_total else "Player" if player_total > banker_total else "Tie"
        is_dragon7 = len(banker_hand) == 3 and banker_total == 7

        self.history.append({
            "Hand": len(self.history) + 1,
            "Player Cards": str(player_hand),
            "Banker Cards": str(banker_hand),
            "Player Total": player_total,
            "Banker Total": banker_total,
            "Winner": winner,
            "Dragon 7": "✅ Yes" if is_dragon7 else "❌ No",
            "Running Count": self.running_count,
            "Decks Remaining": self.remaining_decks,
            "True Count": self.get_true_count(),
            "Dragon 7 Probability": self.get_dragon7_probability()
        })

        if is_dragon7:
            self.dragon7_occurrences.append(len(self.history))

        self.current_hand = {"Player": [], "Banker": []}

# Streamlit UI
st.title("🐉 Dragon 7 Predictor - Advanced Version")
st.write("Track baccarat hands, predict Dragon 7, and optimize profitability!")

if "counter" not in st.session_state:
    st.session_state.counter = Dragon7Counter()

counter = st.session_state.counter

# Display Prediction & Probability
st.subheader(f"📉 True Count: {counter.get_true_count():.2f}")
st.subheader(f"🎯 Dragon 7 Prediction: {counter.predict_dragon7()}")
st.progress(counter.get_dragon7_probability() / 25)

# **Profit Estimator**
st.write(f"💰 **Estimated Profit This Session: ${counter.estimate_profit()}**")

# **Hand Display**
st.write("### 🃏 Current Hand")
st.write(f"**Player:** {counter.current_hand['Player']}")
st.write(f"**Banker:** {counter.current_hand['Banker']}")

# **Card Input - Optimized for Mobile**
st.write("### ✏️ Add Cards")
col1, col2 = st.columns(2)

with col1:
    st.write("**Player:**")
    for card in range(1, 11):  
        if st.button(str(card), key=f"p{card}"):
            counter.add_card_to_hand("Player", card)
            st.rerun()

with col2:
    st.write("**Banker:**")
    for card in range(1, 11):  
        if st.button(str(card), key=f"b{card}"):
            counter.add_card_to_hand("Banker", card)
            st.rerun()

# **Finalize Hand**
if st.button("✅ Finalize Hand"):
    with st.spinner("Processing..."):
        time.sleep(0.3)  
        counter.finalize_hand()
        st.rerun()

# **Reset Button**
if st.button("🔄 Reset"):
    with st.spinner("Resetting..."):
        time.sleep(0.3)  
        st.session_state.counter = Dragon7Counter()
        st.rerun()
