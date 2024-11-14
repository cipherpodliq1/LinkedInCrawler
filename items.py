from util.database import Database
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Profile:
    fullname: str = None
    first_name: str = None
    maiden_name: str = None
    last_name: str = None
    birthdate: str = None
    address: str = None
    email_address: list[str] = None
    phone_numbers: list[str] = None
    wechat_contact_info: str = None
    twitter: str = None
    websites: str = None
    headline: str = None
    public_identifier: str = None
    profile_id: str = None
    about: str = None
    experience: dict = None
    education: dict = None
    licenses_and_certifications: dict = None
    volunteering_experience: dict = None
    interests: dict = field(default_factory=dict)
    skills: list[dict] = field(default_factory=list)
    recommendations: dict = field(default_factory=dict)
    services: dict = field(default_factory=dict)
    languages: dict = None
    volunteer_causes: dict = None
    recommended_profiles_ids: list[str] = field(default_factory=list)
    based_location: str = None
    profile_language: str = None
    variant: str = None
    joined_date: str = None
    last_profile_updates: dict = field(default_factory=dict)

    __attrs__ = [
        "fullname", "first_name", "maiden_name", "last_name", "birthdate", "based_location", "profile_language",
        "address", "email_address", "phone_numbers", "wechat_contact_info", "twitter", "websites", "headline",
        "public_identifier", "profile_id", "about", "experience", "education", "licenses_and_certifications",
        "volunteering_experience", "interests", "skills", "recommendations", "services", "languages", "variant",
        "volunteer_causes", "recommended_profiles_ids", "joined_date", "last_profile_updates"  # len = 31
    ]

    def insert_to_db(self, db: Database) -> bool:
        """ inserts the profile items into the Database object. """
        return db.insert_profile((str(self), ))

    def items(self) -> list[tuple]:
        """ returns all items in the object as a tuple. """
        return [(attr, self.get(attr)) for attr in Profile.__attrs__]

    def get(self, key: str) -> Any:
        """ returns an attribute of the object. """
        return self.__getitem__(str(key))

    def __str__(self) -> str:
        """ returns a string representation of the object. """
        return str({attr: self.get(attr) for attr in Profile.__attrs__})

    def __getitem__(self, item: str) -> Any:
        return getattr(self, str(item))

    def __setitem__(self, key: str, value: Any) -> Any:
        return setattr(self, str(key), value)

    def __add__(self, other):
        return Profile(**dict(self.items() + other.items()))
