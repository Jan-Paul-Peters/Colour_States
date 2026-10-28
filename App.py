import random
import streamlit as st

# color: (min vis, max vis, min ceiling, max ceiling)
BUCKETS = {
    'RED': (0,    799,  0,    199),
    'AMB': (800,  1599, 200,  299),
    'YLW': (1600, 3699, 300,  699),
    'GRN': (3700, 4999, 700,  1499),
    'WHT': (5000, 7999, 1500, 2499),
    'BLU': (8000, 9999, 2500, 5000),
}

def new_question():
    color = random.choice(list(BUCKETS))
    vmin, vmax, cmin, cmax = BUCKETS[color]

    vis = random.randint(vmin, vmax)
    ceil = random.randint(cmin, cmax)

    # Half the time, let one value be higher, so the other one decides the color
    if random.random() < 0.5:
        vis = random.randint(vmin, 9999)
    else:
        ceil = random.randint(cmin, 5000)

    clouds = random.choice(['FEW', 'SCT', 'BKN', 'OVC'])

    return {
        "metar": f"METAR EHWO ..... {str(vis).zfill(4)} {clouds}{str(ceil // 100).zfill(3)} .....",
        "answer": color,
    }


st.title("Colour State oefenen")

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
