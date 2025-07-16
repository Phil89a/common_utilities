from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class MQTTSensorPayload(BaseModel):
    """
    Pydantic model for MQTT sensor payload data.
    Ensures all numeric fields that represent cumulative values or demand
    are handled as Decimal for precision.
    """
    read_at: datetime = Field(..., description="Timestamp of the reading in ISO 8601 format (e.g., '2023-10-27T10:00:00Z')")
    sensor_name: str = Field(..., description="Unique name of the sensor (e.g., 'house_main_meter')")

    # Cumulative values - MUST be Decimal for precision
    import_cumulative: Optional[Decimal] = Field(None, description="Cumulative imported energy (e.g., kWh or m3)")
    export_cumulative: Optional[Decimal] = Field(None, description="Cumulative exported energy (e.g., kWh)")

    # Daily/Weekly/Monthly totals - MUST be Decimal for precision
    import_day: Optional[Decimal] = Field(None, description="Total imported energy for the current day")
    import_week: Optional[Decimal] = Field(None, description="Total imported energy for the current week")
    import_month: Optional[Decimal] = Field(None, description="Total imported energy for the current month")

    # Added export_day, export_week, export_month as per the full model
    export_day: Optional[Decimal] = Field(None, description="Total exported energy for the current day")
    export_week: Optional[Decimal] = Field(None, description="Total exported energy for the current week")
    export_month: Optional[Decimal] = Field(None, description="Total exported energy for the current month")

    # Demand/Power values - power_value is Decimal, power_units is STR
    power_value: Optional[Decimal] = Field(None, description="Instantaneous power/demand value")
    power_units: Optional[str] = Field(None, description="Units for power_value (e.g., 'kW', 'W', 'm3/h')")

    # Optional additional fields for future use
    voltage: Optional[Decimal] = Field(None, description="Voltage reading")
    current: Optional[Decimal] = Field(None, description="Current reading")
    frequency: Optional[Decimal] = Field(None, description="Frequency reading")
    power_factor: Optional[Decimal] = Field(None, description="Power factor reading")


    @classmethod
    def from_raw_data(cls, raw: dict) -> "MQTTSensorPayload":
        # Identify if it's a gas or electricity payload
        sensor_name = next((k for k in ('electricitymeter', 'gasmeter') if k in raw), None)
        if sensor_name is None:
            raise ValueError("Missing 'electricitymeter' or 'gasmeter' key in input data")

        meter_data = raw[sensor_name]
        energy = meter_data.get("energy", {})
        power = meter_data.get("power", {})

        # Extract import energy data
        import_energy_data = energy.get("import", {})
        export_energy_data = energy.get("export", {}) # Added for export day/week/month

        return cls(
            read_at=meter_data.get("timestamp"),
            sensor_name=sensor_name,
            import_cumulative=import_energy_data.get("cumulative"),
            import_day=import_energy_data.get("day"),
            import_week=import_energy_data.get("week"),
            import_month=import_energy_data.get("month"),
            export_cumulative=export_energy_data.get("cumulative"),
            # Added mapping for export_day, export_week, export_month
            export_day=export_energy_data.get("day"),
            export_week=export_energy_data.get("week"),
            export_month=export_energy_data.get("month"),
            power_value=power.get("value"),
            power_units=power.get("units", "kW"), # Default to 'kW' if not provided

            # Mapping for optional additional fields
            voltage=meter_data.get("voltage"),
            current=meter_data.get("current"),
            frequency=meter_data.get("frequency"),
            power_factor=meter_data.get("power_factor"),
        )

    @classmethod
    def model_validate_raw_data(cls, raw: dict) -> "MQTTSensorPayload":
        """Wrapper to mimic .model_validate but for nested raw data"""
        return cls.from_raw_data(raw)

    class Config:
        # Enable ORM mode for Pydantic v1, or from_attributes=True for Pydantic v2
        orm_mode = True

        # Custom JSON encoder for Decimal objects to ensure they are serialized correctly
        json_encoders = {
            Decimal: lambda v: str(v)
        }