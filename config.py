from dataclasses import dataclass


@dataclass
class Config:
    source: str
    target: str
    hashing_algorithm: str
    hashing_mode: str
    delete: bool
    quiet: bool
    failure_threshold: int

    def __post_init__(self) -> None:
        for field_name, expected_type in [
            ("source", str), ("target", str),
            ("hashing_algorithm", str), ("hashing_mode", str),
            ("delete", bool), ("quiet", bool), ("failure_threshold", int)
        ]:
            value = getattr(self, field_name)  # pyright: ignore[reportAny]
            if not isinstance(value, expected_type):
                raise TypeError(f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}")  # pyright: ignore[reportAny]

        if not 0 <= self.failure_threshold <= 100:
            raise ValueError("failure_threshold must be between 0 and 100")