import csv
from query import Query
from column_preprocess import CategoricalEncoder
from column_store import ResalePriceData


class ResalePriceDataEncoded(ResalePriceData):
    def __init__(self):
        super().__init__()
        self.town_encoder = None

    def encode_town(self):
        self.town_encoder = CategoricalEncoder("town", self.columns["town"].data)
        self.columns["town"].data = self.town_encoder.transform(
            self.columns["town"].data
        )


def column_store_encoded():
    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataEncoded()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    resale_data.encode_town()
    return resale_data


if __name__ == "__main__":
    Query.column_store_query(column_store_encoded())
