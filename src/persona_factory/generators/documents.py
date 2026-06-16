"""Synthetic identity-document generator.

Every value here is intentionally **fake** and prefixed/shaped so it cannot be
mistaken for a real, valid document:

* credit cards use the well-known ``4111 11`` Visa *test* BIN prefix; they carry
  a valid Luhn check digit (so format validators accept them) but the test BIN
  is never issued to a real cardholder;
* IBANs use check digits ``00``, which are structurally invalid in real IBANs
  (the spec only ever uses 02-98), so the value is unmistakably synthetic while
  staying IBAN-shaped;
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

    Only used for clearly-fake test-range cards (e.g. the ``411111`` Visa test
    BIN prefix).
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
        card = _luhn_complete(rng, "411111", 16)
        formatted_card = " ".join(card[i : i + 4] for i in range(0, 16, 4))
        # IBAN check digits "00" are invalid by spec (real ones are 02-98), so
        # the value is IBAN-shaped yet unmistakably synthetic.
        persona.documents = Documents(
            national_id=f"FAKE-{code}-{fill_mask(rng, '###-##-####')}",
            credit_card=formatted_card,
            iban=f"{code}00 {fill_mask(rng, '#### #### #### ####')}",
            license_plate=fill_mask(rng, "???-####"),
            passport_number=f"FAKE{fill_mask(rng, '########')}",
        )


register(DocumentsGenerator())
