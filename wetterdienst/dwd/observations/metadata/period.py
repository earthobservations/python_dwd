# -*- coding: utf-8 -*-
# Copyright (c) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE.rst for more info.
from enum import Enum

from wetterdienst.metadata.period import Period


class DWDObservationPeriod(Enum):
    HISTORICAL = Period.HISTORICAL.value
    RECENT = Period.RECENT.value
    NOW = Period.NOW.value
