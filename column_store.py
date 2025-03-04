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


class ResalePriceData:
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

    # Jinyang's
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

    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)

        # price
        for i in town_position_match:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

        return min_price if min_price != float("inf") else "No result"

    # Standard Deviation of Price
    def sd_price(self, year, month, town):
        
        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)

        # price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]
        if not prices:
            return "No result"
        mean_price = sum(prices) / len(prices)
        variance = sum((price - mean_price) ** 2 for price in prices) / (
            len(prices) - 1
        )
        return round(variance**0.5, 2)

    # Average Price
    def avg_price(self, year, month, town):
        
        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)

        # price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]
        if not prices:
            return "No result"
        mean_price = sum(prices) / len(prices)
        return round(mean_price, 2)

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town):
        min_price_per_sqm = float("inf")

        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)

        # price
        for i in town_position_match:
            price_per_sqm = self.columns["resale_price"].data[i] / self.columns["floor_area_sqm"].data[i]
            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        return (
            round(min_price_per_sqm, 2)
            if min_price_per_sqm != float("inf")
            else "No result"
        )




# def main():
#     town_map = {
#     0: "BEDOK",
#     1: "BUKIT PANJANG",
#     2: "CLEMENTI",
#     3: "CHOA CHU KANG",
#     4: "HOUGANG",
#     5: "JURONG WEST",
#     6: "PASIR RIS",
#     7: "TAMPINES",
#     8: "WOODLANDS",
#     9: "YISHUN",
#     }

#     year_map = {
#         0: 2020,
#         1: 2021,
#         2: 2022,
#         3: 2023,
#         4: 2014,
#         5: 2015,
#         6: 2016,
#         7: 2017,
#         8: 2018,
#         9: 2019,
#     }

#     # matric number
#     matric_number = "U2121223J" #Darren
#     # matric_number = "U2121763H" #Bryan
#     # matric_number = "U2122055E" #Jin Yang

#     last_digit_year = int(matric_number[-2])
#     year = year_map[last_digit_year]
#     month = int(matric_number[-3])
#     town_index = int(matric_number[-4])
#     town = town_map[town_index]

#     file_path = "ResalePricesSingapore.csv"
#     resale_data = ResalePriceData()
#     with open(file_path, mode="r") as file:
#         csv_reader = csv.reader(file)
#         _ = next(csv_reader)
#         for row in csv_reader:
#             resale_data.add_data(row)

    

#     start_time = time.time()
#     min_price = resale_data.min_price(year,month,town)
#     end_time = time.time()
#     print("Minimum price: ", min_price)
#     print(f"Time taken for min_price: {end_time - start_time} seconds")
    
    
#     start_time = time.time()
#     sd_price = resale_data.sd_price(year, month, town)
#     end_time = time.time()
#     print("StdDev price: ", sd_price)
#     print(f"Time taken for sd_price: {end_time - start_time} seconds")
    
    
#     start_time = time.time()
#     avg_price = resale_data.avg_price(year,month,town)
#     end_time = time.time()
#     print("Average price: ", avg_price)
#     print(f"Time taken for avg_price: {end_time - start_time} seconds")
    
#     start_time = time.time()
#     min_price_per_sqm = resale_data.min_price_per_sqm(year,month,town)
#     end_time = time.time()
#     print("Minimum price per sqm: ", min_price_per_sqm)
#     print(f"Time taken for min_price_per_sqm: {end_time - start_time} seconds")
    
    
    
    

# if __name__ == "__main__":
#     main()