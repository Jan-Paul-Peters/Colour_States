import random
import streamlit as st

def state(vis, ceiling, fill):
    s = 'RED'
    if vis >= 800  and (ceiling >= 200  or fill <= 1): s = 'AMB'
    if vis >= 1600 and (ceiling >= 300  or fill <= 1): s = 'YLO'
    if vis >= 3700 and (ceiling >= 700  or fill <= 1): s = 'GRN'
    if vis >= 5000 and (ceiling >= 1500 or fill <= 1): s = 'WHT'
    if vis >= 8000 and (ceiling >= 2500 or fill <= 1): s = 'BLU'
    return s

def new_question():
    vis = random.randint(0, 100)*100
    ceil = random.randint(0, 5000)
    n = random.randint(1, 8)

    if n <= 2:   clouds = 'FEW'
    elif n <= 4: clouds = 'SCT'
    elif n <= 7: clouds = 'BKN'
    else:        clouds = 'OVC'

    visib = str(vis).zfill(4)[-4:]
    ceiling = str(ceil // 100).zfill(3)

    return {
        "metar": f"METAR EHWO ..... {visib} {clouds}{ceiling} .....",
        "answer": state(vis, ceil, n),
    }

st.title("Color State oefenen")

if "total" not in st.session_state:
    st.session_state.update(total=0, index=0, score=0, q=None, result=None)

ss = st.session_state

if ss.total == 0:
    aantal = st.number_input("Hoeveel oefenvragen wil je?", 1, 50, 5)
    if st.button("▶ Start"):
        ss.update(total=int(aantal), index=1, score=0,
                  q=new_question(), result=None)
        st.rerun()
else:
    st.write(f"Vraag {ss.index} van {ss.total}")
    st.code(ss.q["metar"])

    if ss.result is None:
        with st.form("antwoord", clear_on_submit=True):
            answer = st.text_input("What is the Color State?")
            if st.form_submit_button("Controleer"):
                correct = answer.strip().upper() == ss.q["answer"]
                ss.score += correct
                prefix = "Affirm" if correct else "Negative"
                ss.result = f"{prefix}, the Color State is {ss.q['answer']}"
                ss.correct = correct
                st.rerun()
    else:
        (st.success if ss.correct else st.error)(ss.result)
        if ss.index < ss.total:
            if st.button("Volgende vraag"):
                ss.index += 1
                ss.q = new_question()
                ss.result = None
                st.rerun()
        else:
            st.subheader(f"Klaar! Score: {ss.score} / {ss.total}")
            if st.button("Opnieuw"):
                ss.total = 0
                st.rerun()
