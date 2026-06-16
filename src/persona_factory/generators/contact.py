"""Contact / digital generator: email, phone, username, social handles.

Emails and usernames derive from the persona's name so they read coherently.
Phone numbers follow the locale's phone mask. All values are clearly synthetic.
"""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING, Any

from persona_factory.generators.base import Generator, register
from persona_factory.generators.location import fill_mask
from persona_factory.models.persona import Contact, SocialProfile

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

# RFC 5737 "documentation" /24 blocks — reserved so a generated address can
# never collide with a real, routable host.
_DOC_IP_PREFIXES = ("192.0.2", "198.51.100", "203.0.113")
_PLATFORMS = ["twitter", "instagram", "github", "linkedin", "tiktok", "mastodon"]
_DEVICES = [
    "iPhone 15",
    "Samsung Galaxy S24",
    "Google Pixel 8",
    "MacBook Pro",
    "Windows 11 laptop",
    "iPad Air",
]


def _romanize(text: str, table: dict[str, str]) -> str:
    """Map a name to its Latin form via the locale's romanization table.

    Tries the whole token first, then a character-by-character fallback so a
    name built from known characters still romanizes even if absent as a unit.
    Returns ``""`` when nothing is known (caller falls back to a generic stem).
    """
    if not text:
        return ""
    if text in table:
        return table[text]
    parts = [table[ch] for ch in text if ch in table]
    return "".join(parts)


def _slug(text: str, table: dict[str, str] | None = None) -> str:
    """ASCII-fold a name fragment into a handle-safe lowercase token.

    For non-Latin scripts the fragment is romanized via ``table`` first, so the
    handle still reflects the persona's name instead of folding to empty.
    """
    if table:
        romanized = _romanize(text, table)
        if romanized:
            text = romanized
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch for ch in ascii_text.lower() if ch.isalnum())
    return cleaned


class ContactGenerator(Generator):
    domain = "contact"
    depends_on = ("identity",)

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        ident = persona.identity
        romanization = locale_data.get("romanization")
        given = _slug(ident.given_name or "user", romanization)
        family = _slug(ident.family_name or "", romanization)
        # If romanization is unavailable and the script ASCII-folds to empty,
        # fall back to a generic stem.
        if not given:
            given = "user"

        suffix = rng.randint(1, 9999)
        stem = f"{given}.{family}" if family else given
        username = f"{given}{family}{suffix}" if family else f"{given}{suffix}"
        domain = rng.choice(locale_data["email_domains"])

        contact = Contact(
            email=f"{stem}{suffix}@{domain}",
            phone=fill_mask(rng, locale_data["phone_format"]),
            username=username,
            device=rng.choice(_DEVICES),
            avatar_seed=f"{username}-{rng.randint(1000, 999999)}",
            ip_address=f"{rng.choice(_DOC_IP_PREFIXES)}.{rng.randint(1, 254)}",
        )

        # 0-3 social profiles
        n_profiles = rng.weighted_choice([0, 1, 2, 3], [0.2, 0.35, 0.3, 0.15])
        platforms = rng.sample(_PLATFORMS, n_profiles) if n_profiles else []
        for platform in platforms:
            contact.social_profiles.append(
                SocialProfile(
                    platform=platform,
                    handle=f"@{username}",
                    url=f"https://{platform}.example/{username}",
                )
            )
        persona.contact = contact


register(ContactGenerator())
