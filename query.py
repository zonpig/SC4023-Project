import pandas as pd


class Query:
    @staticmethod
    def query(
        year,
        month,
        town,
        area_query,
        month_query,
        year_query,
        town_query,
        price_query,
        log_query=False,
    ):
        """ """

        rows_scanned = [0] * 4
        col_idx = 0

        # start with area
        area_position_match, rows_scanned = area_query(rows_scanned, col_idx)
        col_idx += 1

        # year
        year_position_match, rows_scanned = year_query(
            area_position_match, rows_scanned, col_idx, year
        )
        col_idx += 1

        # month
        month_position_match, rows_scanned = month_query(
            year_position_match, rows_scanned, col_idx, month
        )
        col_idx += 1

        # town
        town_position_match, rows_scanned = town_query(
            month_position_match, rows_scanned, col_idx, town
        )
        col_idx += 1

        # price
        query_res = price_query(town_position_match)

        if log_query:
            col_string = ""
            query_lengths = {}
            col_string += "->floor_area_sqm"
            query_lengths[col_string] = rows_scanned[0]
            col_string += "->year"
            query_lengths[col_string] = rows_scanned[1]
            col_string += "->month"
            query_lengths[col_string] = rows_scanned[2]
            col_string += "->town"
            query_lengths[col_string] = rows_scanned[3]

            query_lengths_df = pd.DataFrame(
                {
                    "cols": list(query_lengths.keys()),
                    "lengths": list(query_lengths.values()),
                }
            )
            return query_res, query_lengths_df

        return query_res
