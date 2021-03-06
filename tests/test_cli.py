# -*- coding: utf-8 -*-
# Copyright (c) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE.rst for more info.
import json
import shlex
import sys
import zipfile
from datetime import datetime, timedelta

import docopt
import pytest

from wetterdienst import cli

# Individual settings for observations and forecasts
SETTINGS_STATIONS = [
    "observations stations --resolution=daily --parameter=kl --period=recent",
    "forecasts stations",
]

SETTINGS_READINGS = [
    "observations readings --resolution=daily --parameter=kl --period=recent "
    "--date=2020-06-30",
    f"forecasts readings --mosmix-type=large --parameter=DD "
    f"--date={datetime.strftime(datetime.today() + timedelta(days=2), '%Y-%m-%d')}",
]

SETTINGS_STATION = [
    "04411,07341",  # observation stations
    "10488,67743",  # mosmix forecast stations
]

EXPECTED_STATION_NAMES = [
    ["Schaafheim-Schlierbach", "Offenbach-Wetterpark"],
    ["DRESDEN", "LIVINGSTONE"],
]


def test_cli_help():

    with pytest.raises(docopt.DocoptExit) as excinfo:
        cli.run()

    response = str(excinfo.value)
    assert "wetterdienst dwd observations stations" in response
    assert "wetterdienst dwd observations readings" in response
    assert "wetterdienst dwd forecasts stations" in response
    assert "wetterdienst dwd forecasts readings" in response
    assert "wetterdienst dwd about" in response


def test_cli_about_parameters(capsys):

    sys.argv = ["wetterdienst", "dwd", "about", "parameters"]
    cli.run()
    stdout, stderr = capsys.readouterr()

    response = stdout
    assert "precipitation" in response
    assert "air_temperature" in response
    assert "weather_phenomena" in response
    # assert "radolan" in response
    # assert "wx" in response
    # assert "rx" in response
    # assert "sweep_vol_z" in response


def test_cli_about_resolutions(capsys):

    sys.argv = ["wetterdienst", "dwd", "about", "resolutions"]
    cli.run()
    stdout, stderr = capsys.readouterr()

    response = stdout
    assert "1_minute" in response
    assert "hourly" in response
    assert "annual" in response


def test_cli_about_periods(capsys):

    sys.argv = ["wetterdienst", "dwd", "about", "periods"]
    cli.run()
    stdout, stderr = capsys.readouterr()

    response = stdout
    assert "historical" in response
    assert "recent" in response
    assert "now" in response


def test_cli_about_coverage(capsys):

    sys.argv = ["wetterdienst", "dwd", "about", "coverage"]
    cli.run()
    stdout, stderr = capsys.readouterr()

    response = stdout
    assert "Resolution.ANNUAL" in response
    assert "DWDObservationParameterSet.CLIMATE_SUMMARY" in response
    assert "Period.HISTORICAL" in response


def invoke_wetterdienst_stations_empty(setting, fmt="json"):
    argv = shlex.split(f"wetterdienst dwd {setting} --station=123456 --format={fmt}")
    sys.argv = argv
    cli.run()


def invoke_wetterdienst_stations_static(setting, station, fmt="json"):
    argv = shlex.split(f"wetterdienst dwd {setting} --station={station} --format={fmt}")
    sys.argv = argv
    cli.run()


def invoke_wetterdienst_stations_geo(setting, fmt="json"):
    argv = shlex.split(
        f"wetterdienst dwd {setting} --latitude=49.9195 --longitude=8.9671 --number=5 "
        f"--format={fmt}"
    )
    sys.argv = argv
    cli.run()


def invoke_wetterdienst_readings_static(setting, station, fmt="json"):
    argv = shlex.split(f"wetterdienst dwd {setting} --station={station} --format={fmt}")
    sys.argv = argv
    cli.run()


def invoke_wetterdienst_readings_static_tidy(setting, station, fmt="json"):
    argv = shlex.split(
        f"wetterdienst dwd {setting} --station={station} --format={fmt} --tidy"
    )
    sys.argv = argv
    cli.run()


def invoke_wetterdienst_readings_geo(setting, fmt="json"):
    argv = shlex.split(
        f"wetterdienst dwd {setting} --latitude=49.9195 --longitude=8.9671 --number=5 "
        f"--format={fmt}"
    )
    sys.argv = argv
    cli.run()


@pytest.mark.parametrize(
    "setting,station,expected_station_names",
    zip(SETTINGS_STATIONS, SETTINGS_STATION, EXPECTED_STATION_NAMES),
)
def test_cli_stations_json(setting, station, expected_station_names, capsys):

    invoke_wetterdienst_stations_static(setting=setting, station=station, fmt="json")

    stdout, stderr = capsys.readouterr()
    response = json.loads(stdout)

    station_names = [station["station_name"] for station in response]

    for station_name in expected_station_names:
        assert station_name in station_names


@pytest.mark.parametrize("setting", SETTINGS_STATIONS)
def test_cli_stations_empty(setting, caplog):

    with pytest.raises(SystemExit):
        invoke_wetterdienst_stations_empty(setting=setting, fmt="json")

    assert "ERROR" in caplog.text
    assert "No data available for given constraints" in caplog.text


# TODO: make forecasts formattable as GEOJSON/make to_geojson compatible with WMO_ID
@pytest.mark.parametrize(
    "setting,station,expected_station_names",
    zip(SETTINGS_STATIONS[:1], SETTINGS_STATION[:1], EXPECTED_STATION_NAMES[:1]),
)
def test_cli_stations_geojson(setting, station, expected_station_names, capsys):

    invoke_wetterdienst_stations_static(setting=setting, station=station, fmt="geojson")

    stdout, stderr = capsys.readouterr()
    response = json.loads(stdout)

    assert len(response["features"]) == 2

    station_names = [station["properties"]["name"] for station in response["features"]]

    for station_name in expected_station_names:
        assert station_name in station_names


@pytest.mark.parametrize(
    "setting,station,expected_station_names",
    zip(SETTINGS_STATIONS, SETTINGS_STATION, EXPECTED_STATION_NAMES),
)
def test_cli_stations_csv(setting, station, expected_station_names, capsys):

    invoke_wetterdienst_stations_static(setting=setting, station=station, fmt="csv")

    stdout, stderr = capsys.readouterr()

    for station_name in expected_station_names:
        assert station_name in stdout


@pytest.mark.parametrize(
    "setting,station,expected_station_names",
    zip(SETTINGS_STATIONS, SETTINGS_STATION, EXPECTED_STATION_NAMES),
)
def test_cli_stations_excel(setting, station, expected_station_names, capsys):

    invoke_wetterdienst_stations_static(setting=setting, station=station, fmt="excel")

    # FIXME: Make --format=excel write to a designated file.
    filename = "output.xlsx"
    with zipfile.ZipFile(filename, "r") as zip_file:
        payload = zip_file.read("xl/worksheets/sheet1.xml")

        for station_name in expected_station_names:
            assert bytes(station_name, encoding="utf8") in payload


@pytest.mark.parametrize(
    "setting,station", zip(SETTINGS_READINGS[:1], SETTINGS_STATION[:1])
)
def test_cli_readings_json(setting, station, capsys):

    invoke_wetterdienst_readings_static(setting=setting, station=station, fmt="json")

    stdout, stderr = capsys.readouterr()
    response = json.loads(stdout)

    station_ids = list(set([reading["station_id"] for reading in response]))

    for s in station.split(","):
        assert s in station_ids

    first = response[0]
    assert set(first.keys()).issuperset(
        (
            "station_id",
            "date",
            # "quality_wind",
            "wind_gust_max",
            "wind_speed",
            # "quality_general",
            "precipitation_height",
            "precipitation_form",
            "sunshine_duration",
            "snow_depth",
            "cloud_cover_total",
            "pressure_vapor",
            "pressure_air",
            "temperature_air_200",
            "humidity",
            "temperature_air_max_200",
            "temperature_air_min_200",
            "temperature_air_min_005",
        )
    )


@pytest.mark.parametrize("setting,station", zip(SETTINGS_READINGS, SETTINGS_STATION))
def test_cli_readings_json_tidy(setting, station, capsys):

    invoke_wetterdienst_readings_static_tidy(
        setting=setting, station=station, fmt="json"
    )

    stdout, stderr = capsys.readouterr()
    response = json.loads(stdout)

    station_ids = list(set([reading["station_id"] for reading in response]))

    for s in station.split(","):
        assert s in station_ids

    first = response[0]

    # TODO: align/unify this after setting up a data model
    assert list(first.keys()) == [
        "station_id",
        "date",
        "parameter_set",
        "parameter",
        "value",
        "quality",
    ] or list(first.keys()) == [
        "station_id",
        "date",
        "parameter",
        "value",
    ]


@pytest.mark.parametrize("setting,station", zip(SETTINGS_READINGS, SETTINGS_STATION))
def test_cli_readings_geojson(setting, station):

    with pytest.raises(KeyError) as excinfo:
        invoke_wetterdienst_readings_static(
            setting=setting, station=station, fmt="geojson"
        )

    assert excinfo.typename == "KeyError"
    assert str(excinfo.value) == "'GeoJSON format only available for stations output'"


@pytest.mark.parametrize("setting,station", zip(SETTINGS_READINGS, SETTINGS_STATION))
def test_cli_readings_csv(setting, station, capsys):

    invoke_wetterdienst_readings_static(setting=setting, station=station, fmt="csv")

    stdout, stderr = capsys.readouterr()

    for s in station.split(","):
        assert s in stdout


@pytest.mark.parametrize("setting,station", zip(SETTINGS_READINGS, SETTINGS_STATION))
def test_cli_readings_excel(setting, station):

    invoke_wetterdienst_readings_static(setting=setting, station=station, fmt="excel")

    # FIXME: Make --format=excel write to a designated file.
    filename = "output.xlsx"
    with zipfile.ZipFile(filename, "r") as zip_file:
        payload = zip_file.read("xl/worksheets/sheet1.xml")

        for s in station.split(","):
            assert bytes(s, encoding="utf8") in payload


@pytest.mark.parametrize("setting,station", zip(SETTINGS_READINGS, SETTINGS_STATION))
def test_cli_readings_format_unknown(setting, station, caplog):

    with pytest.raises(SystemExit):
        invoke_wetterdienst_readings_static(
            setting=setting, station=station, fmt="foobar"
        )

    assert "ERROR" in caplog.text
    assert "Unknown output format" in caplog.text


@pytest.mark.parametrize("setting", SETTINGS_STATIONS[:1])
def test_cli_stations_geospatial(setting, capsys):

    invoke_wetterdienst_stations_geo(setting=setting, fmt="json")

    stdout, stderr = capsys.readouterr()
    response = json.loads(stdout)

    station_names = [station["station_name"] for station in response]

    assert "Schaafheim-Schlierbach" in station_names
    assert "Offenbach-Wetterpark" in station_names

    # Please remove if too flakey.
    assert station_names == [
        "Schaafheim-Schlierbach",
        "Kahl/Main",
        "Michelstadt-Vielbrunn",
        "Offenbach-Wetterpark",
        "Michelstadt",
    ]


@pytest.mark.parametrize(
    "setting,station", zip(SETTINGS_READINGS[:1], SETTINGS_STATION[:1])
)
def test_cli_readings_geospatial(setting, station, capsys):

    invoke_wetterdienst_readings_geo(setting=setting, fmt="json")

    stdout, stderr = capsys.readouterr()
    response = json.loads(stdout)

    station_ids = list(set([reading["station_id"] for reading in response]))

    for s in station.split(","):
        assert s in station_ids
        assert s in station_ids
