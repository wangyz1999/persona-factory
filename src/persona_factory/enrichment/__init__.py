"""Optional LLM enrichment of generated personas.

This subpackage is **opt-in**: it requires the ``enrichment`` extra
(``pip install persona-factory[enrichment]``), which pulls in the ``anthropic``
SDK. Core persona generation never imports or depends on it.
"""

from __future__ import annotations

from persona_factory.enrichment.claude import enrich

__all__ = ["enrich"]
