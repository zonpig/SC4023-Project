class CategoricalEncoder:
    def __init__(self, col_name):
        self.col_name = col_name
    
    def fit(self,data):
        unique_vals = set(data)
        # e.g. bedok:0
        self.mappings = {v:k for k,v in enumerate(unique_vals)}
    
    def transform(self,data):
        return [self.mappings[value] for value in data]
    
    def fit_transform(self,data):
        '''
        Args: 
            data: list, original column store
            transformed_data: list, encoded column store
            mappings: list, mapping of encoded column store
        '''
        self.fit(data)
        return self.transform(data)
    
    def inverse_transform(self, transformed_data):
        inverse_mappings = {k:v for v,k in enumerate(self.mappings)}
        return [inverse_mappings[key] for key in transformed_data]

class ZoneMapping:

    def __init__(self,
                 col_name,
                 num_zones,
                 ):
        
        '''
        Args:
            col_name: str
            num_zones: int, number of zones to divide
            bin_method: str, to be either width or depth
        
        '''
        self.col_name = col_name
        self.num_zones = num_zones
        
    def fit(self,data):
        
        N = len(data)
        rows_per_zone = N // self.num_zones
        zones = []
        for i in range(0,N,rows_per_zone):
            zone_vals = data[i:min(N, i+rows_per_zone)]
            min_val, max_val = min(zone_vals), max(zone_vals)
            zones.append([min_val,max_val])
        self.zones = {k:v for k,v in enumerate(zones)}