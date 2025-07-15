from decimal import Decimal

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MQTTSensorPayload(BaseModel):
    read_at: datetime  # Parsed automatically from ISO strings
    sensor_name: str
    import_cumulative: Optional[Decimal] = None
    import_day: Optional[Decimal] = None
    import_week: Optional[Decimal] = None
    import_month: Optional[Decimal] = None
    export_cumulative: Optional[Decimal] = None
    power_value: Optional[Decimal] = None
    power_units: Optional[Decimal] = None

    @classmethod
    def from_raw_data(cls, raw: dict) -> "MQTTSensorPayload":
        # Identify if it's a gas or electricity payload
        sensor_name = next((k for k in ('electricitymeter', 'gasmeter') if k in raw), None)
        if sensor_name is None:
            raise ValueError("Missing 'electricitymeter' or 'gasmeter' key in input data")

        meter_data = raw[sensor_name]
        energy = meter_data.get("energy", {})
        power = meter_data.get("power", {})

        return cls(
            read_at=meter_data.get("timestamp"),
            sensor_name=sensor_name,
            import_cumulative=energy.get("import", {}).get("cumulative"),
            import_day=energy.get("import", {}).get("day"),
            import_week=energy.get("import", {}).get("week"),
            import_month=energy.get("import", {}).get("month"),
            export_cumulative=energy.get("export", {}).get("cumulative"),
            power_value=power.get("value"),
            power_units=power.get("units", "kW"),
        )

    @classmethod
    def model_validate_raw_data(cls, raw: dict) -> "MQTTSensorPayload":
        """Wrapper to mimic .model_validate but for nested raw data"""
        return cls.from_raw_data(raw)