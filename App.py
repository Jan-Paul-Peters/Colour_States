import random
import streamlit as st

# color: (min vis, max vis, min ceiling, max ceiling)
BUCKETS = {
    'RED': (0,    799,  100,    199),
    'AMB': (800,  1599, 200,  299),
    'YLO': (1600, 3699, 300,  699),
    'GRN': (3700, 4999, 700,  1499),
    'WHT': (5000, 7999, 1500, 2499),
    'BLU': (8000, 9999, 2500, 5000),
}

COLOURS = ['RED', 'AMB', 'YLO', 'GRN', 'WHT', 'BLU']


def new_question():
    color = random.choice(list(BUCKETS))
    vmin, vmax, cmin, cmax = BUCKETS[color]

    # CAVOK always means BLU, so only offer it when BLU was drawn
    options = ['FEW', 'SCT', 'BKN', 'OVC', 'NSC']
    if color == 'BLU':
        options.append('CAVOK')
    clouds = random.choice(options)

    if clouds == 'CAVOK':
        # CAVOK replaces both the visibility and the cloud group
        return {"metar": "METAR EHWO ..... CAVOK .....", "answer": "BLU"}

    if clouds in ('BKN', 'OVC'):
        vis = random.randint(vmin, vmax)
        ceil = random.randint(cmin, cmax)

        # Half the time, let one value be higher, so the other one decides the color
        if random.random() < 0.5:
            vis = random.randint(vmin, 9999)
        else:
            ceil = random.randint(cmin, 5000)
        cloud_group = f"{clouds}{str(ceil // 100).zfill(3)}"
    elif clouds in ('FEW', 'SCT'):
        # No ceiling: visibility alone decides. Cloud height is a distractor.
        vis = random.randint(vmin, vmax)
        ceil = random.randint(1, 5000)
        cloud_group = f"{clouds}{str(ceil // 100).zfill(3)}"
    else:  # NSC: no cloud group height at all, visibility decides
        vis = random.randint(vmin, vmax)
        cloud_group = "NSC"

    return {
        "metar": f"METAR EHWO ..... {str((vis // 100)*100).zfill(4)} {cloud_group} .....",
        "answer": color,
    }


def show_help():
    with st.expander("ℹ️ Help: Rules"):
        st.markdown(
            """
**The Colour State is decided by the worse of two values:**
visibility and cloud ceiling.

| Colour | Visibility | Ceiling |
|--------|-----------|---------|
| BLU | 8000 m or more | 2500 ft or higher |
| WHT | 5000 – 7999 m | 1500 – 2499 ft |
| GRN | 3700 – 4999 m | 700 – 1499 ft |
| YLO | 1600 – 3699 m | 300 – 699 ft |
| AMB | 800 – 1599 m | 200 – 299 ft |
| RED | below 800 m | below 200 ft |

**What counts as a ceiling?**
- Only **BKN** (5-7 oktas) and **OVC** (8 oktas) form a ceiling.
- **FEW** and **SCT** do *not* count. Ignore their height, visibility alone decides.
- **NSC** (no significant cloud) has no ceiling either, so visibility alone decides.
- **CAVOK** replaces visibility and clouds (10 km or more, no cloud below 5000 ft), so it is always **BLU**.

**Reading the cloud group:** the three digits are hundreds of feet,
so `BKN008` = 800 ft and `OVC025` = 2500 ft.

**Example:** `9900 FEW002` → FEW is ignored, 9900 m is BLU → **BLU**.
`9900 BKN002` → ceiling 200 ft is AMB, which is worse than the BLU visibility → **AMB**.
            """
        )


def submit_answer(answer):
    correct = answer.strip().upper() == ss.q["answer"]
    ss.score += correct
    prefix = "Affirm" if correct else "Negative"
    ss.result = f"{prefix}, the Color State is {ss.q['answer']}"
    ss.correct = correct
    st.rerun()


st.title("Colour State practice")
show_help()

if "total" not in st.session_state:
    st.session_state.update(total=0, index=0, score=0, q=None, result=None,
                            mode="Type in", correct=False)

ss = st.session_state

if ss.total == 0:
    count = st.number_input("How many practice questions?", 1, 50, 5)
    mode = st.radio("How do you want to answer?", ["Type in", "Multiple choice"],
                    horizontal=True)
    if st.button("▶ Start"):
        ss.update(total=int(count), index=1, score=0,
                  q=new_question(), result=None, mode=mode)
        st.rerun()
else:
    st.write(f"Question {ss.index} of {ss.total}")
    st.code(ss.q["metar"])

    if ss.result is None:
        st.write("What is the Color State?")
        if ss.mode == "Multiple choice":
            # One click answers immediately, no separate confirm step
            cols = st.columns(len(COLOURS))
            for col, colour in zip(cols, COLOURS):
                if col.button(colour, key=f"opt_{ss.index}_{colour}",
                              use_container_width=True):
                    submit_answer(colour)
        else:
            with st.form("answer", clear_on_submit=True):
                answer = st.text_input("What is the Color State?",
                                       label_visibility="collapsed")
                if st.form_submit_button("Check"):
                    if not answer:
                        st.warning("Please type an answer first.")
                    else:
                        submit_answer(answer)
    else:
        (st.success if ss.correct else st.error)(ss.result)
        if ss.index < ss.total:
            if st.button("Next question"):
                ss.index += 1
                ss.q = new_question()
                ss.result = None
                st.rerun()
        else:
            st.subheader(f"Done! Score: {ss.score} / {ss.total}")
            if st.button("Restart"):
                ss.total = 0
                st.rerun()
