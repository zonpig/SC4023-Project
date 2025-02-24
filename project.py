import csv


class Month:
    def __init__(self):
        self.months: list[dict[str, int]] = []

    def add_month(self, month: str):
        year, month = map(int, month.split("-"))
        self.months.append({"year": year, "month": month})


class Town:
    def __init__(self):
        self.towns: list[str] = []

    def add_town(self, name: str):
        self.towns.append(name)


class FlatType:
    def __init__(self):
        self.types: list[str] = []

    def add_type(self, type: str):
        self.types.append(type)


class Block:
    def __init__(self):
        self.blocks: list[str] = []

    def add_block(self, block: str):
        self.blocks.append(block)


class StreetName:
    def __init__(self):
        self.streets: list[str] = []

    def add_street(self, street: str):
        self.streets.append(street)


class StoreyRange:
    def __init__(self):
        self.ranges: list[str] = []

    def add_range(self, range: str):
        self.ranges.append(range)


class FloorAreaSqm:
    def __init__(self):
        self.areas: list[float] = []

    def add_area(self, area: float):
        self.areas.append(area)


class FlatModel:
    def __init__(self):
        self.models: list[str] = []

    def add_model(self, model: str):
        self.models.append(model)


class LeaseCommenceDate:
    def __init__(self):
        self.dates: list[int] = []

    def add_date(self, date: int):
        self.dates.append(date)


class ResalePrice:
    def __init__(self):
        self.prices: list[float] = []

    def add_price(self, price: float):
        self.prices.append(price)


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


class ResalePriceData:
    def __init__(self):
        self.month = Month()
        self.town = Town()
        self.flat_type = FlatType()
        self.block = Block()
        self.street_name = StreetName()
        self.storey_range = StoreyRange()
        self.floor_area_sqm = FloorAreaSqm()
        self.flat_model = FlatModel()
        self.lease_commence_date = LeaseCommenceDate()
        self.resale_price = ResalePrice()

    def add_data(
        self,
        month,
        town,
        flat_type,
        block,
        street_name,
        storey_range,
        floor_area_sqm,
        flat_model,
        lease_commence_date,
        resale_price,
    ):
        self.month.add_month(month)
        self.town.add_town(town)
        self.flat_type.add_type(flat_type)
        self.block.add_block(block)
        self.street_name.add_street(street_name)
        self.storey_range.add_range(storey_range)
        self.floor_area_sqm.add_area(floor_area_sqm)
        self.flat_model.add_model(flat_model)
        self.lease_commence_date.add_date(lease_commence_date)
        self.resale_price.add_price(resale_price)

    def __str__(self):
        return (
            f"Months: {self.month.months}\n"
            f"Towns: {self.town.towns}\n"
            f"Flat Types: {self.flat_type.types}\n"
            f"Blocks: {self.block.blocks}\n"
            f"Street Names: {self.street_name.streets}\n"
            f"Storey Ranges: {self.storey_range.ranges}\n"
            f"Floor Areas (sqm): {self.floor_area_sqm.areas}\n"
            f"Flat Models: {self.flat_model.models}\n"
            f"Lease Commence Dates: {self.lease_commence_date.dates}\n"
            f"Resale Prices: {self.resale_price.prices}\n"
        )

    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

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
    def sd_price(self, year, month, town):
        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

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
        prices = [self.resale_price.prices[i] for i in town_position_match]
        if not prices:
            return "No result"
        mean_price = sum(prices) / len(prices)
        variance = sum((price - mean_price) ** 2 for price in prices) / len(prices)
        return round(variance**0.5, 2)

    # Average Price
    def avg_price(self, year, month, town):
        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

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
        prices = [self.resale_price.prices[i] for i in town_position_match]
        if not prices:
            return "No Results"
        mean_price = sum(prices) / len(prices)
        return round(mean_price, 2)

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town):
        min_price_per_sqm = float("inf")

        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

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
            price_per_sqm = self.resale_price.prices[i] / self.floor_area_sqm.areas[i]
            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        return (
            round(min_price_per_sqm, 2)
            if min_price_per_sqm != float("inf")
            else "No result"
        )


def read_csv(file_path):
    resale_data = ResalePriceData()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(
                month=row[0],
                town=row[1],
                flat_type=row[2],
                block=row[3],
                street_name=row[4],
                storey_range=row[5],
                floor_area_sqm=float(row[6]),
                flat_model=row[7],
                lease_commence_date=int(row[8]),
                resale_price=float(row[9]),
            )
    return header, resale_data


# You are expected to write a program to manage the data in a column-oriented manner,
# including data storage and processing. Your program should first receive queries, scan
# the data columns to find matched lines, and compute the results according to associated
# query content. To be specific, a query is composed of a target time (YYYY-MM to YYYY-
# (MM+1)), a matched town, and a query content. These factors are determined by your
# matriculation number as follows:
# a) The last digit of the year of the target time (YYYY) equals the last digit of the matriculation number;
# b) the commencing month (MM) equals the second last digit of the matriculation number (note that “0" represents October);
# c) the matched town depends on the third last digit of the matriculation number as Table 1 presents;
# d) there are four query contents in total that are listed in Table 2, and the area requirement (≥80m2) is applicable to all these contents.
# the area requirement (≥80m2) is applicable to all these contents


def main():
    file_path = "ResalePricesSingapore.csv"
    header, data = read_csv(file_path)

    # print("Header:", header)
    # print("Data:", data)

    # matric number
    matric_number = "U2121223J"

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    print(data.min_price(year, month, town))
    print(data.sd_price(year, month, town))
    print(data.avg_price(year, month, town))
    print(data.min_price_per_sqm(year, month, town))

    categories = [
        ("Minimum Price", data.min_price),
        ("Standard Deviation of Price", data.sd_price),
        ("Average Price", data.avg_price),
        ("Minimum Price per Square Meter", data.min_price_per_sqm),
    ]

    results = [
        {
            "Year": year,
            "Month": month,
            "Town": town,
            "Category": category,
            "Value": func(year, month, town),
        }
        for category, func in categories
    ]

    with open(f"ScanResult_{matric_number}.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["Year", "Month", "Town", "Category", "Value"]
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    main()
