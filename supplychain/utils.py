"""
optimization.py defines the optimization problem for the supply chain network
"""
import numpy as np
from .model import Location


def _haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    """
    R = 6372800  # Earth radius in meters
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    return (
        2
        * R
        * np.arcsin(
            np.sqrt(
                np.sin(delta_lat / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
            )
        )
    )


def haversine_distance(location1: Location, location2: Location):
    """
    Calculate the great circle distance between two points
    """
    return _haversine_distance(
        location1.latitude, location1.longitude, location2.latitude, location2.longitude
    )
