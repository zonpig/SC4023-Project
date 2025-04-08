import csv
import operator
from query import Query

from column_store import ResalePriceData
from multiprocess import parallel_processing


class ResalePriceDataMP(ResalePriceData):
    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # STEP: Get floor_area_sqm
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # price
        for i in town_position_match:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

        return min_price if min_price != float("inf") else "No result"

    # Standard Deviation of Price
    def sd_price(self, year, month, town, log_query=False):
        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # STEP: Get price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        if not prices:
            query_res = "No Results"
            mean_price = 0
        else:
            mean_price = sum(prices) / len(prices)
            variance = sum((price - mean_price) ** 2 for price in prices) / (
                len(prices) - 1
            )
            query_res = round(variance**0.5, 2)

        return query_res, len(prices), mean_price

    # Average Price
    def avg_price(self, year, month, town, log_query=False):
        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # STEP: Get price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        if not prices:
            query_res = "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            query_res = round(mean_price, 2)

        return query_res, len(prices)

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town, log_query=False):
        min_price_per_sqm = float("inf")

        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # price
        for i in town_position_match:
            price_per_sqm = (
                self.columns["resale_price"].data[i]
                / self.columns["floor_area_sqm"].data[i]
            )

            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        if min_price_per_sqm == float("inf"):
            query_res = "No Results"
        else:
            query_res = round(min_price_per_sqm, 2)

        return query_res

    def shared_scan(self, year, month, town, log_query=False):
        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        query_res = self.shared_scan_query(town_position_match)

        return query_res


def column_store_mp():
    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataMP()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)
    return resale_data


if __name__ == "__main__":
    Query.column_store_query(column_store_mp())
