import os
import random
from typing import List
from typing import List
import faker

fake = faker.Faker()

GENDER_MAPPING = {"M": "male", "F": "female"}


def gen_profile() -> str:
    lines: List[str] = []
    profile = fake.profile()
    for k, v in profile.items():
        if isinstance(v, list):
            v = ", ".join(v)
        if isinstance(v, str):
            v = v.replace("\n", ", ")
        if k == "sex":
            v = GENDER_MAPPING[v]
        if not isinstance(v, (str, int)):
            continue
        lines.append(f"{k} {v}")
    return "\n".join(lines)


def _read_static_profiles(dir: str = "data") -> List[str]:
    profiles: List[str] = []
    for file in os.listdir(dir):
        with open(os.path.join(dir, file), "r") as f:
            profiles.append(f.read())
    return profiles


_STATIC_PROFILES = _read_static_profiles()


def get_static_profile() -> str:
    return random.choice(_STATIC_PROFILES)
