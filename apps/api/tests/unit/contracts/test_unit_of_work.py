from app.contracts.unit_of_work import UnitOfWork


def test_unit_of_work_protocol_exposes_explicit_transaction_methods() -> None:
    assert "commit" in UnitOfWork.__dict__
    assert "rollback" in UnitOfWork.__dict__
    assert "__aenter__" in UnitOfWork.__dict__
    assert "__aexit__" in UnitOfWork.__dict__
