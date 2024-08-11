from dataclasses import dataclass

import numpy as np
import pandas as pd
import polars as pl

from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import VotingRegressor
import lightgbm as lgb
import optuna

DATA_PATH = "experiment/processed_data.csv"

DROP_COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "turnover",
    "month",
    "day_of_year",
    "hour",
    "day",
]


@dataclass
class CFG:
    seed: int = 42
    n_trials: int = 100
    n_splits: int = 3
    n_estimators: int = 10000
    early_stop_patience: int = 100
    n_splits: int = 3
    val_size: int = 1


if __name__ == "__main__":
    df = pl.read_csv(DATA_PATH)
    df = df.with_columns(pl.col("datetime").str.strptime(pl.Datetime))

    df = df.drop(DROP_COLUMNS)
    df = df.drop_nulls()

    # 最終週が不完全なので削除
    df = df.filter(pl.col("num_week") < 59)

    max_week = int(df.select("num_week").max().to_numpy().squeeze())
    min_week = int(df.select("num_week").min().to_numpy().squeeze())

    all_train_phases = np.arange(min_week, max_week, 1)
    tscv = TimeSeriesSplit(n_splits=CFG.n_splits, test_size=CFG.val_size)

    datasets = []

    for train_phases, valid_phases in tscv.split(all_train_phases):
        # データセットの作成
        df_train = (
            df.filter(pl.col("num_week").is_in(train_phases))
            .to_pandas()
            .drop(["datetime", "num_week"], axis=1)
        )
        df_valid = (
            df.filter(pl.col("num_week").is_in(valid_phases))
            .to_pandas()
            .drop(["datetime", "num_week"], axis=1)
        )

        datasets.append((df_train, df_valid))

    trial_best_iters = []

    def objective(trial):
        # 探索するパラメータ
        trial_params = {
            "num_leaves": trial.suggest_int("num_leaves", 2, 256),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-5, 1e5, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-5, 1e5, log=True),
            "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1e-1, log=True),
            "verbosity": -1,
        }

        val_scores = []
        best_iters = []

        for df_train, df_valid in datasets:
            # モデルの学習 (Early Stoppingあり)
            model = lgb.LGBMRegressor(
                objective="rmse", n_estimators=10000, **trial_params
            )

            model.fit(
                df_train.drop(["target"], axis=1),
                df_train["target"],
                eval_set=[(df_valid.drop(["target"], axis=1), df_valid["target"])],
                eval_metric="rmse",
                callbacks=[
                    lgb.early_stopping(
                        stopping_rounds=CFG.early_stop_patience, verbose=False
                    )
                ],
            )

            iteration = model.best_iteration_
            n_average = 4
            model = VotingRegressor(
                [
                    (
                        f"lgbm{i}",
                        lgb.LGBMRegressor(
                            objective="rmse",
                            n_estimators=iteration,
                            random_state=CFG.seed + i,
                            **trial_params,
                        ),
                    )
                    for i in range(n_average)
                ]
            )
            model.fit(df_train.drop(["target"], axis=1), df_train["target"])

            y_pred = model.predict(df_valid.drop(["target"], axis=1))
            val_score = direction_accuracy(df_valid["target"], y_pred)
            val_scores.append(val_score)

            best_iters.append(iteration)

        trial_best_iters.append(best_iters)

        return np.mean(val_scores)

    study = optuna.create_study(
        direction="maximize", sampler=optuna.samplers.TPESampler(seed=CFG.seed)
    )
    study.optimize(objective, n_trials=CFG.n_trials)

    # 最適なパラメータを表示
    print("Best trial:")
    trial = study.best_trial
    print(f"  Value: {trial.value}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")

    # 最適なパラメータの取得
    tuned_params = trial.params
    tuned_iter = int(np.mean(trial_best_iters[trial.number]))
