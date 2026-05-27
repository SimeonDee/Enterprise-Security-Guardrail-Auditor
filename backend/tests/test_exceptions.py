import pytest

from app.core.exceptions import (
    APIError,
    ConflictError,
    InternalError,
    NotFoundError,
    ValidationError,
)


def test_not_found_error():
    err = NotFoundError("Guardrail", 42)
    assert err.status_code == 404
    assert "42" in err.detail
    assert err.error_code == "NOT_FOUND"


def test_conflict_error():
    err = ConflictError("Guardrail", "name", "test-rule")
    assert err.status_code == 409
    assert "test-rule" in err.detail
    assert err.error_code == "CONFLICT"


def test_validation_error():
    err = ValidationError("Invalid input")
    assert err.status_code == 422
    assert err.error_code == "VALIDATION_ERROR"


def test_internal_error():
    err = InternalError()
    assert err.status_code == 500
    assert err.error_code == "INTERNAL_ERROR"


def test_base_api_error():
    err = APIError(status_code=418, detail="I'm a teapot", error_code="TEAPOT")
    assert err.status_code == 418
    assert err.error_code == "TEAPOT"
