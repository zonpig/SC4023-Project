import csv
import time

from column_preprocess import ZoneMappingNum
from column_store import ResalePriceData
from query import Query


class ResalePriceDataZoneMapNum(ResalePriceData):
    def __init__(self):
        super().__init__()
        self.floor_area_sqm_zone_map = None

    def create_zone_map(self, num_zones):
        self.floor_area_sqm_zone_map = ZoneMappingNum("floor_area_sqm", num_zones)
        self.floor_area_sqm_zone_map.fit(self.columns["floor_area_sqm"].data)

    def area_query(self, rows_scanned, col_idx):
        area_position_zones = []
        for i, j in self.floor_area_sqm_zone_map.zones.items():
            if j[1] >= 80:
                area_position_zones.append(i)

        area_position_match = []
        for i in area_position_zones:
            start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
            end_index = min(
                (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
                len(self.columns["floor_area_sqm"].data),
            )
            for j in range(start_index, end_index):
                if self.columns["floor_area_sqm"].data[j] >= 80:
                    area_position_match.append(j)

        return area_position_match, rows_scanned

    # Minimum Price
    def min_price(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.min_price_query,
            log_query=log_query,
        )

    # Standard Deviation of Price
    def sd_price(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.sd_price_query,
            log_query=log_query,
        )

    def avg_price(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.avg_price_query,
            log_query=log_query,
        )

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.min_price_per_sqm_query,
            log_query=log_query,
        )

    # shared scan to obtain all 4 metrics
    def shared_scan(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.shared_scan_query,
            log_query=log_query,
        )


def column_store_zone_map_num():
    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataZoneMapNum()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    # Creating zone map on flat_type column
    resale_data.create_zone_map(16)
    return resale_data


if __name__ == "__main__":
    Query.column_store_query(column_store_zone_map_num())
