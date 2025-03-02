import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dragon 7 Predictor", layout="centered")

class Dragon7Counter:
    def __init__(self, total_decks=8):
        self.running_count = 0
        self.total_decks = total_decks
        self.remaining_decks = total_decks
        self.cards_dealt = 0
        self.history = []  # Stores history of hands
        self.dragon7_occurrences = []  # Stores past Dragon 7 hands
        self.current_hand = {"Player": [], "Banker": []}

    def update_count(self, card):
        """ Updates the running count based on the card drawn """
        if card in [4, 5, 6, 7]:  
            self.running_count -= 1
        elif card in [8, 9]:  
            self.running_count += 2
        
        self.cards_dealt += 1
        self.update_decks()

    def update_decks(self):
        """ Updates the number of decks remaining in the shoe """
        self.remaining_decks = max(1, self.total_decks - (self.cards_dealt / 52))

    def get_true_count(self):
        """ Calculates the true count """
        return self.running_count / self.remaining_decks

    def should_bet_dragon7(self):
        """ Predicts when to bet on Dragon 7 """
        # If True Count is high and a pattern is detected, recommend betting
        recent_dragon7 = len(self.dragon7_occurrences) >= 2
        last_dragon7_hand = self.dragon7_occurrences[-1] if recent_dragon7 else None

        if self.get_true_count() >= 4:
            return "🔥 Strong Bet Now!"
        elif last_dragon7_hand and last_dragon7_hand + 5 < len(self.history):
            return "⚠️ Possible Soon!"
        else:
            return "❌ Not Yet"

    def add_card_to_hand(self, role, card):
        """ Adds a card to either the Player or Banker hand """
        if role in self.current_hand:
            self.current_hand[role].append(card)
            self.update_count(card)

    def finalize_hand(self):
        """ Checks if a Dragon 7 has occurred and saves the hand to history """
        banker_hand = self.current_hand["Banker"]
        player_hand = self.current_hand["Player"]
        banker_total = sum(banker_hand) % 10  # Baccarat total (last digit only)

        is_dragon7 = len(banker_hand) == 3 and banker_total == 7

        # Save the hand details
        self.history.append({
            "Hand": len(self.history) + 1,
            "Player Cards": str(player_hand),
            "Banker Cards": str(banker_hand),
            "Banker Total": banker_total,
            "Dragon 7": "✅ Yes" if is_dragon7 else "❌ No",
            "Running Count": self.running_count,
            "Decks Remaining": self.remaining_decks,
            "True Count": self.get_true_count()
        })

        # Track past Dragon 7 occurrences
        if is_dragon7:
            self.dragon7_occurrences.append(len(self.history))

        # Reset for the next hand
        self.current_hand = {"Player": [], "Banker": []}

# Streamlit UI
st.title("🐉 Dragon 7 Predictor")
st.write("Track baccarat hands and predict when to bet on Dragon 7!")

# Initialize session state for counter
if "counter" not in st.session_state:
    st.session_state.counter = Dragon7Counter()

counter = st.session_state.counter

# Display Current Count & Prediction
st.subheader(f"📊 Running Count: {counter.running_count}")
st.subheader(f"📉 True Count: {counter.get_true_count():.2f}")
st.subheader(f"📦 Decks Remaining: {counter.remaining_decks:.2f}")
st.subheader(f"🎯 Dragon 7 Prediction: {counter.should_bet_dragon7()}")

# Show current hand
st.write("### 🃏 Current Hand")
st.write(f"**Player:** {counter.current_hand['Player']}")
st.write(f"**Banker:** {counter.current_hand['Banker']}")

# Card Input Buttons (Bigger for Mobile)
st.write("### ✏️ Add Cards to Current Hand")

col1, col2 = st.columns(2)
with col1:
    st.write("**Add to Player:**")
    for card in range(2, 11):  # 2 to 10
        if st.button(str(card), key=f"p{card}"):
            counter.add_card_to_hand("Player", card)
    if st.button("🅰️ (Ace)", key="p1"):
        counter.add_card_to_hand("Player", 1)

with col2:
    st.write("**Add to Banker:**")
    for card in range(2, 11):  # 2 to 10
        if st.button(str(card), key=f"b{card}"):
            counter.add_card_to_hand("Banker", card)
    if st.button("🅰️ (Ace)", key="b1"):
        counter.add_card_to_hand("Banker", 1)

# Finalize Hand Button
if st.button("✅ Finalize Hand"):
    counter.finalize_hand()

# Expandable section for history & graph
with st.expander("📜 Hand History & True Count Graph", expanded=False):
    if counter.history:
        st.write("### Hand History")
        df = pd.DataFrame(counter.history)
        st.dataframe(df, height=200)

        # Plot True Count Over Time
        st.write("### True Count Trend")
        fig, ax = plt.subplots()
        ax.plot(df["Hand"], df["True Count"], marker="o", linestyle="-", color="blue", label="True Count")
        ax.set_xlabel("Hand Number")
        ax.set_ylabel("True Count")
        ax.axhline(y=4, color="red", linestyle="--", label="Dragon 7 Bet Threshold")
        ax.legend()
        st.pyplot(fig)

st.write("")
if st.button("🔄 Reset Counter"):
    st.session_state.counter = Dragon7Counter()
