import streamlit as st
import random
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ---------- 초기화 ----------
if "day" not in st.session_state:
    st.session_state.day = 1

if "prices" not in st.session_state:
    st.session_state.prices = {
        "A": [100],
        "B": [80]
    }

if "holdings" not in st.session_state:
    st.session_state.holdings = {
        "A": 0,
        "B": 0
    }

if "cash" not in st.session_state:
    st.session_state.cash = 1000

# ---------- 함수 ----------
def buy(stock):
    price = st.session_state.prices[stock][-1]
    if st.session_state.cash >= price:
        st.session_state.cash -= price
        st.session_state.holdings[stock] += 1

def sell(stock):
    price = st.session_state.prices[stock][-1]
    if st.session_state.holdings[stock] > 0:
        st.session_state.cash += price
        st.session_state.holdings[stock] -= 1

def next_day():
    st.session_state.day += 1
    for s in st.session_state.prices:
        change = random.randint(-5, 5)
        new_price = max(10, st.session_state.prices[s][-1] + change)
        st.session_state.prices[s].append(new_price)

# ---------- UI ----------
menu = st.sidebar.radio("종목 선택", ["A", "B"])
st.sidebar.markdown(f"Day {st.session_state.day}")
st.sidebar.markdown(f"현금: {st.session_state.cash}원")

prices = st.session_state.prices[menu]

# ---------- 화살표 (버튼과 완전 분리) ----------
if len(prices) >= 2:
    diff = prices[-1] - prices[-2]
    arrow = "🔺" if diff > 0 else "🔻" if diff < 0 else "➖"
else:
    arrow = "➖"

st.markdown(f"## {menu} {arrow}")
st.markdown(f"현재가: {prices[-1]}원")
st.markdown(f"보유 수량: {st.session_state.holdings[menu]}주")

# ---------- 그래프 (항상 표시) ----------
fig, ax = plt.subplots()
ax.plot(prices, marker="o")
ax.set_xlabel("Day")
ax.set_ylabel("Price")
st.pyplot(fig)

# ---------- 버튼 ----------
col1, col2 = st.columns(2)
with col1:
    st.button("🟢 매수", on_click=buy, args=(menu,), key=f"buy_{menu}")
with col2:
    st.button("🔴 매도", on_click=sell, args=(menu,), key=f"sell_{menu}")

st.markdown("---")
st.button("⏭ 다음 날", on_click=next_day)
