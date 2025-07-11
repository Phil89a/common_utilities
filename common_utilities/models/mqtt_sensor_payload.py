from dataclasses import dataclass
from typing import Optional

@dataclass
class MQTTSensorPayload:
    read_at: str  # ISO timestamp
    sensor_name: str
    # Import
    import_cumulative: Optional[float] = None
    import_day: Optional[float] = None
    import_week: Optional[float] = None
    import_month: Optional[float] = None

    # Export
    export_cumulative: Optional[float] = None

    # Power
    power_value: Optional[float] = None
    power_units: Optional[str] = None

    @classmethod
    def from_raw_data(cls, raw: dict) -> "MQTTSensorPayload":
        """
        Parse raw MQTT message dictionary into MQTTPayload dataclass.
        Supports keys 'electricitymeter' and 'gasmeter'.
        """
        sensor_name = next((k for k in ('electricitymeter', 'gasmeter') if k in raw), None)
        meter_data = raw[sensor_name] if sensor_name else raw
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