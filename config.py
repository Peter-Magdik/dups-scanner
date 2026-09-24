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

    def __post_init__(self):
        if not 0 <= self.failure_threshold <= 100:
            raise ValueError("failure_threshold must be between 0 and 100")