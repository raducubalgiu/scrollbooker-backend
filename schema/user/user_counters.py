from pydantic import BaseModel, condecimal

class UserCountersBase(BaseModel):
    user_id: int
    followings_count: int
    followers_count: int
    products_count: int
    posts_count: int
    ratings_count: int
    ratings_average: condecimal(gt=0, max_digits=10, decimal_places=1)

    class Config:
        from_attributes = True

class UserCountersResponse(UserCountersBase):
    pass
        