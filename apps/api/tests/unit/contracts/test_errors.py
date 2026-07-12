from app.contracts.errors import ErrorCode, ErrorResponse


def test_error_codes_are_unique_and_machine_readable() -> None:
    values = [code.value for code in ErrorCode]
    assert len(values) == len(set(values))
    assert all(value == value.upper() for value in values)
    assert all(" " not in value for value in values)


def test_error_response_preserves_existing_envelope() -> None:
    response = ErrorResponse(
        code=ErrorCode.VALIDATION_ERROR,
        message="The request contains invalid data.",
        details={"fields": {"email": ["invalid"]}},
        request_id="request-123",
    )
    assert response.model_dump(mode="json") == {
        "code": "VALIDATION_ERROR",
        "message": "The request contains invalid data.",
        "details": {"fields": {"email": ["invalid"]}},
        "request_id": "request-123",
    }
