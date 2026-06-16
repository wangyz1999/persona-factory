"""Location generator: address, city/region, postal, timezone, coordinates.

Addresses are assembled from the locale's ``address_format`` template and its
street name/suffix pools; postal codes and phone numbers follow the locale's
mask (``#`` -> digit, ``?`` -> uppercase letter).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.generators._helpers import as_enum, pick
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import SettlementType
from persona_factory.models.persona import Location

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def fill_mask(rng: RNG, mask: str) -> str:
    """Expand a mask: ``#`` -> digit, ``?`` -> uppercase letter, else literal."""
    out = []
    for ch in mask:
        if ch == "#":
            out.append(str(rng.randint(0, 9)))
        elif ch == "?":
            out.append(rng.choice(_LETTERS))
        else:
            out.append(ch)
    return "".join(out)


class LocationGenerator(Generator):
    domain = "location"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        street = pick(rng, config, "location.street", locale_data["street_names"])
        suffix = rng.choice(locale_data["street_suffixes"])
        number = rng.randint(1, 9999)
        address = locale_data["address_format"].format(number=number, street=street, suffix=suffix)

        location = Location(
            street_address=address,
            city=pick(rng, config, "location.city", locale_data["cities"]),
            region=pick(rng, config, "location.region", locale_data["regions"]),
            country=locale_data["country"],
            country_code=locale_data["country_code"],
            postal_code=fill_mask(rng, locale_data["postal_format"]),
            timezone=rng.choice(locale_data["timezones"]),
            settlement_type=as_enum(
                pick(
                    rng,
                    config,
                    "location.settlement_type",
                    list(SettlementType),
                    [0.45, 0.4, 0.15],
                ),
                SettlementType,
            ),
            latitude=round(rng.uniform(-60, 70), 5),
            longitude=round(rng.uniform(-180, 180), 5),
        )
        persona.location = location


register(LocationGenerator())
