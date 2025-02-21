import streamlit as st

from utils.conversion_functions import convert_llc_to_uminn, convert_uminn_to_llc


st.title("Dakota Orthography Conversion")

ORTHOGRAPHIES = (
    "LLC",
    "UMinn",
)

leftcol, rightcol = st.columns(2)

source_orthography = leftcol.selectbox(
    "Source orthography",
    ORTHOGRAPHIES,
    index=0,
)

input_text = leftcol.text_area(
    "Input text",
)

target_orthography = rightcol.selectbox(
    "Target orthography",
    ORTHOGRAPHIES,
    index=1,
)

if source_orthography == "LLC" and target_orthography == "UMinn":
    output_text = convert_llc_to_uminn(input_text)
elif source_orthography == "UMinn" and target_orthography == "LLC":
    output_text = convert_uminn_to_llc(input_text)
elif source_orthography == target_orthography:
    output_text = input_text
else:
    st.warning("Conversion not supported at this time")
    output_text = ""

rightcol.html('<p style="font-size: 14px; margin-bottom: -10px">Converted text</p>')
container = rightcol.container(border=True)
container.text(output_text)