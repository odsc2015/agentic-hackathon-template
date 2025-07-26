import streamlit as st
from planner import plan_tasks
from executor import execute, get_trending_news
from memory import store_memory, get_memory

st.set_page_config(page_title="Fake News Detection Agent 3.0", page_icon="📰", layout="wide")
st.title("📰 Fake News Detection Agent 3.0")

tab1, tab2 = st.tabs(["✅ Verify a Claim", "🔥 Latest Fake / Unverified News"])

# -------- TAB 1: Verify Manually --------
with tab1:
    user_input = st.text_input("Enter a claim to verify:",
                               placeholder="e.g., Is it true that AI will replace 90% of jobs by 2030?")
    if st.button("Verify Claim"):
        if user_input:
            with st.spinner("🤖 Thinking..."):
                st.write("### 🧠 Agent Thinking Steps")
                tasks = plan_tasks(user_input)
                for t in tasks:
                    st.write(f"✅ {t}")

                verdict, evidence, probability = execute(tasks, user_input)

                # Detect verdict color
                verdict_upper = verdict.upper()
                if "TRUE" in verdict_upper:
                    color = "green"
                elif "FALSE" in verdict_upper:
                    color = "red"
                else:
                    color = "orange"

                st.markdown(f"### 🏆 Verdict: <span style='color:{color};font-weight:bold'>{verdict}</span>",
                            unsafe_allow_html=True)

                if probability is not None:
                    st.progress(probability / 100)
                    st.write(f"Probability of being TRUE: {probability}%")

                # Show evidence
                st.write("### 🔗 Top Sources")
                if evidence:
                    for e in evidence:
                        st.markdown(f"[{e['title']}]({e['link']}) - {e['snippet']}")
                else:
                    st.write("No live sources found.")

                # Memory Logging
                store_memory(user_input, verdict)

    st.write("---")
    st.write("### 📜 Recent Verification Timeline")
    for mem in reversed(get_memory()):
        st.markdown(f"✅ Claim: {mem['claim']}  \n🔎 Verdict: {mem['verification']}")

# -------- TAB 2: Auto Fake News Detection --------
with tab2:
    st.subheader("🔥 Latest Fake / Unverified News (Auto-Checked)")
    news_list = get_trending_news()
    fake_news_detected = []

    if news_list:
        with st.spinner("Scanning latest news..."):
            for n in news_list:
                headline = n["title"]
                tasks = plan_tasks(headline)
                verdict, _, probability = execute(tasks, headline)
                verdict_upper = verdict.upper()

                if "FALSE" in verdict_upper or "UNVERIFIED" in verdict_upper:
                    fake_news_detected.append((headline, verdict, probability, n["url"]))

        if fake_news_detected:
            for headline, verdict, probability, link in fake_news_detected:
                color = "red" if "FALSE" in verdict.upper() else "orange"
                st.markdown(f"[{headline}]({link})", unsafe_allow_html=True)
                st.markdown(f"<span style='color:{color};font-weight:bold'>{verdict}</span>",
                            unsafe_allow_html=True)
                if probability is not None:
                    st.progress(probability / 100)
                    st.write(f"Probability of being TRUE: {probability}%")
                st.write("---")
        else:
            st.success("✅ No fake or unverified news detected right now!")
    else:
        st.warning("⚠️ Could not fetch latest news. Check your NEWSAPI_KEY.")