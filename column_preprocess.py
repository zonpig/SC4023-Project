from collections import defaultdict


class CategoricalEncoder:
    def __init__(self, col_name, data):
        self.col_name = col_name
        self.mappings = self.__fit__(data)

    def __fit__(self, data):
        unique_vals = set(data)
        # e.g. bedok:0
        return {v: k for k, v in enumerate(unique_vals)}

    def transform(self, data):
        if isinstance(data, list):
            return [self.mappings[value] for value in data]
        else:
            return self.mappings[data]

    def inverse_transform(self, transformed_data):
        inverse_mappings = {k: v for v, k in enumerate(self.mappings)}
        return [inverse_mappings[key] for key in transformed_data]


class ZoneMappingNum:
    def __init__(
        self,
        col_name,
        num_zones,
    ):
        """
        Args:
            col_name: str
            num_zones: int, number of zones to divide
        """
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

    """
    Takes in the original dataset and sort the zone maps by each categorical value.
    To provide a common class to zone map and rearrange tables based on a given column name.
    """

    def __rearrange__(self, column_store, col_name):
        # print("Running rearrange function")
        mapped_col_idxs = {}

        # print("Adding idx to mapped_col_idxs")
        for i, col_val in enumerate(column_store.columns[col_name].data):
            if col_val in mapped_col_idxs:
                mapped_col_idxs[col_val].append(i)
            else:
                mapped_col_idxs[col_val] = [i]

        # print("Done adding idx to mapped_col_idxs")
        # print(f"mapped_col_idx keys: {mapped_col_idxs.keys()}")
        # print(mapped_col_idxs)

        # STEP: Create an empty dictionary each for each column
        rerranged_column_store = defaultdict(list)
        columns = [k for k in column_store.columns.keys()]
        # print(f"all columns: {columns}")

        # TODO: we need to store the column store in a dictionary with key being column name and values being the rows
        # STEP: Iterate through the column store and add to each dict
        for col in columns:
            for unique_col_val in mapped_col_idxs:
                rerranged_column_store[col].extend(
                    [
                        column_store.columns[col].data[idx]
                        for idx in mapped_col_idxs[unique_col_val]
                    ]
                )

        # print(type(rerranged_column_store))
        # print(f"Testing 1 column of rearranged col store: {rerranged_column_store["floor_area_sqm"]}")
        # print(f"rerranged_column_store keys: {rerranged_column_store.keys()}")

        # TODO: changing it to an object before returning
        # (NOT DOING THIS FOR NOW)

        # print("Returned rearranged columns (Currently returning as a dictionary)")
        # print()
        return mapped_col_idxs, rerranged_column_store

    def fit(self, column_store, col_name):
        """
        Returns the start and end idx of each zone, and the min and max
        """
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
