import numpy as np
import polars as pl

DATA_PATH = "experiment/data.csv"

if __name__ == "__main__":
    df = pl.read_csv(DATA_PATH)
    df = df.with_columns(pl.col("datetime").str.to_datetime(format="%Y-%m-%d %H:%M:%S"))

    df = (
        df.with_columns(
            pl.col("datetime").dt.month().alias("month"),
            pl.col("datetime").dt.ordinal_day().alias("day_of_year"),
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.day().alias("day"),
            pl.col("datetime").dt.weekday().alias("weekday"),
        )
        .with_columns(
            pl.when(pl.col("datetime").dt.minute() < 30)
            .then(pl.col("hour"))
            .otherwise(pl.col("hour") + 0.5)
            .alias("hour")
        )
        .with_columns(
            (np.pi * pl.col("month") / 6).sin().alias("sin(month)"),
            (np.pi * pl.col("month") / 6).cos().alias("cos(month)"),
            (np.pi * pl.col("day_of_year") / 183).sin().alias("sin(day_of_year)"),
            (np.pi * pl.col("day_of_year") / 183).cos().alias("cos(day_of_year)"),
            (np.pi * pl.col("hour") / 12).sin().alias("sin(hour)"),
            (np.pi * pl.col("hour") / 12).cos().alias("cos(hour)"),
        )
    )

    df = (
        df.with_columns(pl.col("close").log().diff().alias("log_return"))
        .with_columns(pl.col("log_return").shift(-1).alias("target"))
        .with_columns(
            pl.col("log_return").shift(1).alias("log_return_1"),
            pl.col("log_return").shift(2).alias("log_return_2"),
            pl.col("log_return").shift(3).alias("log_return_3"),
            pl.col("log_return").rolling_mean(5).alias("log_return_rolling_5"),
            pl.col("log_return").rolling_mean(10).alias("log_return_rolling_10"),
            pl.col("log_return").rolling_mean(20).alias("log_return_rolling_20"),
            pl.col("log_return").rolling_mean(30).alias("log_return_rolling_30"),
            pl.col("log_return").rolling_min(5).alias("log_return_min_5"),
            pl.col("log_return").rolling_min(10).alias("log_return_min_10"),
            pl.col("log_return").rolling_min(20).alias("log_return_min_20"),
            pl.col("log_return").rolling_min(30).alias("log_return_min_30"),
            pl.col("log_return").rolling_max(5).alias("log_return_max_5"),
            pl.col("log_return").rolling_max(10).alias("log_return_max_10"),
            pl.col("log_return").rolling_max(20).alias("log_return_max_20"),
            pl.col("log_return").rolling_max(30).alias("log_return_max_30"),
            pl.col("log_return").rolling_std(5).alias("log_return_std_5"),
            pl.col("log_return").rolling_std(10).alias("log_return_std_10"),
            pl.col("log_return").rolling_std(20).alias("log_return_std_20"),
            pl.col("log_return").rolling_std(30).alias("log_return_std_30"),
            pl.col("log_return").rolling_sum(2).alias("log_return_sum_2"),
            pl.col("log_return").rolling_sum(3).alias("log_return_sum_3"),
            pl.col("log_return").rolling_sum(4).alias("log_return_sum_4"),
            pl.col("log_return").rolling_sum(5).alias("log_return_sum_5"),
        )
        .with_columns(
            (pl.col("log_return") - pl.col("log_return_rolling_5")).alias(
                "log_return_distance_5"
            ),
            (pl.col("log_return") - pl.col("log_return_rolling_10")).alias(
                "log_return_distance_10"
            ),
            (pl.col("log_return") - pl.col("log_return_rolling_20")).alias(
                "log_return_distance_20"
            ),
            (pl.col("log_return") - pl.col("log_return_rolling_30")).alias(
                "log_return_distance_30"
            ),
        )
        .with_columns(
            (pl.col("log_return") > 0)
            .cast(pl.Float32)
            .rolling_sum(5)
            .alias("log_return_positive_5"),
            (pl.col("log_return") > 0)
            .cast(pl.Float32)
            .rolling_sum(10)
            .alias("log_return_positive_10"),
            (pl.col("log_return") > 0)
            .cast(pl.Float32)
            .rolling_sum(20)
            .alias("log_return_positive_20"),
            (pl.col("log_return") > 0)
            .cast(pl.Float32)
            .rolling_sum(30)
            .alias("log_return_positive_30"),
        )
    )

    df = df.with_columns(
        pl.col("volume").log().alias("volume"),
        pl.col("volume").rolling_mean(5).alias("volume_rolling_5"),
        pl.col("volume").rolling_mean(10).alias("volume_rolling_10"),
        pl.col("volume").rolling_mean(20).alias("volume_rolling_20"),
        pl.col("volume").rolling_mean(30).alias("volume_rolling_30"),
    )

    df = df.with_columns(
        (
            pl.when((pl.col("weekday") == 1) & (pl.col("weekday").shift(1) == 7))
            .then(1)
            .otherwise(0)
        )
        .cum_sum()
        .alias("num_week")
    )

    # 最初の週は不完全なので削除、週番号を0-indexedにする
    df = df.filter((pl.col("num_week") > 0))
    df = df.with_columns((pl.col("num_week") - 1).alias("num_week"))

    df.write_csv("experiment/processed_data.csv")
