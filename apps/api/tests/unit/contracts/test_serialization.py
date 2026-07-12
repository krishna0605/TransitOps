from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.contracts.dto.common import AwareDateTime, ContractModel, Money
from app.contracts.enums import VehicleStatus


class SerializationProbe(ContractModel):
    identifier: object
    amount: Money
    occurred_at: AwareDateTime
    status: VehicleStatus


def test_contract_serializes_uuid_decimal_utc_and_enum() -> None:
    identifier = uuid4()
    probe = SerializationProbe(
        identifier=identifier,
        amount=Decimal("1250.50"),
        occurred_at=datetime(2026, 7, 12, 10, 0, tzinfo=timezone(timedelta(hours=5, minutes=30))),
        status=VehicleStatus.AVAILABLE,
    )
    assert probe.model_dump(mode="json") == {
        "identifier": str(identifier),
        "amount": "1250.50",
        "occurred_at": "2026-07-12T04:30:00Z",
        "status": "AVAILABLE",
    }


def test_contract_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError, match="datetime must include a timezone offset"):
        SerializationProbe(
            identifier=uuid4(),
            amount=Decimal("1.00"),
            occurred_at=datetime(2026, 7, 12, 10, 0),
            status=VehicleStatus.AVAILABLE,
        )
