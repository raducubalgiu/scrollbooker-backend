from pydantic import BaseModel

class UserCountersBase(BaseModel):
    user_id: int
    followings_count: int
    followers_count: int
    products_count: int
    posts_count: int
    ratings_count: int
    ratings_average: int

    class Config:
        from_attributes = True

class UserCountersResponse(UserCountersBase):
    pass
        