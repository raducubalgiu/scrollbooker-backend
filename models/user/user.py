from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float, TIMESTAMP, func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from backend.core.enums.enums import GenderType
from backend.models import Base, Business, EmploymentRequest

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=True)
    username = Column(String(35), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    bio = Column(String(100), nullable=True)
    profession = Column(String(100), nullable=False, default='Creator')
    gender = Column(String(String(10)), default=GenderType.OTHER)
    instant_booking = Column(Boolean, nullable=False, default=False)
    avatar = Column(String)
    date_of_birth = Column(Date, nullable=True)
    last_known_lat = Column(Float, nullable=True)
    last_known_lng = Column(Float, nullable=True)
    phone_number = Column(String(20), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign Key
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    # Relations
    owner_business = relationship("Business", back_populates="business_owner", uselist=False, foreign_keys=[Business.owner_id])

    employee_business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    employee_business = relationship("Business", back_populates="employees", foreign_keys=[employee_business_id])

    counters = relationship('UserCounters', back_populates="user", uselist=False, cascade="all, delete")
    role = relationship("Role", back_populates="users")
    bookmark_posts = relationship("BookmarkPost", back_populates="user")

    following = relationship("Follow", foreign_keys="[Follow.follower_id]", back_populates="follower", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="[Follow.followee_id]", back_populates="followee", cascade="all, delete-orphan")

    comments = relationship("Comment", back_populates="user")
    posts = relationship("Post", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")

    products = relationship("Product", back_populates="user")
    currencies_assoc = relationship("UserCurrency", back_populates="user")
    currencies = association_proxy("currencies_assoc", "currency")

    customer_reviews = relationship("Review", foreign_keys="[Review.customer_id]", back_populates="customer")
    business_or_employee_reviews = relationship("Review", foreign_keys="[Review.user_id]", back_populates="business_or_employee")

    appointments_customer = relationship(
        "Appointment",
        foreign_keys="[Appointment.customer_id]",
        back_populates="customer")

    appointments_user = relationship(
        "Appointment",
        foreign_keys="[Appointment.user_id]",
        back_populates="user"
    )

    employment_requests_as_employee = relationship(
        "EmploymentRequest",
        back_populates="employee",
        foreign_keys=[EmploymentRequest.employee_id],
        cascade="all, delete-orphan"
    )
    employment_requests_as_employer = relationship(
        "EmploymentRequest",
        back_populates="employer",
        foreign_keys=[EmploymentRequest.employer_id],
    )