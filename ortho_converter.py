import streamlit as st

from utils.conversion_functions import (
    convert_llc_to_uminn,
    convert_uminn_to_llc_no_velar_aspiration,
    convert_uminn_to_llc,
    convert_uminn_to_phoneme,
    convert_llc_to_phoneme,
    #convert_whitehat_to_phoneme,
    convert_phoneme_to_llc_unvelarized,
    convert_phoneme_to_llc_velar_aspiration,
    convert_phoneme_to_uminn
    #convert_phoneme_to_whitehat
)


st.title("Dakota Orthography Conversion")

ORTHOGRAPHIES = (
    "LLC",
    "UMinn",
    "IPA Phonemic",
    "Whitehat"
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
if target_orthography == "LLC":
    with_velar_aspiration = rightcol.checkbox("With velar aspiration", value=True)

# For simplicity, let's make the assumption that any text in its phonemic
# representation uses the UMinn convention for accents.

# Converting source text to phonemic orthography.
phonemic_text = None
if source_orthography == "UMinn":
    phonemic_text = convert_uminn_to_phoneme(input_text)
elif source_orthography == "LLC":
    phonemic_text = convert_llc_to_phoneme(input_text)
elif source_orthography == "IPA Phonemic":
    phonemic_text = input_text
#elif source_orthography == "Whitehat":
#    phonemic_text == convert_whitehat_to_phoneme(input_text)

# Converting phonemic text to target orthography.
if target_orthography == "LLC":
    if with_velar_aspiration:
        st.success("Phonemic conversion with velar aspiration worked!")
        output_text = convert_phoneme_to_llc_velar_aspiration(phonemic_text)
    else:
        st.success("Phonemic conversion without velar aspiration worked!")
        output_text = convert_phoneme_to_llc_unvelarized(phonemic_text)
elif target_orthography == "UMinn":
    output_text = convert_phoneme_to_uminn(phonemic_text)
elif target_orthography == "IPA Phonemic":
    output_text = phonemic_text
#elif target_orthography == "Whitehat":
#    output_text = convert_phoneme_to_whitehat(phonemic_text)
elif target_orthography == source_orthography:
    output_text = input_text

# Old logic, gradually delete as we convert to using a phonemic backend.
if phonemic_text is None:
    if source_orthography == "LLC" and target_orthography == "UMinn":
        output_text = convert_llc_to_uminn(input_text)
    elif source_orthography == "UMinn" and target_orthography == "LLC":
        if with_velar_aspiration:
            output_text = convert_uminn_to_llc(input_text)
        else:
            output_text = convert_uminn_to_llc_no_velar_aspiration(input_text)
    elif source_orthography == target_orthography:
        output_text = input_text
    else:
        st.warning("Conversion not supported at this time")
        output_text = ""
# End of deletable old logic

rightcol.html('<p style="font-size: 14px; margin-bottom: -10px">Converted text</p>')
container = rightcol.container(border=True)
container.text(output_text)