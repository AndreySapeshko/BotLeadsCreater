import enum
import uuid
from datetime import datetime

from sqlalchemy import UUID, BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    is_active = Column(Boolean, index=True, default=False)
    is_admin = Column(Boolean, default=False)
    password_hash = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} username={self.username}>"


class DomainStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    LEAD = "lead"
    SKIP = "skip"
    CONTACTED = "contacted"


class Query(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), index=True, nullable=False)
    business_type = Column(String, nullable=True)
    region = Column(String, nullable=True, default="ru")
    search_phrase = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Domain(Base):
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String, nullable=False, unique=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    global_status = Column(String, default=DomainStatus.UNKNOWN, index=True)


class SearchStatus(str, enum.Enum):
    PAUSE = "pause"
    LIVE = "live"
    CLOSED = "closed"


class Search_cache(Base):
    __tablename__ = "search_caches"

    id = Column(Integer, primary_key=True)
    query_id = Column(UUID, ForeignKey("queries.id"), index=True, nullable=False)
    domain_id = Column(UUID, ForeignKey("domains.id"), index=True, nullable=False)
    seen_at = Column(DateTime)
    rank = Column(Integer)
    status = Column(String, default=SearchStatus.LIVE, index=True)

    __table_args__ = (UniqueConstraint("query_id", "domain_id"),)


class UserDomainStatus(str, enum.Enum):
    NEW = "new"
    LEAD = "lead"
    CONTACTED = "contacted"
    IGNORED = "ignored"


class UserDomain(Base):
    __tablename__ = "user_domains"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True, nullable=False)
    domain_id = Column(UUID, ForeignKey("domains.id"), index=True, nullable=False)
    status = Column(String, default=UserDomainStatus.NEW, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)

    __table_args__ = (UniqueConstraint("user_id", "domain_id"),)
