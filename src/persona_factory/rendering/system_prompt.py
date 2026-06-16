"""Render a persona into a second-person LLM system prompt.

The output instructs a model to *become* the persona ("You are …"), folding in
only the attributes that were actually generated. Two styles are offered:

* ``"roleplay"`` (default) — immersive, character-acting instructions;
* ``"profile"`` — a neutral structured briefing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from persona_factory.models.persona import Persona


def render_system_prompt(persona: Persona, *, style: str = "roleplay") -> str:
    """Return an LLM system prompt describing ``persona``.

    Parameters
    ----------
    style:
        ``"roleplay"`` for immersive character instructions, or ``"profile"``
        for a neutral briefing.
    """
    if style not in {"roleplay", "profile"}:
        raise ValueError(f"unknown style {style!r}; use 'roleplay' or 'profile'")
    lines = _build_lines(persona)
    body = "\n".join(lines)
    if style == "profile":
        return f"# Persona Profile: {persona.display_name}\n\n{body}"

    header = (
        f"You are {persona.display_name}. Fully embody this person in every "
        f"response — their voice, knowledge, opinions, and way of speaking. "
        f"Never break character or mention that you are an AI.\n"
    )
    footer = (
        "\nStay in character. Let your personality, background, and "
        "communication style shape how you respond."
    )
    return f"{header}\n{body}{footer}"


def _build_lines(persona: Persona) -> list[str]:
    lines: list[str] = []

    ident = persona.identity
    bits: list[str] = []
    if ident.age:
        bits.append(f"{ident.age} years old")
    if ident.gender:
        bits.append(str(ident.gender))
    if ident.pronouns:
        bits.append(f"pronouns {ident.pronouns}")
    if ident.nationality:
        bits.append(f"from {ident.nationality}")
    if bits:
        lines.append(f"- **Basics:** {', '.join(bits)}.")

    if ident.spoken_languages:
        langs = ", ".join(
            f"{lang.language} ({lang.proficiency})" if lang.proficiency else lang.language
            for lang in ident.spoken_languages
        )
        lines.append(f"- **Languages:** {langs}.")

    socio = persona.socioeconomic
    if socio:
        job_bits: list[str] = []
        if socio.occupation:
            job_bits.append(f"works as a {socio.occupation}")
        if socio.industry:
            job_bits.append(f"in {socio.industry.lower()}")
        if socio.education_level:
            job_bits.append(f"education: {str(socio.education_level).replace('_', ' ')}")
        if job_bits:
            lines.append(f"- **Work & education:** {', '.join(job_bits)}.")

    pers = persona.personality
    if pers:
        pbits: list[str] = []
        if pers.mbti:
            pbits.append(f"MBTI {pers.mbti}")
        if pers.enneagram_wing:
            pbits.append(f"Enneagram {pers.enneagram_wing}")
        if pers.traits:
            pbits.append("traits: " + ", ".join(pers.traits))
        if pbits:
            lines.append(f"- **Personality:** {'; '.join(pbits)}.")

    beliefs = persona.beliefs
    if beliefs:
        bbits: list[str] = []
        if beliefs.religion and str(beliefs.religion) != "none":
            bbits.append(f"religion: {str(beliefs.religion).replace('_', ' ')}")
        if beliefs.political_orientation:
            bbits.append(f"politics: {str(beliefs.political_orientation).replace('_', ' ')}")
        if beliefs.worldview:
            bbits.append(f"worldview: {beliefs.worldview}")
        if bbits:
            lines.append(f"- **Beliefs:** {'; '.join(bbits)}.")

    life = persona.lifestyle
    if life and (life.hobbies or life.interests):
        lbits: list[str] = []
        if life.hobbies:
            lbits.append("hobbies: " + ", ".join(life.hobbies))
        if life.interests:
            lbits.append("interests: " + ", ".join(life.interests))
        lines.append(f"- **Lifestyle:** {'; '.join(lbits)}.")

    comm = persona.communication
    if comm:
        cbits: list[str] = []
        if comm.tone:
            cbits.append(f"tone: {comm.tone}")
        if comm.formality:
            cbits.append(f"formality: {str(comm.formality).replace('_', ' ')}")
        if comm.verbosity:
            cbits.append(f"verbosity: {comm.verbosity}")
        if comm.humor and str(comm.humor) != "none":
            cbits.append(f"humor: {str(comm.humor).replace('_', ' ')}")
        if comm.catchphrases:
            cbits.append("catchphrases: " + ", ".join(f'"{c}"' for c in comm.catchphrases))
        if cbits:
            lines.append(f"- **Speaking style:** {'; '.join(cbits)}.")

    narr = persona.narrative
    if narr:
        if narr.goals:
            lines.append(f"- **Goals:** {', '.join(narr.goals)}.")
        if narr.fears:
            lines.append(f"- **Fears:** {', '.join(narr.fears)}.")
        if narr.quirks:
            lines.append(f"- **Quirks:** {', '.join(narr.quirks)}.")
        if narr.bio:
            lines.append(f"- **Background:** {narr.bio}")

    return lines
