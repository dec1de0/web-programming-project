"""Domain errors independent of the HTTP layer."""


class DomainError(Exception):
    def __init__(self, message: str, *, code: str = "business_rule_violation"):
        super().__init__(message)
        self.message = message
        self.code = code


class ResourceNotFound(DomainError):
    pass


class ResourceConflict(DomainError):
    pass
