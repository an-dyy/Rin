from __future__ import annotations

import pytest
import rin


class TestHTTPException:
    @pytest.fixture()
    def data(self) -> dict[str, str | int]:
        return {"message": "foo", "code": 1}

    @pytest.fixture()
    def error(self, data: dict[str, str | int]) -> rin.HTTPException:
        return rin.HTTPException(data)

    def test_init(self, data: dict[str, str | int], error: rin.HTTPException) -> None:
        assert isinstance(error, Exception)
        assert error.data == data
        assert error.message == "foo"
        assert error.code == 1

    def test_subclasses(self, data: dict[str, str | int]) -> None:
        assert isinstance(rin.Unauthorized(data), rin.HTTPException)
        assert isinstance(rin.BadRequest(data), rin.HTTPException)
        assert isinstance(rin.Forbidden(data), rin.HTTPException)
        assert isinstance(rin.NotFound(data), rin.HTTPException)
