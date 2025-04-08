from collections import defaultdict
from typing import Union


class CategoricalEncoder:
    """
    CategoricalEncoder is a class that encodes categorical variables into numerical values.

    Parameters
    ----------
    col_name : str
        The name of the column to be encoded.
    data : list
        The data to be encoded.
    """

    __slots__ = ("col_name", "mappings")

    def __init__(self, col_name: str, data: list):
        self.col_name = col_name
        self.mappings = self.__fit__(data)

    def __fit__(self, data: list) -> dict:
        """
        This function creates a mapping of unique values to integers.
        """
        unique_vals = set(data)
        return {v: k for k, v in enumerate(unique_vals)}

    def transform(self, data: Union[str, list]) -> Union[str, list]:
        """
        This function transforms the data using the mapping created in the fit method.
        It can handle both single values and lists of values.
        """
        if isinstance(data, list):
            return [self.mappings[value] for value in data]
        else:
            return self.mappings[data]

    def inverse_transform(self, transformed_data):
        inverse_mappings = {k: v for v, k in enumerate(self.mappings)}
        return [inverse_mappings[key] for key in transformed_data]


class ZoneMappingNum:
    """
    ZoneMappingNum is a class that creates zones for numerical data.
    It divides the data into zones based on the number of zones specified.

    Parameters
    ----------
    col_name : str
        The name of the column to be zoned.
    num_zones : int
        The number of zones to create.
    """

    __slots__ = ("col_name", "num_zones", "rows_per_zone", "zones")

    def __init__(
        self,
        col_name: str,
        num_zones: int,
    ):
        self.col_name = col_name
        self.num_zones = num_zones
        self.rows_per_zone = None
        self.zones = {}

    def fit(self, data):
        N = len(data)
        self.rows_per_zone = N // self.num_zones
        zones = []
        for i in range(0, N, self.rows_per_zone):
            zone_vals = data[i : min(N, i + self.rows_per_zone)]
            min_val, max_val = min(zone_vals), max(zone_vals)
            zones.append([min_val, max_val])
        self.zones = {k: v for k, v in enumerate(zones)}


class ZoneMappingCat:
    def __rearrange__(self, column_store, col_name: str):
        mapped_col_idxs = {}

        for i, col_val in enumerate(column_store.columns[col_name].data):
            if col_val in mapped_col_idxs:
                mapped_col_idxs[col_val].append(i)
            else:
                mapped_col_idxs[col_val] = [i]

        rerranged_column_store = defaultdict(list)
        columns = [k for k in column_store.columns.keys()]
        for col in columns:
            for unique_col_val in mapped_col_idxs:
                rerranged_column_store[col].extend(
                    [
                        column_store.columns[col].data[idx]
                        for idx in mapped_col_idxs[unique_col_val]
                    ]
                )
        return mapped_col_idxs, rerranged_column_store

    def fit(self, column_store, col_name):
        zone_start_idx = 0
        mapped_col_idxs, rearranged_column_store = self.__rearrange__(
            column_store=column_store, col_name=col_name
        )

        zone_mapping = {}
        for zone_map, row_idxs_list in mapped_col_idxs.items():
            zone_end_idx = zone_start_idx + len(row_idxs_list) - 1

            # min and max value will be off of the floor_area_sqm
            zone_min_val = min(
                rearranged_column_store["floor_area_sqm"][
                    zone_start_idx : zone_end_idx + 1
                ]
            )
            zone_max_val = max(
                rearranged_column_store["floor_area_sqm"][
                    zone_start_idx : zone_end_idx + 1
                ]
            )

            zone_mapping[zone_map] = {
                "start_idx": zone_start_idx,
                "end_idx": zone_end_idx,
                "zone_min": zone_min_val,
                "zone_max": zone_max_val,
            }

            zone_start_idx = zone_end_idx + 1

        return zone_mapping, rearranged_column_store
