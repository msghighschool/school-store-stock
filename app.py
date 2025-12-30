import streamlit as st
import random
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ---------------- 초기 상태 ----------------
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

EVENTS = {
    3: ("정부의 반도체 투자 발표", +8),
    5: ("금리 인상 우려 확산", -6),
    7: ("해외 수요 증가 전망", +5)
}

# ---------------- 사이드바 ----------------
menu = st.sidebar.radio("메뉴", ["A", "B"])

st.sidebar.markdown(f"### 📅 Day {st.session_state.day}")
st.sidebar.markdown(f"💰 현금: {st.session_state.cash}원")

# ---------------- 사전 뉴스 ----------------
if st.session_state.day + 1 in EVENTS:
    trust = random.randint(50, 100)
    st.warning(
        f"🔮 사전 뉴스: {EVENTS[st.session_state.day + 1][0]} (신뢰도 {trust}%)"
    )

# ---------------- 가격 그래프 ----------------
prices = st.session_state.prices[menu]

fig, ax = plt.subplots()
ax.plot(prices, marker="o")
ax.set_title(f"{menu} 주가 추이")
ax.set_xlabel("Day")
ax.set_ylabel("Price")
st.pyplot(fig)

# ---------------- 현재 상태 ----------------
st.markdown(f"### 📊 {menu} 주식")
st.markdown(f"- 현재가: {prices[-1]}원")
st.markdown(f"- 보유 수량: {st.session_state.holdings[menu]}주")

# ---------------- 매수 / 매도 ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "🟢 매수",
        key=f"buy_{menu}"
    ):
        if st.session_state.cash >= prices[-1]:
            st.session_state.cash -= prices[-1]
            st.session_state.holdings[menu] += 1
            st.success("매수 완료")
        else:
            st.error("현금 부족")

with col2:
    if st.button(
        "🔴 매도",
        key=f"sell_{menu}"
    ):
        if st.session_state.holdings[menu] > 0:
            st.session_state.cash += prices[-1]
            st.session_state.holdings[menu] -= 1
            st.success("매도 완료")
        else:
            st.error("보유 주식 없음")

# ---------------- 다음 날 ----------------
st.markdown("---")

if st.button("⏭ 다음 날"):
    st.session_state.day += 1

    for stock in st.session_state.prices:
        change = random.randint(-5, 5)

        if st.session_state.day in EVENTS:
            event_stock = "A"  # 예시
            if stock == event_stock:
                change += EVENTS[st.session_state.day][1]

        new_price = max(10, st.session_state.prices[stock][-1] + change)
        st.session_state.prices[stock].append(new_price)

    st.experimental_rerun()
