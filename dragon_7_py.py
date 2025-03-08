import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Dragon 7 Betting Simulator", layout="wide")

class Dragon7Simulator:
    def __init__(self, total_decks=8):
        self.current_hand = {"Player": [], "Banker": []}
        self.remaining_cards = {i: 4 * 8 for i in range(1, 11)}

    def add_card_to_hand(self, role, card):
        """ Adds a card to either the Player or Banker hand """
        if role in self.current_hand:
            self.current_hand[role].append(card)
            if self.remaining_cards[card] > 0:
                self.remaining_cards[card] -= 1

    def draw_random_card(self):
        """ Draws a random card from the remaining deck """
        available_cards = [k for k, v in self.remaining_cards.items() if v > 0]
        return random.choice(available_cards) if available_cards else None

    def apply_third_card_rules(self):
        """ Automatically draws third cards for Player and Banker based on official Baccarat rules """

        player_hand = self.current_hand["Player"]
        banker_hand = self.current_hand["Banker"]

        if not player_hand or not banker_hand:
            return  

        player_total = sum(player_hand) % 10
        banker_total = sum(banker_hand) % 10

        # **Natural Win (8 or 9) - No more cards drawn**
        if player_total in [8, 9] or banker_total in [8, 9]:
            return  

        # **Player's Third Card Rule**
        player_draws = player_total <= 5  # Player draws if total is 0-5
        player_third_card = None
        if player_draws:
            player_third_card = self.draw_random_card()
            if player_third_card:
                self.current_hand["Player"].append(player_third_card)

        # **Banker's Third Card Rule**
        banker_draws = False
        if banker_total <= 2:
            banker_draws = True
        elif banker_total == 3 and (not player_draws or player_third_card != 8):
            banker_draws = True
        elif banker_total == 4 and player_third_card in [2, 3, 4, 5, 6, 7]:
            banker_draws = True
        elif banker_total == 5 and player_third_card in [4, 5, 6, 7]:
            banker_draws = True
        elif banker_total == 6 and player_third_card in [6, 7]:
            banker_draws = True

        if banker_draws:
            banker_third_card = self.draw_random_card()
            if banker_third_card:
                self.current_hand["Banker"].append(banker_third_card)

    def predict_winner(self):
        """ Uses official EZ Baccarat rules to predict the winner after all draws """
        self.apply_third_card_rules()  # Apply third card rules first

        player_total = sum(self.current_hand["Player"]) % 10
        banker_total = sum(self.current_hand["Banker"]) % 10

        if player_total > banker_total:
            return "🏆 **Predicted Winner: Player**"
        elif banker_total > player_total:
            return "🏆 **Predicted Winner: Banker**"
        else:
            return "🔄 **Predicted Result: Tie**"

# Streamlit UI
st.title("🐉 Dragon 7")
st.write("Track baccarat hands, predict winners, and apply full third-card rules!")

if "simulator" not in st.session_state:
    st.session_state.simulator = Dragon7Simulator()

simulator = st.session_state.simulator

# **Winner Prediction**
st.write("### 🔮 Predicted Winner")
st.subheader(simulator.predict_winner())

# **Hand Display**
st.write("### 🃏 Current Hand")
st.write(f"**Player:** {simulator.current_hand['Player']}")
st.write(f"**Banker:** {simulator.current_hand['Banker']}")

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

# **Auto Banker Draw Button**
if st.button("🎴 Auto-Draw Third Cards"):
    simulator.apply_third_card_rules()
    st.rerun()

# Reset Game
if st.button("🔄 Reset"):
    st.session_state.simulator = Dragon7Simulator()
    st.rerun()
