import re
import unicodedata


COMBINING_ACCENTS = ("̀", "́")


def convert(rules, input_text) -> str:
    output_text = input_text
    for rule_type, *rule_args in rules:
        if rule_type == "Replace":
            target, repl = rule_args
            target = unicodedata.normalize("NFC", target)
            repl = unicodedata.normalize("NFC", repl)
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
                        word = word[:pos] + "́" + word[pos:]
                word = unicodedata.normalize("NFC", word)
                result += word + whitespace_sequence
            output_text = result
    return output_text


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
    rules = [tuple(rule.split(",")) for rule in rules]
    case_normalized_rules = []
    for rule_type, *rule_args in rules:
        rule_type = rule_type.strip()
        case_normalized_rules.append(tuple(
            [rule_type] + [e.upper() for e in rule_args]
        ))
        case_normalized_rules.append(tuple(
            [rule_type] + [e.lower() for e in rule_args]
        ))
    case_normalized_rules.append(("LLC to UMinn accents",))
    return convert(case_normalized_rules, input_text)


def convert_uminn_to_llc(input_text):
    # Same as convert_llc_to_uminn but reverses both the order of
    # rules as well as the order of replacements.
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
    rules = [tuple(rule.split(",")) for rule in rules]
    case_normalized_rules = []
    for rule_type, *rule_args in rules:
        rule_type = rule_type.strip()
        case_normalized_rules.append(tuple(
            [rule_type] + [e.upper() for e in rule_args]
        ))
        case_normalized_rules.append(tuple(
            [rule_type] + [e.lower() for e in rule_args]
        ))
    case_normalized_rules.append(("UMinn to LLC accents",))
    return convert(case_normalized_rules, input_text)