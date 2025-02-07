class Severity:
    SEVERITY_UNKOWN = "Unkown"
    SEVERITY_NONE = "None"
    SEVERITY_LOW = "Low"
    SEVERITY_HIGH = "High"
    SEVERITY_MEDIUM = "Medium"
    SEVERITY_CRITICAL = "Critical"

    SEVERITY_CHOICES = [
        (SEVERITY_UNKOWN, SEVERITY_UNKOWN),
        (SEVERITY_NONE, SEVERITY_NONE),
        (SEVERITY_LOW, SEVERITY_LOW),
        (SEVERITY_MEDIUM, SEVERITY_MEDIUM),
        (SEVERITY_HIGH, SEVERITY_HIGH),
        (SEVERITY_CRITICAL, SEVERITY_CRITICAL),
    ]

    NUMERICAL_SEVERITIES = {
        SEVERITY_UNKOWN: 6,
        SEVERITY_NONE: 5,
        SEVERITY_LOW: 4,
        SEVERITY_MEDIUM: 3,
        SEVERITY_HIGH: 2,
        SEVERITY_CRITICAL: 1,
    }


class Status:
    STATUS_OPEN = "Open"
    STATUS_RESOLVED = "Resolved"
    STATUS_DUPLICATE = "Duplicate"
    STATUS_FALSE_POSITIVE = "False positive"
    STATUS_IN_REVIEW = "In review"
    STATUS_NOT_AFFECTED = "Not affected"
    STATUS_NOT_SECURITY = "Not security"
    STATUS_RISK_ACCEPTED = "Risk accepted"

    STATUS_CHOICES = [
        (STATUS_OPEN, STATUS_OPEN),
        (STATUS_RESOLVED, STATUS_RESOLVED),
        (STATUS_DUPLICATE, STATUS_DUPLICATE),
        (STATUS_FALSE_POSITIVE, STATUS_FALSE_POSITIVE),
        (STATUS_IN_REVIEW, STATUS_IN_REVIEW),
        (STATUS_NOT_AFFECTED, STATUS_NOT_AFFECTED),
        (STATUS_NOT_SECURITY, STATUS_NOT_SECURITY),
        (STATUS_RISK_ACCEPTED, STATUS_RISK_ACCEPTED),
    ]
