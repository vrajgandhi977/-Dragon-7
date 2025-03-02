import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set up Streamlit app for mobile
st.set_page_config(page_title="Dragon 7 Counter", layout="centered")

class Dragon7Counter:
    def __init__(self, total_decks=8):
        self.running_count = 0
        self.total_decks = total_decks
        self.remaining_decks = total_decks
        self.cards_dealt = 0
        self.history = []  # Stores history of hands
        self.current_hand = {"Player": [], "Banker": []}

    def update_count(self, card):
        """ Updates the running count based on the card drawn """
        if card in [4, 5, 6, 7]:  # These cards reduce Dragon 7 chance
            self.running_count -= 1
        elif card in [8, 9]:  # These cards increase Dragon 7 chance
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
        """ Decides if it's time to bet on Dragon 7 """
        return self.get_true_count() >= 4

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

        # Reset for the next hand
        self.current_hand = {"Player": [], "Banker": []}

# Streamlit UI
st.title("🐉 Dragon 7 Tracker - Multi-Card Hands")
st.write("Track multiple cards per hand and detect Dragon 7 wins!")

# Initialize session state for counter
if "counter" not in st.session_state:
    st.session_state.counter = Dragon7Counter()

counter = st.session_state.counter

# Display Current Count
st.subheader(f"📊 Running Count: {counter.running_count}")
st.subheader(f"📉 True Count: {counter.get_true_count():.2f}")
st.subheader(f"📦 Decks Remaining: {counter.remaining_decks:.2f}")

# Dragon 7 Betting Recommendation
if counter.should_bet_dragon7():
    st.success("🔥 Time to bet on Dragon 7! ✅")
else:
    st.warning("🚫 No Dragon 7 bet yet.")

# Show current hand
st.write("### 🃏 Current Hand")
st.write(f"**Player:** {counter.current_hand['Player']}")
st.write(f"**Banker:** {counter.current_hand['Banker']}")

# Card Input Buttons (Bigger for Mobile)
st.write("### ✏️ Add Cards to Current Hand")

col1, col2 = st.columns(2)
with col1:
    st.write("**Add to Player:**")
    if st.button("2️⃣", key="p2"):
        counter.add_card_to_hand("Player", 2)
    if st.button("3️⃣", key="p3"):
        counter.add_card_to_hand("Player", 3)
    if st.button("4️⃣", key="p4"):
        counter.add_card_to_hand("Player", 4)
    if st.button("5️⃣", key="p5"):
        counter.add_card_to_hand("Player", 5)
    if st.button("6️⃣", key="p6"):
        counter.add_card_to_hand("Player", 6)
    if st.button("7️⃣", key="p7"):
        counter.add_card_to_hand("Player", 7)
    if st.button("8️⃣", key="p8"):
        counter.add_card_to_hand("Player", 8)
    if st.button("9️⃣", key="p9"):
        counter.add_card_to_hand("Player", 9)
    if st.button("🔟 / J / Q / K", key="p10"):
        counter.add_card_to_hand("Player", 10)
    if st.button("🅰️ (Ace)", key="p1"):
        counter.add_card_to_hand("Player", 1)

with col2:
    st.write("**Add to Banker:**")
    if st.button("2️⃣", key="b2"):
        counter.add_card_to_hand("Banker", 2)
    if st.button("3️⃣", key="b3"):
        counter.add_card_to_hand("Banker", 3)
    if st.button("4️⃣", key="b4"):
        counter.add_card_to_hand("Banker", 4)
    if st.button("5️⃣", key="b5"):
        counter.add_card_to_hand("Banker", 5)
    if st.button("6️⃣", key="b6"):
        counter.add_card_to_hand("Banker", 6)
    if st.button("7️⃣", key="b7"):
        counter.add_card_to_hand("Banker", 7)
    if st.button("8️⃣", key="b8"):
        counter.add_card_to_hand("Banker", 8)
    if st.button("9️⃣", key="b9"):
        counter.add_card_to_hand("Banker", 9)
    if st.button("🔟 / J / Q / K", key="b10"):
        counter.add_card_to_hand("Banker", 10)
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
