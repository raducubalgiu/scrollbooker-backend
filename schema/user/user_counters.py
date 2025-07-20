from decimal import Decimal

from pydantic import BaseModel, field_serializer

class UserCountersBase(BaseModel):
    user_id: int
    followings_count: int
    followers_count: int
    products_count: int
    posts_count: int
    ratings_count: int
    ratings_average: Decimal

    @field_serializer("ratings_average", return_type=str)
    def serialize_price(self, value: Decimal, _info) -> str:
        return '{0:.2f}'.format(value).rstrip('0').rstrip('.') if value is not None else None

    class Config:
        from_attributes = True

class UserCountersResponse(UserCountersBase):
    pass
        