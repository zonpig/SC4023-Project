import csv
import time
import argparse
from tqdm import tqdm
from column_store import ResalePriceData
from column_store_encoded import ResalePriceDataEncoded
from column_store_zone_map_cat import ResalePriceDataZoneMapCat
from column_store_zone_map_num import ResalePriceDataZoneMapNum
from column_store_combined_cat import ResalePriceDataCombinedCat
from column_store_combined_num import ResalePriceDataCombinedNum
from column_store_mp import ResalePriceDataMP

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
    elif type == 2:
        resale_data = ResalePriceDataZoneMapNum()
    elif type == 3:
        resale_data = ResalePriceDataZoneMapCat()
    elif type == 4:
        resale_data = ResalePriceDataCombinedNum()
    elif type == 5:
        resale_data = ResalePriceDataCombinedCat()
    elif type == 6:
        resale_data = ResalePriceDataMP()

    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)
    return resale_data


def split_csv(file_path: str):
    # Find the size of the csv file and see if it can fit into main memory. If it cannot then split the file using the number of rows until the splits can fit into main memory


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


def main(args):
    # matric number
    matric_number = "U2121223J"  # Darren
    # matric_number = "U2121763H" #Bryan
    # matric_number = "U2122055E" #Jin Yang

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"
 
    # NOTE: Uncomment this for testing avg runtime
    
    splits = split_csv(file_path)
    
    
    
    column_store = read_csv(file_path, 0)
    column_store_encoded = read_csv(file_path, 1)
    column_store_zone_map_num = read_csv(file_path, 2)
    column_store_zone_map_cat = read_csv(file_path, 3)
    column_store_combined_num = read_csv(file_path, 4)
    column_store_combined_cat = read_csv(file_path, 5)

    # preprocess
    column_store_encoded.encode_town()
    column_store_encode_town = column_store_encoded.town_encoder.mappings[
        town
    ]  # get the encoded town value

    column_store_zone_map_num.create_zone_map(16)

    column_store_zone_map_cat.create_zone_map("flat_type")

    column_store_combined_num.create_zone_map(16)
    column_store_combined_num.encode_town()
    column_store_combined_num_town = column_store_combined_num.town_encoder.mappings[
        town
    ]

    column_store_combined_cat.create_zone_map(
        "flat_type"
    )  # have to zonemap first to create the rearrange columns, then encode town on that rearrange columns
    column_store_combined_cat.encode_town()
    column_store_combined_cat_town = column_store_combined_cat.town_encoder.mappings[
        town
    ]  # get the encoded town value

    scenarios = {
        "original": {"col_db": column_store, "town": town},
        "categorical_encoded": {
            "col_db": column_store_encoded,
            "town": column_store_encode_town,
        },
        "zone_map_num": {"col_db": column_store_zone_map_num, "town": town},
        "zone_map_cat": {"col_db": column_store_zone_map_cat, "town": town},
        "combined_num": {
            "col_db": column_store_combined_num,
            "town": column_store_combined_num_town,
        },
        "combined_cat": {
            "col_db": column_store_combined_cat,
            "town": column_store_combined_cat_town,
        },
    }

    scan_results = {}

    for _ in tqdm(range(args.num_runs), desc="Running repeated runs of queries."):
        for k in scenarios.keys():
            print(f"Scenario: {k}")
            start_time = time.time()
            x = scenarios[k]["col_db"].min_price(year, month, scenarios[k]["town"])
            end_time = time.time()
            times = scenarios[k].get("min_price", [])
            times.append(end_time - start_time)
            scenarios[k]["min_price"] = times
            print(f"Min price: {x}")

            if "min_price" not in scan_results:
                scan_results["Minimum Price"] = x

            start_time = time.time()
            x = scenarios[k]["col_db"].sd_price(year, month, scenarios[k]["town"])
            end_time = time.time()
            times = scenarios[k].get("sd_price", [])
            times.append(end_time - start_time)
            scenarios[k]["sd_price"] = times
            print(f"SD price: {x}")

            if "Standard Deviation of Price" not in scan_results:
                scan_results["Standard Deviation of Price"] = x

            start_time = time.time()
            x = scenarios[k]["col_db"].avg_price(year, month, scenarios[k]["town"])
            end_time = time.time()
            times = scenarios[k].get("avg_price", [])
            times.append(end_time - start_time)
            scenarios[k]["avg_price"] = times
            print(f"Avg price: {x}")

            if "Average Price" not in scan_results:
                scan_results[" Average Price"] = x

            start_time = time.time()
            x = scenarios[k]["col_db"].min_price_per_sqm(
                year, month, scenarios[k]["town"]
            )
            end_time = time.time()
            times = scenarios[k].get("min_price_per_sqm", [])
            times.append(end_time - start_time)
            scenarios[k]["min_price_per_sqm"] = times
            print(f"Min price per sqm: {x}")
            print()

            if "Minimum Price per Square Meter" not in scan_results:
                scan_results["Minimum Price per Square Meter"] = x

    print(f"{args.num_runs} runs concluded!")
    print()
    if args.aggregation == "mean":
        for k in scenarios.keys():
            print("Scenario: ", k)
            N = args.num_runs
            print(
                f"Avg time taken for min_price query: {sum(scenarios[k]['min_price']) / N}"
            )
            print(
                f"Avg time taken for sd_price query: {sum(scenarios[k]['sd_price']) / N}"
            )
            print(
                f"Avg time taken for avg_price query: {sum(scenarios[k]['avg_price']) / N}"
            )
            print(
                f"Avg time taken for min_price_per_sqm query: {sum(scenarios[k]['min_price_per_sqm']) / N}"
            )

    results = [
        {
            "Year": year,
            "Month": month,
            "Town": town,
            "Category": category,
            "Value": round(value, 2),
        }
        for category, value in scan_results.items()
    ]

    with open(f"ScanResult_{matric_number}.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["Year", "Month", "Town", "Category", "Value"]
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your program")

    # Adding arguments
    parser.add_argument(
        "--num_runs", type=int, default=1, help="Number of runs to repeat."
    )

    parser.add_argument(
        "--aggregation",
        type=str,
        default="mean",
        help="Method to aggregate runs results.",
    )
    args = parser.parse_args()

    main(args)
