import json
import math

import pandas as pd
import numpy as np
import _jsonnet

from enduro.config import EnduroConfig


def _load_config(config_path):
    config_dict = json.loads(_jsonnet.evaluate_file(config_path))
    return EnduroConfig(**config_dict)


def _format_dt_str(dt):
    seconds = dt.total_seconds()
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    time_str = f"{seconds:02.0f}"
    if minutes or hours:
        time_str = f"{minutes:02.0f}:" + time_str
    if hours:
        time_str = f"{hours:0.0f}:" + time_str

    return time_str


def _print_df(df):
    for col in df.columns:
        if pd.api.types.is_timedelta64_dtype(df[col]):
            df[col] = df[col].apply(_format_dt_str)

    print(df)


def _compute_stints(config):
    stint_lap_tolerance = 0.1

    max_stint_laps = int(config.car.max_fuel / config.track.fuel_per_lap - stint_lap_tolerance)
    max_stint_time_s = max_stint_laps * config.track.avg_lap_time_s

    max_pit_refuel_time_s = config.car.max_fuel / config.car.refuel_rate
    max_pit_time_s = max_pit_refuel_time_s + config.track.pit_time_loss_s

    # Compute est. number of stints, without accounting for pit time
    n_stints = math.ceil(config.race.duration * 60 / max_stint_time_s)

    # Compute total fuel requirement for race. Do not account for pit time.
    total_race_time_s = config.race.duration * 60 + config.track.avg_lap_time_s
    total_race_laps = math.ceil(total_race_time_s / config.track.avg_lap_time_s)
    total_fuel_req = total_race_laps * config.track.fuel_per_lap
    total_refuel_req = total_fuel_req - config.car.max_fuel
    total_refuel_time = total_refuel_req / config.car.refuel_rate

    # Compute total ADDED pit in/out time for race
    total_pit_travel_time = (n_stints - 1) * config.track.pit_time_loss_s

    total_pit_time = total_refuel_time + total_pit_travel_time

    # Compute total n race laps w/ pits included
    total_drive_time_s = total_race_time_s - total_pit_time
    total_drive_laps = math.ceil(total_drive_time_s / config.track.avg_lap_time_s)

    # Re-compute n_stints
    n_stints = math.ceil(total_drive_laps / max_stint_laps)

    # Compute stint schedule
    data = []
    laps_remaining = total_drive_laps
    for i in range(n_stints):
        stint_data = {
            "stint": i,
            "n_laps": min(max_stint_laps, laps_remaining),
        }

        if i == 0:
            stint_data["fuel_start"] = config.car.max_fuel
            stint_data["refuel"] = 0
            stint_data["pit"] = False
        else:
            stint_data["pit"] = True
            stint_data["fuel_start"] = data[-1]["fuel_end"]
            stint_data["refuel"] = stint_data["n_laps"] * config.track.fuel_per_lap

        stint_data["fuel_consumed"] = stint_data["n_laps"] * config.track.fuel_per_lap
        stint_data["fuel_end"] = stint_data["fuel_start"] + stint_data["refuel"] - stint_data["fuel_consumed"]

        laps_remaining -= stint_data["n_laps"]
        data.append(stint_data)
    stint_df = pd.DataFrame(data)

    stint_df["drive_time"] = stint_df["n_laps"] * config.track.avg_lap_time_s
    stint_df["pit_service_time"] = stint_df["refuel"] / config.car.refuel_rate
    stint_df["pit_time"] = (stint_df["refuel"] + config.track.pit_time_loss_s) * stint_df["pit"]
    stint_df["stint_time"] = stint_df["drive_time"] + stint_df["pit_time"]

    stint_df["lap_end"] = stint_df["n_laps"].cumsum()
    stint_df["lap_start"] = [0] + stint_df["lap_end"].tolist()[:-1]

    stint_df["t_end"] = stint_df["stint_time"].cumsum()
    stint_df["t_start"] = [0] + stint_df["t_end"].tolist()[:-1]

    time_cols = ["t_start", "t_end", "stint_time", "pit_time"]
    for col in time_cols:
        stint_df[col] = pd.to_timedelta(stint_df[col], unit="seconds")

    stint_df = stint_df[
        [
            "stint",
            "n_laps",
            "t_start",
            "t_end",
            "stint_time",
            "refuel",
            "fuel_consumed",
            "fuel_end",
            "lap_start",
            "lap_end",
            "pit_service_time",
        ]
    ]

    return stint_df


def run(config_path):
    config = _load_config(config_path)

    print(config.json(sort_keys=True, indent=2))
    stint_df = _compute_stints(config)
    _print_df(stint_df)
