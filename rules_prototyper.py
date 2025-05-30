import streamlit as st
import unicodedata
import re

from utils.conversion_functions import convert, normalize_replace_rules

st.title("Orthography Conversion Rules Prototyper")

rules = st.session_state.get(
    "rules",
    [
        ("Replace", "", ""),
    ]
)

expander = st.expander("Import rules from CSV")
rules_input = expander.text_area(
    "Rules",
)
if expander.button("Import"):
    rules = rules_input.split("\n")
    rules = [
        tuple(rule.split(","))
        for rule in rules
    ]

def update_rules_len():
    num_rules = st.session_state.num_rules
    diff = num_rules - len(st.session_state.rules)
    if diff > 0:
        st.session_state.rules += [("Replace", "", "")] * diff
    elif diff < 0:
        st.session_state.rules = st.session_state.rules[:num_rules]

specified_rules = []
num_rules = st.number_input(
    "Number of rules",
    min_value=0,
    value=len(rules),
    key="num_rules",
    on_change=update_rules_len,
)

for i in range(num_rules):
    rule = rules[i] if i < len(rules) else ("Replace", "", "")
    cols = st.columns(3)
    RULE_TYPES = (
        "Replace",
        "LLC to UMinn accents",
        "UMinn to LLC accents",
        "Phonemic to LLC accents",
    )
    rule_type = cols[0].selectbox(
        "Rule type",
        RULE_TYPES,
        key=f"rule_{i}_type",
        index=RULE_TYPES.index(rule[0]),
    )
    if rule_type == "Replace":
        target = cols[1].text_input(
            "Replace this...",
            key=f"rule_{i}_arg_0",
            value=rule[1] if len(rule) > 1 else "",
        )
        repl = cols[2].text_input(
            "...with this.",
            key=f"rule_{i}_arg_1",
            value=rule[2] if len(rule) > 2 else "",
        )
        specified_rules.append((rule_type, target, repl))
    elif rule_type == "LLC to UMinn accents":
        cols[1].markdown("Remove accents when they do not fall on the second syllable, and retain all others.")
        specified_rules.append((rule_type,))
    elif rule_type in ("Phonemic to LLC accents", "UMinn to LLC accents"):
        cols[1].markdown("Add accents to 2nd syllable of unaccented words, and to all monosyllabic words.")
        specified_rules.append((rule_type,))

st.session_state.rules = specified_rules

expander = st.expander("Export rules to CSV")
expander.code("\n".join([",".join(rule) for rule in st.session_state.rules]))

text_input = st.text_area(
    "Input",
    value="Yašlé (Šuŋgmánitu) waŋ tókhiya yá-haŋ yuŋkȟáŋ othíweta waŋ él míla waŋ iyéyiŋ na yuhá héčhena yé.",
)

text_input = unicodedata.normalize("NFC", text_input)

normalized_rules = []
for rule_type, *rule_args in specified_rules:
    if rule_type == "Replace":
        normalized_rules += normalize_replace_rules([
            (rule_type, *rule_args)
        ])
    else:
        normalized_rules.append((rule_type, *rule_args))
text_output = convert(normalized_rules, text_input)

st.header("Output")
st.text(text_output)