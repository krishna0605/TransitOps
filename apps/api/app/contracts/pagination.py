from pydantic import Field

from app.contracts.dto.common import ContractModel


class PageParams(ContractModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
