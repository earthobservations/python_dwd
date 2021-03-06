# -*- coding: utf-8 -*-
# Copyright (c) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE.rst for more info.
from datetime import datetime

import pandas as pd
import pytest
import pytz
from pandas import Timestamp
from pandas._testing import assert_frame_equal

from wetterdienst.dwd.metadata.column_names import DWDMetaColumns
from wetterdienst.dwd.observations import (
    DWDObservationParameterSet,
    DWDObservationPeriod,
    DWDObservationResolution,
)
from wetterdienst.dwd.observations.api import DWDObservationStations
from wetterdienst.exceptions import InvalidParameterCombination
from wetterdienst.metadata.columns import Columns


@pytest.mark.remote
def test_dwd_observations_stations_success():

    # Existing combination of parameters
    request = DWDObservationStations(
        DWDObservationParameterSet.CLIMATE_SUMMARY,
        DWDObservationResolution.DAILY,
        DWDObservationPeriod.HISTORICAL,
    )

    df = request.all()

    assert not df.empty

    assert_frame_equal(
        df.loc[df[Columns.STATION_ID.value] == "00001", :].reset_index(drop=True),
        pd.DataFrame(
            {
                "STATION_ID": ["00001"],
                "FROM_DATE": [datetime(1937, 1, 1, tzinfo=pytz.UTC)],
                "TO_DATE": [datetime(1986, 6, 30, tzinfo=pytz.UTC)],
                "HEIGHT": [478.0],
                "LATITUDE": [47.8413],
                "LONGITUDE": [8.8493],
                "STATION_NAME": ["Aach"],
                "STATE": ["Baden-Württemberg"],
            }
        ),
    )

    # assert df.loc[
    #     df[Columns.STATION_ID.value] == "00001", :
    # ].values.tolist() == [
    #     [
    #         "00001",
    #         datetime(1937, 1, 1, tzinfo=pytz.UTC),
    #         datetime(1986, 6, 30, tzinfo=pytz.UTC),
    #         478.0,
    #         47.8413,
    #         8.8493,
    #         "Aach",
    #         "Baden-Württemberg",
    #     ]
    # ]


@pytest.mark.remote
def test_dwd_observations_stations_geojson():

    # Existing combination of parameters
    request = DWDObservationStations(
        DWDObservationParameterSet.CLIMATE_SUMMARY,
        DWDObservationResolution.DAILY,
        DWDObservationPeriod.HISTORICAL,
    )

    df = request.all()

    assert not df.empty

    df = df[df[Columns.STATION_ID.value] == "00001"]

    geojson = df.dwd.to_geojson()

    properties = geojson["features"][0]["properties"]
    geometry = geojson["features"][0]["geometry"]

    assert properties["name"] == "Aach"
    assert properties["state"] == "Baden-Württemberg"

    assert geometry == {
        "type": "Point",
        "coordinates": [8.8493, 47.8413, 478.0],
    }
