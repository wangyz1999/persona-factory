"""Location generator: address, city/region, postal, timezone, coordinates.

Geography is **coherent**: each locale ships a ``places`` list where every entry
bundles a real ``{city, region, timezone, lat, lon}``. The generator samples one
*place* and derives region/timezone/coordinates from it, so a persona's city,
region, timezone and map coordinates always agree (this is an intra-``location``
key-link). A ``location.city`` override selects the matching place when known.

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


def _place_for_city(places: list[dict[str, Any]], city: str) -> dict[str, Any]:
    """Return the place entry for ``city``, or the first place as a fallback.

    The fallback covers an explicit ``location.city`` override that isn't one of
    the locale's known cities, so generation still produces a valid (if generic)
    region/timezone/coordinate set.
    """
    for place in places:
        if place["city"] == city:
            return place
    return places[0]


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

        # Sample a coherent place; city/region/timezone/coords all come from it.
        places = locale_data["places"]
        cities = [p["city"] for p in places]
        city = pick(rng, config, "location.city", cities)
        place = _place_for_city(places, city)
        # A region override still wins; otherwise the place's region is used.
        region = pick(rng, config, "location.region", [place["region"]])
        # Jitter coordinates slightly (~a few km) around the city center so a
        # pool isn't stacked on one exact point, while staying in the locale.
        latitude = round(place["lat"] + rng.uniform(-0.05, 0.05), 5)
        longitude = round(place["lon"] + rng.uniform(-0.05, 0.05), 5)

        location = Location(
            street_address=address,
            city=city,
            region=region,
            country=locale_data["country"],
            country_code=locale_data["country_code"],
            postal_code=fill_mask(rng, locale_data["postal_format"]),
            timezone=place["timezone"],
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
            latitude=latitude,
            longitude=longitude,
        )
        persona.location = location


register(LocationGenerator())
