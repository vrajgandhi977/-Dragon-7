import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Dragon 7 Betting Simulator", layout="wide")

# Third-Card Drawing Rules Table
third_card_chart = pd.DataFrame({
    "Banker Total": [0, 1, 2, 3, 4, 5, 6, 7],
    "Draws When Player’s 3rd Card Is": ["Any", "Any", "Any", "Not 8", "2-7", "4-7", "6-7", "Stands"]
})

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
        if len(player_hand) == 2 and player_total in [0, 1, 2, 3, 4, 5]:
            third_card = self.draw_random_card()
            if third_card:
                self.current_hand["Player"].append(third_card)

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
                third_card = self.draw_random_card()
                if third_card:
                    self.current_hand["Banker"].append(third_card)

        # **Final Winner Prediction**
        player_total = sum(self.current_hand["Player"]) % 10
        banker_total = sum(self.current_hand["Banker"]) % 10

        if player_total > banker_total:
            return "🏆 **Predicted Winner: Player**"
        elif banker_total > player_total:
            return "🏆 **Predicted Winner: Banker**"
        else:
            return "🔄 **Predicted Result: Tie**"

# Streamlit UI
st.title("🐉 Dragon 7 Betting Simulator - Now With Auto Banker Drawing!")
st.write("Track baccarat hands, predict winners, and apply full third-card rules!")

if "simulator" not in st.session_state:
    st.session_state.simulator = Dragon7Simulator()

simulator = st.session_state.simulator

# **Winner Prediction**
st.write("### 🔮 Predicted Winner")
st.subheader(simulator.predict_winner())

# **Third-Card Rule Chart**
st.write("### 📊 Third-Card Drawing Rules")
st.dataframe(third_card_chart, height=300)

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
if st.button("🎴 Auto-Draw for Banker"):
    simulator.predict_winner()  # This will trigger auto drawing
    st.rerun()

# Reset Game
if st.button("🔄 Reset"):
    st.session_state.simulator = Dragon7Simulator()
    st.rerun()
