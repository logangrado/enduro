import pydantic
import datetime


class CarConfig(pydantic.BaseModel):
    max_fuel: float
    refuel_rate: float
    tire_change_time: datetime.timedelta


class TrackConfig(pydantic.BaseModel):
    avg_lap_time: datetime.timedelta
    fuel_per_lap: float
    pit_time_loss: datetime.timedelta


class RaceConfig(pydantic.BaseModel):
    duration: datetime.timedelta
    start_time: datetime.time
    sim_time: datetime.time
    mult: float


class EnduroConfig(pydantic.BaseModel):
    race: RaceConfig
    track: TrackConfig
    car: CarConfig
