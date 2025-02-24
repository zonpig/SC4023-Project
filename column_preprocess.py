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


class ZoneMapping:
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
