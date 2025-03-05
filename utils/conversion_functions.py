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
        elif rule_type == "LLC to UMinn accents":
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
        elif rule_type == "UMinn to LLC accents":
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


def convert_llc_to_uminn(input_text):
    rules = """
        Replace,š,ṡ
        Replace,ȟ,ḣ
        Replace,ǧ,ġ
        Replace,č,c
        Replace,ch,c̣
        Replace,kh,ḳ
        Replace,kḣ,ḳ
        Replace,ph,p̣
        Replace,pḣ,p̣
        Replace,th,ṭ
        Replace,tḣ,ṭ
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("LLC to UMinn accents",))
    return convert(normalized_rules, input_text)


def convert_uminn_to_llc(input_text):
    rules = """
        Replace,ṡ,š
        Replace,ġ,ǧ
        Replace,c̣,čh
        Replace,c,č
        Replace,ḳa,kȟa
        Replace,ḳo,kȟo
        Replace,ḳuŋ,kȟuŋ
        Replace,ḳe,khe
        Replace,ḳi,khi
        Replace,ḳu,ku
        Replace,p̣a,pȟa
        Replace,p̣o,pȟo
        Replace,p̣uŋ,pȟuŋ
        Replace,p̣e,pȟe
        Replace,p̣i,phi
        Replace,p̣u,phu
        Replace,ṭa,tȟa
        Replace,ṭo,tȟo
        Replace,ṭuŋ,tȟuŋ
        Replace,ṭe,tȟe
        Replace,ṭi,thi
        Replace,ṭu,thu
        Replace,ḣ,ȟ
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("UMinn to LLC accents",))
    return convert(case_normalized_rules, input_text)


def convert_uminn_to_llc_no_velar_aspiration(input_text):
    rules = """
        Replace,ṡ,š
        Replace,ġ,ǧ
        Replace,c̣,čh
        Replace,c,č
        Replace,ḳa,kha
        Replace,ḳo,kho
        Replace,ḳuŋ,khuŋ
        Replace,ḳe,khe
        Replace,ḳi,khi
        Replace,ḳu,ku
        Replace,p̣a,pha
        Replace,p̣o,pho
        Replace,p̣uŋ,phuŋ
        Replace,p̣e,phe
        Replace,p̣i,phi
        Replace,p̣u,phu
        Replace,ṭa,tha
        Replace,ṭo,tho
        Replace,ṭuŋ,thuŋ
        Replace,ṭe,the
        Replace,ṭi,thi
        Replace,ṭu,thu
        Replace,ḣ,h
    """.strip().split("\n")
    rules = [
        tuple(e.strip() for e in rule.split(","))
        for rule in rules
    ]
    normalized_rules = normalize_replace_rules(rules)
    normalized_rules.append(("UMinn to LLC accents",))
    return convert(normalized_rules, input_text)