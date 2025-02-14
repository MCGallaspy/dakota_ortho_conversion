import streamlit as st
import unicodedata
import re

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
    

num_rules = st.number_input(
    "Number of rules",
    min_value=0,
    value=len(rules),
    key="num_rules",
    on_change=update_rules_len,
)

specified_rules = []
for i in range(num_rules):
    rule = rules[i] if i < len(rules) else ("Replace", "", "")
    cols = st.columns(3)
    RULE_TYPES = ("Replace", "Replace (ignore accents)")
    rule_type = cols[0].selectbox(
        "Rule type",
        RULE_TYPES,
        key=f"rule_{i}_type",
        index=RULE_TYPES.index(rule[0]),
    )
    if rule_type in ("Replace", "Replace (ignore accents)"):
        target = cols[1].text_input(
            "Replace this...",
            key=f"rule_{i}_arg_0",
            value=rule[1],
        )
        repl = cols[2].text_input(
            "...with this.",
            key=f"rule_{i}_arg_1",
            value=rule[2],
        )
        specified_rules.append((rule_type, target, repl))

st.session_state.rules = specified_rules

expander = st.expander("Export rules to CSV")
expander.code("\n".join([",".join(rule) for rule in st.session_state.rules]))

text_input = st.text_area(
    "Input",
    value="Yašlé (Šuŋgmánitu) waŋ tókhiya yá-haŋ yuŋkȟáŋ othíweta waŋ él míla waŋ iyéyiŋ na yuhá héčhena yé.",
)

text_input = unicodedata.normalize("NFC", text_input)

text_output = text_input

normalized_rules = []
for rule_type, *rule_args in st.session_state.rules:
    normalized_rules.append(tuple(
        [rule_type] + [e.upper() for e in rule_args]
    ))
    normalized_rules.append(tuple(
        [rule_type] + [e.lower() for e in rule_args]
    ))
    
for rule_type, *rule_args in normalized_rules:
    if rule_type == "Replace":
        target, repl = rule_args
        target = unicodedata.normalize("NFC", target)
        repl = unicodedata.normalize("NFC", repl)
        text_output = re.sub(
            target,
            repl,
            text_output,
            flags=re.NOFLAG,
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
            flags=re.NOFLAG,
        )
        text_output = unicodedata.normalize("NFC", text_output)

st.header("Output")
st.markdown(text_output)