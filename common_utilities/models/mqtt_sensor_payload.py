from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MQTTSensorPayload(BaseModel):
    read_at: datetime  # Pydantic will parse ISO strings automatically
    sensor_name: str
    import_cumulative: Optional[float] = None
    import_day: Optional[float] = None
    import_week: Optional[float] = None
    import_month: Optional[float] = None
    export_cumulative: Optional[float] = None
    power_value: Optional[float] = None
    power_units: Optional[str] = None

    @classmethod
    def from_raw_data(cls, raw: dict) -> "MQTTSensorPayload":
        sensor_name = next((k for k in ('electricitymeter', 'gasmeter') if k in raw), None)
        meter_data = raw.get(sensor_name, raw)
        energy = meter_data.get('energy', {})
        power = meter_data.get('power', {})

        return cls(
            read_at=meter_data.get('timestamp'),
            sensor_name=sensor_name or "unknown",
            import_cumulative=energy.get('import', {}).get('cumulative'),
            import_day=energy.get('import', {}).get('day'),
            import_week=energy.get('import', {}).get('week'),
            import_month=energy.get('import', {}).get('month'),
            export_cumulative=energy.get('export', {}).get('cumulative'),
            power_value=power.get('value'),
            power_units=power.get('units', 'kW'),
        )