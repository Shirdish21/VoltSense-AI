from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    electricity_tariff: float = 8.25  # INR / kWh
    carbon_factor: float = 0.708  # kg CO2e / kWh
    database_url: str = "sqlite:///./voltsense.db"


settings = Settings()
