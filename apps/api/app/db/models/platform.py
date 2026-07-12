from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")


class OrganizationSettings(TimestampMixin, VersionMixin, Base):
    __tablename__ = "organization_settings"

    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    distance_unit: Mapped[str] = mapped_column(String(8), nullable=False, default="km")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Kolkata")


class User(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    @property
    def user_id(self) -> UUID:
        return self.id


class Membership(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),
        Index("ix_memberships_org_role", "organization_id", "role"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")


class RefreshSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "refresh_sessions"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False
    )
    family_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[UUID | None] = mapped_column(Uuid)


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_org_created", "organization_id", "created_at"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    actor_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(60), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(Uuid)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    request_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OutboxEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "outbox_events"
    __table_args__ = (Index("ix_outbox_pending", "processed_at", "available_at"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(60), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IdempotencyRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("organization_id", "key", "operation", name="uq_idempotency_scope"),
    )

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer)
    response_body: Mapped[dict[str, object] | None] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Document(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "documents"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    uploaded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"), index=True)
    user_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReportExport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_exports"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"), index=True)
    requested_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    report_type: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    filters: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    object_key: Mapped[str | None] = mapped_column(String(512))
    error: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ContactSubmission(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "contact_submissions"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_ip_hash: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
