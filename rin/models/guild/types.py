from __future__ import annotations

import enum

__all__ = (
    "VerificationLevel",
    "MessageNotificationLevel",
    "ExplicitContentFilterLevel",
    "MFALevel",
    "NSFWLevel",
    "GuildPremiumTier",
)


class VerificationLevel(enum.IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class MessageNotificationLevel(enum.IntEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(enum.IntEnum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(enum.IntEnum):
    NONE = 0
    ELEVATED = 1


class NSFWLevel(enum.IntEnum):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class GuildPremiumTier(enum.IntEnum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3
