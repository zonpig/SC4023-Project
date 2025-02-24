import csv
import time
from column_preprocess import CategoricalEncoder, ZoneMapping
from column_store import ResalePriceData
from column_store_encoded import ResalePriceDataEncoded

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


def read_csv(file_path: str, type: int):
    if type == 0:
        resale_data = ResalePriceData()
    elif type == 1:
        resale_data = ResalePriceDataEncoded()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
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
    return resale_data


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
    # matric number
    matric_number = "U2121223J"

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"
    column_store = read_csv(file_path, 0)
    column_store_encoded = read_csv(file_path, 1)

    # Scenario 1: Original
    print("Scenario 1: Original")
    start_time = time.time()

    column_store.min_price(year, month, town)
    column_store.sd_price(year, month, town)
    column_store.avg_price(year, month, town)
    column_store.min_price_per_sqm(year, month, town)

    end_time = time.time()
    print(f"Time taken to run the code: {end_time - start_time} seconds")

    # Scenario 2:
    column_store_encoded.encode_town()
    print("Scenario 2:")

    start_time = time.time()

    column_store_encoded.min_price(year, month, town)
    column_store_encoded.sd_price(year, month, town)
    column_store_encoded.avg_price(year, month, town)
    column_store_encoded.min_price_per_sqm(year, month, town)

    end_time = time.time()
    print(f"Time taken to run the code: {end_time - start_time} seconds")

    # Output Code
    # categories = [
    #     ("Minimum Price", column_store.min_price),
    #     ("Standard Deviation of Price", column_store.sd_price),
    #     ("Average Price", column_store.avg_price),
    #     ("Minimum Price per Square Meter", column_store.min_price_per_sqm),
    # ]

    # results = [
    #     {
    #         "Year": year,
    #         "Month": month,
    #         "Town": town,
    #         "Category": category,
    #         "Value": func(year, month, town),
    #     }
    #     for category, func in categories
    # ]

    # with open(f"ScanResult_{matric_number}.csv", mode="w", newline="") as file:
    #     writer = csv.DictWriter(
    #         file, fieldnames=["Year", "Month", "Town", "Category", "Value"]
    #     )
    #     writer.writeheader()
    #     for result in results:
    #         writer.writerow(result)


if __name__ == "__main__":
    main()
