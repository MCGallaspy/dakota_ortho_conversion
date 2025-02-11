import streamlit as st
import unicodedata
import re

st.title("Orthography Conversion Rules Prototyper")

rules = []

num_rules = st.number_input(
    "Number of rules",
    min_value=0,
    value=1,
    key="num_rules",
)

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
            key=f"rule_{i}_arg_0",
        )
        repl = cols[2].text_input(
            "...with this.",
            key=f"rule_{i}_arg_1",
        )
        rules.append((rule_type, target, repl))

expander = st.expander("Export rules to CSV")
expander.code("\n".join([",".join(rule) for rule in rules]))

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
        text_output = re.sub(
            target,
            repl,
            text_output,
            flags=re.IGNORECASE,
        )
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
        text_output = re.sub(
            target,
            repl,
            text_output,
            flags=re.IGNORECASE,
        )
        text_output = unicodedata.normalize("NFC", text_output)

st.header("Output")
st.text(text_output)