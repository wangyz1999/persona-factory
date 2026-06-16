"""Synthetic identity-document generator.

Every value here is intentionally **fake** and prefixed/shaped so it cannot be
mistaken for a real, valid document:

* credit cards use the reserved ``4000 0000 0000 0000`` test-card style and pass
  no real issuer check beyond the Luhn digit;
* national IDs / passports carry an explicit ``FAKE-`` marker.

This domain is **opt-in** (not in DEFAULT_DOMAINS) to avoid surprising callers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.generators.base import Generator, register
from persona_factory.generators.location import fill_mask
from persona_factory.models.persona import Documents

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG


def _luhn_complete(rng: RNG, prefix: str, length: int) -> str:
    """Build a ``length``-digit number with a valid Luhn check digit.

    Only used for clearly-fake test-range cards (e.g. the ``400000`` prefix).
    """
    digits = [int(c) for c in prefix]
    while len(digits) < length - 1:
        digits.append(rng.randint(0, 9))
    # Standard Luhn: double every second digit starting from the one just left
    # of the (yet-to-be-appended) check digit, i.e. even indices of the reversed
    # payload.
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    check = (10 - (total % 10)) % 10
    digits.append(check)
    return "".join(str(d) for d in digits)


class DocumentsGenerator(Generator):
    domain = "documents"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        code = locale_data.get("country_code", "XX")
        card = _luhn_complete(rng, "400000", 16)
        formatted_card = " ".join(card[i : i + 4] for i in range(0, 16, 4))
        persona.documents = Documents(
            national_id=f"FAKE-{code}-{fill_mask(rng, '###-##-####')}",
            credit_card=formatted_card,
            iban=f"{code}{fill_mask(rng, '## #### #### #### ####')}",
            license_plate=fill_mask(rng, "???-####"),
            passport_number=f"FAKE{fill_mask(rng, '########')}",
        )


register(DocumentsGenerator())
