import re
import unicodedata


COMBINING_ACCENTS = ("̀", "́")


def convert(rules, input_text) -> str:
    output_text = unicodedata.normalize("NFD", input_text)
    for rule_type, *rule_args in rules:
        if rule_type == "Replace":
            target, repl = rule_args
            output_text = re.sub(
                target,
                repl,
                output_text,
                flags=re.NOFLAG,
            )
        elif rule_type == "LLC to Phonemic accents":
            matches = re.split(r"(\s+)", output_text.lstrip())
            if len(matches) % 2 == 1:
                matches.append("")
            words = [
                (matches[2*i], matches[2*i+1])
                for i in range(len(matches)//2)
            ]
            result = ""
            for word, whitespace_sequence in words:
                word = unicodedata.normalize("NFD", word)
                vowel_pattern = re.compile(r"[aeiouAEIOU]")
                first_vowel_mo = vowel_pattern.search(word, pos=0)
                if first_vowel_mo:
                    first_vowel = first_vowel_mo.group(0)
                    pos = word.index(first_vowel) + 1
                    second_vowel_mo = vowel_pattern.search(
                        word,
                        pos=pos,
                    )
                    if second_vowel_mo:
                        second_vowel = second_vowel_mo.group(0)
                        pos = word.index(second_vowel, pos)
                        is_second_syllable_accented = \
                            (pos+1 < len(word)) and \
                            (word[pos+1] in COMBINING_ACCENTS)
                        if is_second_syllable_accented:
                            word = word[:pos+1] + word[pos+2:]
                    else: # Single syllable word, suppress accents
                        for accent in COMBINING_ACCENTS:
                            word = word.replace(accent, "")
                word = unicodedata.normalize("NFC", word)
                result += word + whitespace_sequence
            output_text = result
        elif rule_type in "Phonemic to LLC accents":
            matches = re.split(r"(\s+)", output_text.lstrip())
            if len(matches) % 2 == 1:
                matches.append("")
            words = [
                (matches[2*i], matches[2*i+1])
                for i in range(len(matches)//2)
            ]
            result = ""
            for word, whitespace_sequence in words:
                word = unicodedata.normalize("NFD", word)
                is_word_accented = any(
                    accent in word
                    for accent in COMBINING_ACCENTS
                )
                vowel_pattern = re.compile(r"[aeiouAEIOU]")
                first_vowel_mo = vowel_pattern.search(word, pos=0)
                if first_vowel_mo:
                    first_vowel = first_vowel_mo.group(0)
                    pos = word.index(first_vowel) + 1
                    second_vowel_mo = vowel_pattern.search(
                        word,
                        pos=pos,
                    )
                    if second_vowel_mo:
                        second_vowel = second_vowel_mo.group(0)
                        pos = word.index(second_vowel, pos)
                        if not is_word_accented:
                            word = word[:pos+1] + "́" + word[pos+1:]
                    elif not is_word_accented:
                        ALWAYS_UNACCENTED = [
                            "na",
                            "waŋ",
                            "kiŋ",
                            "k'uŋ",
                        ]
                        if word not in ALWAYS_UNACCENTED:
                            word = word[:pos] + "́" + word[pos:]
                word = unicodedata.normalize("NFC", word)
                result += word + whitespace_sequence
            output_text = result
    return unicodedata.normalize("NFC", output_text)


def normalize_replace_rules(rules):
    """ From a given Replace rule, derives rules with the following modifications:
        1. A version of the rule with all lower case letters.
        2. A version of the rule with the initial letter only uppercase.
        3. All vowels match their accented and unaccented versions,
            e.g. "a" matches "a" and "á".
        4. Prevent patterns from matching only part of a sequence of
           combining diacritics (in other words, h shouldn't match ȟ even
           though the former is a prefix of the latter because it would
           leave an orphaned combining diacritic character)
    """
    normalized_rules = []
    for rule_type, target, repl in rules:
        assert rule_type == "Replace"
        target = target.lower()
        repl = repl.lower()
        target = unicodedata.normalize("NFD", target)
        repl = unicodedata.normalize("NFD", repl)
        target = re.sub(r"([aeiou])", r"\1(́)?", target) # a -> a(́)?
        target += r"(?=\w|\s|[!\"#\$%&'\(\)\*+,-\./:;<=>\?@\[\\\]\^_`\{\|\}~]|$)"
        repl = re.sub(r"([aeiou])", r"\1\\1", repl) # a -> a\1
        normalized_rules.append((rule_type, target, repl))
        normalized_rules.append((rule_type, target.upper(), repl.upper()))
        if target:
            target = target[0].upper() + target[1:]
        if repl:
            repl = repl[0].upper() + repl[1:]
        normalized_rules.append((rule_type, target, repl))
    return normalized_rules

# This set of rules converts orthographies to phonemic backend.
def convert_uminn_to_phoneme(input_text):
    rules = """
        Replace,aŋ,ã
        Replace,iŋ,ĩ
        Replace,uŋ,ũ
        Replace,c̣,tʃʰ
        Replace,cʼ,tʃʼ
        Replace,c,tʃ
        Replace,ḳ,kʰ
        Replace,p̣,pʰ
        Replace,ṭ,tʰ
        Replace,ḣʼ,xʼ
        Replace,ḣ,x
        Replace,ṡʼ,ʃʼ
        Replace,ṡ,ʃ
        Replace,ġ,ɣ
        Replace,ż,ʒ
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    return convert(normalized_rules, input_text)

def convert_llc_to_phoneme(input_text):
    rules = """
        Replace,aŋ,ã
        Replace,iŋ,ĩ
        Replace,uŋ,ũ
        Replace,čh,tʃʰ
        Replace,čʼ,tʃʼ
        Replace,č,tʃ
        Replace,kȟ,kʰ
        Replace,kh,kʰ
        Replace,pȟ,pʰ
        Replace,ph,pʰ
        Replace,tȟ,tʰ
        Replace,th,tʰ
        Replace,ȟʼ,xʼ
        Replace,ȟ,x
        Replace,šʼ,ʃʼ
        Replace,š,ʃ
        Replace,ǧ,ɣ
        Replace,ž,ʒ
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("LLC to Phonemic accents",))
    return convert(normalized_rules, input_text)

def convert_whitehat_to_phoneme(input_text):
    rules = """
        Replace,ċ,tʃʰ
        Replace,c’,tʃʼ
        Replace,č’,tʃʼ
        Replace,c,tʃ
        Replace,ka,kʰa
        Replace,ke,kʰe
        Replace,ki,kʰi
        Replace,ko,kʰo
        Replace,ku,kʰu
        Replace,k̇,kʰ
        Replace,k̄,k
        Replace,pa,pʰa
        Replace,pe,pʰe
        Replace,pi,pʰi
        Replace,po,pʰo
        Replace,pu,pʰu
        Replace,ṗ,pʰ
        Replace,p̄,p
        Replace,ta,tʰa
        Replace,te,tʰe
        Replace,ti,tʰi
        Replace,to,tʰo
        Replace,tu,tʰu
        Replace,ṫ,tʰ
        Replace,t̄,t
        Replace,ḣʼ,xʼ
        Replace,ḣ,x
        Replace,ṡʼ,ʃʼ
        Replace,ṡ,ʃ
        Replace,ġ,ɣ
        Replace,j,ʒ
        Replace,ƞ,ŋ
        Replace,aŋ,ã
        Replace,iŋ,ĩ
        Replace,uŋ,ũ
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("LLC to Phonemic accents",))
    return convert(normalized_rules, input_text)

# This set of rules converts phonemic backend orthographies.
def convert_phoneme_to_uminn(input_text):
    rules = """
        Replace,ã,aŋ
        Replace,ĩ,iŋ
        Replace,ũ,uŋ
        Replace,tʃʰ,c̣
        Replace,tʃʼ,cʼ
        Replace,tʃ,c
        Replace,kʰ,ḳ
        Replace,pʰ,p̣
        Replace,tʰ,ṭ
        Replace,xʼ,ḣʼ
        Replace,x,ḣ
        Replace,ʃʼ,ṡʼ
        Replace,ʃ,ṡ
        Replace,ɣ,ġ
        Replace,ʒ,ż
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    return convert(normalized_rules, input_text)

def convert_phoneme_to_llc_unvelarized(input_text):
    rules = """
        Replace,ã,aŋ
        Replace,ĩ,iŋ
        Replace,ũ,uŋ
        Replace,tʃʰ,čh
        Replace,tʃʼ,čʼ
        Replace,tʃ,č
        Replace,kʰ,kh
        Replace,pʰ,ph
        Replace,tʰ,th
        Replace,xʼ,ȟʼ
        Replace,x,ȟ
        Replace,ʃʼ,šʼ
        Replace,ʃ,š
        Replace,ɣ,ǧ
        Replace,ʒ,ž
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("Phonemic to LLC accents",))
    return convert(normalized_rules, input_text)

def convert_phoneme_to_llc_velar_aspiration(input_text):
    rules = """
        Replace,ã,aŋ
        Replace,ĩ,iŋ
        Replace,ũ,uŋ
        Replace,tʃʰ,čh
        Replace,tʃʼ,čʼ
        Replace,tʃ,č
        Replace,kʰ,kh
        Replace,pʰ,ph
        Replace,tʰ,th
        Replace,xʼ,ȟʼ
        Replace,x,ȟ
        Replace,ʃʼ,šʼ
        Replace,ʃ,š
        Replace,ɣ,ǧ
        Replace,ʒ,ž
        Replace,kha,kȟa
        Replace,kho,kȟo
        Replace,khuŋ,kȟuŋ
        Replace,pha,pȟa
        Replace,pho,pȟo
        Replace,phuŋ,pȟuŋ
        Replace,phe,pȟe
        Replace,tha,tȟa
        Replace,tho,tȟo
        Replace,thuŋ,tȟuŋ
        Replace,the,tȟe
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("Phonemic to LLC accents",))
    return convert(normalized_rules, input_text)

def convert_phoneme_to_whitehat_unvelarized(input_text):
    rules = """
        Replace,ã,aŋ
        Replace,ĩ,iŋ
        Replace,ũ,uŋ
        Replace,ŋ,ƞ
        Replace,tʃʰ,ċ
        Replace,tʃʼ,c’
        Replace,tʃ,c
        Replace,kʰ,k̇
        Replace,ka,k̄a
        Replace,ke,k̄e
        Replace,ki,k̄i
        Replace,ko,k̄o
        Replace,ku,k̄u
        Replace,k̇,k
        Replace,pʰ,ṗ
        Replace,pa,p̄a
        Replace,pe,p̄e
        Replace,pi,p̄i
        Replace,po,p̄o
        Replace,pu,p̄u
        Replace,ṗ,p
        Replace,tʰ,ṫ
        Replace,ta,t̄a
        Replace,te,t̄e
        Replace,ti,t̄i
        Replace,to,t̄o
        Replace,tu,t̄u
        Replace,ṫ,t
        Replace,xʼ,ḣʼ
        Replace,x,ḣ
        Replace,ʃʼ,ṡʼ
        Replace,ʃ,ṡ
        Replace,ɣ,ġ
        Replace,ʒ,j
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    return convert(normalized_rules, input_text)

def convert_phoneme_to_whitehat_velar_aspiration(input_text):
    rules = """
        Replace,ã,aŋ
        Replace,ĩ,iŋ
        Replace,ũ,uŋ
        Replace,ŋ,ƞ
        Replace,tʃʰ,ċ
        Replace,tʃʼ,c’
        Replace,tʃ,c
        Replace,kʰ,k̇
        Replace,ka,k̄a
        Replace,ke,k̄e
        Replace,ki,k̄i
        Replace,ko,k̄o
        Replace,ku,k̄u
        Replace,k̇e,ke
        Replace,k̇i,ki
        Replace,k̇u,ku
        Replace,kuƞ,k̇uƞ
        Replace,pʰ,ṗ
        Replace,pa,p̄a
        Replace,pe,p̄e
        Replace,pi,p̄i
        Replace,po,p̄o
        Replace,pu,p̄u
        Replace,ṗi,pi
        Replace,ṗu,pu
        Replace,puƞ,ṗuƞ
        Replace,tʰ,ṫ
        Replace,ta,t̄a
        Replace,te,t̄e
        Replace,ti,t̄i
        Replace,to,t̄o
        Replace,tu,t̄u
        Replace,ṫi,ti
        Replace,ṫu,tu
        Replace,tuƞ,ṫuƞ
        Replace,xʼ,ḣʼ
        Replace,x,ḣ
        Replace,ʃʼ,ṡʼ
        Replace,ʃ,ṡ
        Replace,ɣ,ġ
        Replace,ʒ,j
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    return convert(normalized_rules, input_text)