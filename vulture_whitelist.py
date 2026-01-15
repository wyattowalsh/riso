# Vulture whitelist file - known false positives
# These are flagged as unused but are actually required by their frameworks

# Pydantic @classmethod validators require cls parameter even if not directly used
# The parameter is used internally by the decorator framework
cls  # @classmethod parameter in Pydantic validators
