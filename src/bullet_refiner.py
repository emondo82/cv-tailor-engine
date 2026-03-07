from __future__ import annotations

import re
from typing import List


VERB_UPGRADES = {
    "carried out": "Conducted",
    "worked on": "Contributed to",
    "helped": "Supported",
    "did": "Performed",
    "made": "Developed",
    "handled": "Managed",
    "looked at": "Analysed",
    "involved in": "Participated in",
    "responsible for": "Led",
    "was responsible for": "Led",
    "participated in": "Participated in",
    "supported": "Supported",
    "managed": "Managed",
    "conducted": "Conducted",
    "analysed": "Analysed",
    "analyzed": "Analysed",
    "developed": "Developed",
    "led": "Led",
}


NOISE_PREFIXES = [
    "tasks included",
    "responsibilities included",
    "key responsibilities included",
    "main responsibilities included",
    "work included",
]


COMMON_PHRASE_FIXES = {
    "and translate them into": "and translated them into",
    "and translate": "and translated",
    "and elicit": "and elicited",
    "Ensure processes": "Ensured processes",
    "Identify inefficiencies": "Identified inefficiencies",
    "Analyse and improve": "Analysed and improved",
    "Analyze and improve": "Analysed and improved",
    "Monitor process performance": "Monitored process performance",
    "suggest solutions": "suggested solutions",
    "recommend improvements": "recommended improvements",
    "was involved in": "participated in",
    "helped with": "supported",
    "performed analysis of": "analysed",
    "performed review of": "reviewed",
    "create and maintain": "created and maintained",
    "identify and define": "identified and defined",
    "gather and analyze": "gathered and analysed",
    "gather and analyse": "gathered and analysed",
}


READABILITY_FIXES = {
    "in order to": "to",
    "with the help of": "using",
    "the existing": "existing",
    "the current": "current",
    "for the purpose of": "for",
    "in the context of": "for",
    "a number of": "several",
}


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_trailing_punctuation(text: str) -> str:
    return text.strip().rstrip(" .;:")


def remove_noise_prefix(text: str) -> str:
    lower = text.lower()
    for prefix in NOISE_PREFIXES:
        if lower.startswith(prefix):
            text = text[len(prefix):].lstrip(" :-")
            break
    return text


def normalize_leading_verb(text: str) -> str:
    lower = text.lower()

    for weak, strong in sorted(VERB_UPGRADES.items(), key=lambda x: len(x[0]), reverse=True):
        if lower.startswith(weak + " "):
            return strong + text[len(weak):]

    return text[:1].upper() + text[1:] if text else text


def apply_phrase_fixes(text: str) -> str:
    refined = text
    for old, new in COMMON_PHRASE_FIXES.items():
        refined = refined.replace(old, new)
    return refined


def tighten_phrasing(text: str) -> str:
    refined = text
    for old, new in READABILITY_FIXES.items():
        refined = refined.replace(old, new)
    return refined


def fix_double_letters(text: str) -> str:
    text = re.sub(r"(translated)d\b", r"\1", text)
    text = re.sub(r"(analysed)d\b", r"\1", text)
    return text


def is_safe_refinement(original: str, refined: str) -> bool:
    if not refined or len(refined) < 4:
        return False

    original_len = len(original.strip())
    refined_len = len(refined.strip())

    if original_len > 0:
        ratio = refined_len / original_len
        if ratio < 0.65 or ratio > 1.60:
            return False

    original_acronyms = set(re.findall(r"\b[A-Z]{2,}\b", original))
    refined_acronyms = set(re.findall(r"\b[A-Z]{2,}\b", refined))

    if not original_acronyms.issubset(refined_acronyms):
        return False

    return True


def refine_bullet(bullet: str) -> str:
    if not bullet or not bullet.strip():
        return bullet

    original = bullet.strip()

    refined = original
    refined = clean_whitespace(refined)
    refined = remove_noise_prefix(refined)
    refined = strip_trailing_punctuation(refined)
    refined = normalize_leading_verb(refined)
    refined = apply_phrase_fixes(refined)
    refined = tighten_phrasing(refined)
    refined = fix_double_letters(refined)

    if not is_safe_refinement(original, refined):
        return original

    return refined


def refine_bullets(bullets: List[str]) -> List[str]:
    refined_items: List[str] = []

    for bullet in bullets:
        try:
            refined_items.append(refine_bullet(bullet))
        except Exception:
            refined_items.append(bullet)

    return refined_items