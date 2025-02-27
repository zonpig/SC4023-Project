import csv
import time

from columns import (
    Month,
    Town,
    FlatType,
    Block,
    StreetName,
    StoreyRange,
    FloorAreaSqm,
    FlatModel,
    LeaseCommenceDate,
    ResalePrice,
)

from column_preprocess import ZoneMapping

class ResalePriceDataZoneMap:
    def __init__(self):
        self.columns = {
            "month": Month(),  # Querying
            "town": Town(),  # Querying
            "flat_type": FlatType(),
            "block": Block(),
            "street_name": StreetName(),
            "storey_range": StoreyRange(),
            "floor_area_sqm": FloorAreaSqm(),  # Querying
            "flat_model": FlatModel(),
            "lease_commence_date": LeaseCommenceDate(),
            "resale_price": ResalePrice()  # Querying
        }

    def add_data(self,row):
        for i,col in enumerate(self.columns.keys()):
            self.columns[col].add_data(row[i])

    def __str__(self):
        return (
            f"Months: {self.columns['month'].data}\n"
            f"Towns: {self.columns['town'].data}\n"
            f"Flat Types: {self.columns['flat_type'].data}\n"
            f"Blocks: {self.columns['block'].data}\n"
            f"Street Names: {self.columns['street_name'].data}\n"
            f"Storey Ranges: {self.columns['storey_range'].data}\n"
            f"Floor Areas (sqm): {self.columns['floor_area_sqm'].data}\n"
            f"Flat Models: {self.columns['flat_model'].data}\n"
            f"Lease Commence Dates: {self.columns['lease_commence_date'].data}\n"
            f"Resale Prices: {self.columns['resale_price'].data}\n"
        )
    def create_zone_map(self,col_name):
        self.zone_mapping, self.rearranged_column_store = ZoneMapping().fit(self.columns, col_name)

    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # start with area
        area_position_match =  []
        # iterate through area position zones
        for k,v in self.zone_mapping.items():
            zone_max_val = v['zone_max']
            zone_start_idx = v['start_idx']
            zone_end_idx = v['end_idx']

            if not zone_max_val < 80:
                area_position_match.extend([idx for idx in range(zone_start_idx, zone_end_idx+1)])

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.month.months[i]["month"] == month
                or self.month.months[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.month.months[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.town.towns[i] == town:
                town_position_match.append(i)

        # price
        for i in town_position_match:
            if self.resale_price.prices[i] < min_price:
                min_price = self.resale_price.prices[i]

        return min_price if min_price != float("inf") else "No result"

    # Standard Deviation of Price
    # def sd_price(self, year, month, town):
    #     # start with area
    #     area_position_zones = []
    #     for i, j in self.floor_area_sqm_zone_map.zones.items():
    #         if j[1] >= 80:
    #             area_position_zones.append(i)

    #     area_position_match = []
    #     for i in area_position_zones:
    #         start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
    #         end_index = min(
    #             (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
    #             len(self.floor_area_sqm.areas),
    #         )
    #         for j in range(start_index, end_index):
    #             if self.floor_area_sqm.areas[j] >= 80:
    #                 area_position_match.append(j)

    #     # month
    #     month_position_match = []
    #     for i in area_position_match:
    #         if (
    #             self.month.months[i]["month"] == month
    #             or self.month.months[i]["month"] == month + 1
    #         ):
    #             month_position_match.append(i)

    #     # year
    #     year_position_match = []
    #     for i in month_position_match:
    #         if self.month.months[i]["year"] == year:
    #             year_position_match.append(i)

    #     # town
    #     town_position_match = []
    #     for i in year_position_match:
    #         if self.town.towns[i] == town:
    #             town_position_match.append(i)

        # price
        # prices = [self.resale_price.prices[i] for i in town_position_match]
        # if not prices:
        #     return "No result"
        # mean_price = sum(prices) / len(prices)
        # variance = sum((price - mean_price) ** 2 for price in prices) / (
        #     len(prices) - 1
        # )        return round(variance**0.5, 2)

    # # Average Price
    # def avg_price(self, year, month, town):
    #     # start with area
    #     area_position_zones = []
    #     for i, j in self.floor_area_sqm_zone_map.zones.items():
    #         if j[1] >= 80:
    #             area_position_zones.append(i)

    #     area_position_match = []
    #     for i in area_position_zones:
    #         start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
    #         end_index = min(
    #             (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
    #             len(self.floor_area_sqm.areas),
    #         )
    #         for j in range(start_index, end_index):
    #             if self.floor_area_sqm.areas[j] >= 80:
    #                 area_position_match.append(j)

    #     # month
    #     month_position_match = []
    #     for i in area_position_match:
    #         if (
    #             self.month.months[i]["month"] == month
    #             or self.month.months[i]["month"] == month + 1
    #         ):
    #             month_position_match.append(i)

    #     # year
    #     year_position_match = []
    #     for i in month_position_match:
    #         if self.month.months[i]["year"] == year:
    #             year_position_match.append(i)

    #     # town
    #     town_position_match = []
    #     for i in year_position_match:
    #         if self.town.towns[i] == town:
    #             town_position_match.append(i)

    #     # price
    #     prices = [self.resale_price.prices[i] for i in town_position_match]
    #     if not prices:
    #         return "No Results"
    #     mean_price = sum(prices) / len(prices)
    #     return round(mean_price, 2)

    # # Minimum Price per Square Meter
    # def min_price_per_sqm(self, year, month, town):
    #     min_price_per_sqm = float("inf")

    #     # start with area
    #     area_position_zones = []
    #     for i, j in self.floor_area_sqm_zone_map.zones.items():
    #         if j[1] >= 80:
    #             area_position_zones.append(i)

    #     area_position_match = []
    #     for i in area_position_zones:
    #         start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
    #         end_index = min(
    #             (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
    #             len(self.floor_area_sqm.areas),
    #         )
    #         for j in range(start_index, end_index):
    #             if self.floor_area_sqm.areas[j] >= 80:
    #                 area_position_match.append(j)

    #     # month
    #     month_position_match = []
    #     for i in area_position_match:
    #         if (
    #             self.month.months[i]["month"] == month
    #             or self.month.months[i]["month"] == month + 1
    #         ):
    #             month_position_match.append(i)

    #     # year
    #     year_position_match = []
    #     for i in month_position_match:
    #         if self.month.months[i]["year"] == year:
    #             year_position_match.append(i)

    #     # town
    #     town_position_match = []
    #     for i in year_position_match:
    #         if self.town.towns[i] == town:
    #             town_position_match.append(i)

    #     # price
    #     for i in town_position_match:
    #         price_per_sqm = self.resale_price.prices[i] / self.floor_area_sqm.areas[i]
    #         if price_per_sqm < min_price_per_sqm:
    #             min_price_per_sqm = price_per_sqm

    #     return (
    #         round(min_price_per_sqm, 2)
    #         if min_price_per_sqm != float("inf")
    #         else "No result"
    #     )


def main():
    town_map = {
    0: "BEDOK",
    1: "BUKIT PANJANG",
    2: "CLEMENTI",
    3: "CHOA CHU KANG",
    4: "HOUGANG",
    5: "JURONG WEST",
    6: "PASIR RIS",
    7: "TAMPINES",
    8: "WOODLANDS",
    9: "YISHUN",
    }

    year_map = {
        0: 2020,
        1: 2021,
        2: 2022,
        3: 2023,
        4: 2014,
        5: 2015,
        6: 2016,
        7: 2017,
        8: 2018,
        9: 2019,
    }

    # matric number
    matric_number = "U2121223J"

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataZoneMap()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    resale_data.create_zone_map("flat_type")

    start_time = time.time()
    min_price = resale_data.min_price(year,month,town)
    end_time = time.time()

    print("min price: ", min_price)
    print("time_elapsed: ", end_time - start_time)

if __name__ == "__main__":
    main()