from dataclasses import dataclass

@dataclass
class Config:
    source: str
    target: str
    hashing_algo: str
    hashing_mode: str
    delete: bool
    quiet: bool