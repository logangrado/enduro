import pydantic


class CarConfig(pydantic.BaseModel):
    max_fuel: float
    refuel_rate: float
    tire_change_time: float


class TrackConfig(pydantic.BaseModel):
    avg_lap_time_s: float
    fuel_per_lap: float
    pit_time_loss_s: float


class RaceConfig(pydantic.BaseModel):
    duration: float


class EnduroConfig(pydantic.BaseModel):
    race: RaceConfig
    track: TrackConfig
    car: CarConfig