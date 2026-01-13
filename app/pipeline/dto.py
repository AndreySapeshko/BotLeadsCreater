from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SearchHit:
    query_id: str
    url: str
    rank: int | None = None


@dataclass(frozen=True)
class DomainCandidate:
    query_id: str
    domain: str
    source_url: str
    rank: int | None
    seen_at: datetime


@dataclass(frozen=True)
class HtmlPage:
    domain: str
    url: str
    html: str


@dataclass(frozen=True)
class SiteSignals:
    domain: str
    has_form: bool
    has_telegram: bool
    has_chat: bool
    has_booking_words: bool
