class CategoricalEncoder:
    def __init__(self, col_name):
        self.col_name = col_name
    
    def fit(self,data):
        unique_vals = set(data)
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
    
class ZoneMapping:

    def __init__(self,
                 col_name,
                 num_zones,
                 bin_method='width'
                 ):
        
        '''
        Args:
            col_name: str
            num_zones: int, number of zones to divide
            bin_method: str, to be either width or depth
        
        '''
        assert bin_method in ["width", "depth"], "bin_method must be either width or depth."
        self.col_name = col_name
        self.num_zones = num_zones
        self.bin_method = bin_method
        
    def fit(self,data):
        
        if self.bin_method == "width":
            min_val, max_val = min(data), max(data)
            bin_width = (max_val - min_val)/self.num_zones
            
            zones = []
            cur_min = min_val
            for _ in range(self.num_zones): 
                zone_min = cur_min
                zone_max = cur_min + bin_width

                zones.append([zone_min, zone_max]) 
                cur_min = max(cur_min, cur_min+bin_width)

        elif self.bin_method == "depth":
            bin_size = len(data) // self.num_zones
            data = sorted(data) # need to sort the data first
            zones = [data[i * bin_size:(i + 1) * bin_size] for i in range(self.num_zones)]

        self.zones = {v:k for k,v in enumerate(zones)}

    def transform(self,data):

        processed_data = []
        for val in data:
            for i, partition in enumerate(self.zones):
                if val in partition:  # Check if value belongs to this partition
                    processed_data.append(i)
        return processed_data
       
    def fit_transform(self,data):
        '''
        Args: 
            data: list, original column store
            transformed_data: list, encoded column store
            mappings: list, mapping of encoded column store
        '''
        self.fit(data)
        return self.transform(data)