import streamlit as st
import unicodedata

st.title("Orthography Conversion Rules Prototyper")

num_rules = st.number_input("Number of rules", min_value=0, value=1)
rules = []

for i in range(num_rules):
    cols = st.columns(3)
    rule_type = cols[0].selectbox(
        "Rule type",
        ("Replace", "Replace (ignore accents)"),
        key=f"rule_{i}_type",
    )
    if rule_type in ("Replace", "Replace (ignore accents)"):
        target = cols[1].text_input(
            "Replace this...",
            key=f"rule_{i}_target",
        )
        repl = cols[2].text_input(
            "...with this.",
            key=f"rule_{i}_repl",
        )
        rules.append((rule_type, target, repl))

text_input = st.text_area(
    "Input",
    value="Yašlé (Šuŋgmánitu) waŋ tókhiya yá-haŋ yuŋkȟáŋ othíweta waŋ él míla waŋ iyéyiŋ na yuhá héčhena yé.",
)

text_input = unicodedata.normalize("NFC", text_input)

text_output = text_input
for rule_type, *rule_args in rules:
    if rule_type == "Replace":
        target, repl = rule_args
        target = unicodedata.normalize("NFC", target)
        repl = unicodedata.normalize("NFC", repl)
        text_output = text_output.replace(target, repl)
    if rule_type == "Replace (ignore accents)":
        combining_accents = ("̀", "́")
        target, repl = rule_args
        target = unicodedata.normalize("NFD", target)
        repl = unicodedata.normalize("NFD", repl)
        for e in combining_accents:
            target = target.replace(e, "")
            repl =repl.replace(e, "")
        target = unicodedata.normalize("NFC", target)
        repl = unicodedata.normalize("NFC", repl)
        text_output = unicodedata.normalize("NFD", text_output)                
        text_output = text_output.replace(target, repl)
        text_output = unicodedata.normalize("NFC", text_output)

st.header("Output")
st.text(text_output)