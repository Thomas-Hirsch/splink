from __future__ import annotations

import json
import os
from typing import Any

from splink.internals.pipeline import CTEPipeline


class LinkerMisc:
    def __init__(self, linker):
        self._linker = linker

    def save_model_to_json(
        self, out_path: str | None = None, overwrite: bool = False
    ) -> dict[str, Any]:
        """Save the configuration and parameters of the linkage model to a `.json` file.

        The model can later be loaded back in using `linker.load_model()`.
        The settings dict is also returned in case you want to save it a different way.

        Examples:
            ```py
            linker.save_model_to_json("my_settings.json", overwrite=True)
            ```
        Args:
            out_path (str, optional): File path for json file. If None, don't save to
                file. Defaults to None.
            overwrite (bool, optional): Overwrite if already exists? Defaults to False.

        Returns:
            dict: The settings as a dictionary.
        """
        model_dict = self._linker._settings_obj.as_dict()
        if out_path:
            if os.path.isfile(out_path) and not overwrite:
                raise ValueError(
                    f"The path {out_path} already exists. Please provide a different "
                    "path or set overwrite=True"
                )
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(model_dict, f, indent=4)
        return model_dict

    def query_sql(self, sql, output_type="pandas"):
        """
        Run a SQL query against your backend database and return
        the resulting output.

        Examples:
            ```py
            linker = Linker(df, settings, db_api)
            df_predict = linker.predict()
            linker.query_sql(f"select * from {df_predict.physical_name} limit 10")
            ```

        Args:
            sql (str): The SQL to be queried.
            output_type (str): One of splink_df/splinkdf or pandas.
                This determines the type of table that your results are output in.
        """

        output_tablename_templated = "__splink__df_sql_query"

        pipeline = CTEPipeline()
        pipeline.enqueue_sql(sql, output_tablename_templated)
        splink_dataframe = self._linker.db_api.sql_pipeline_to_splink_dataframe(
            pipeline, use_cache=False
        )

        if output_type in ("splink_df", "splinkdf"):
            return splink_dataframe
        elif output_type == "pandas":
            out = splink_dataframe.as_pandas_dataframe()
            # If pandas, drop the table to cleanup the db
            splink_dataframe.drop_table_from_database_and_remove_from_cache()
            return out
        else:
            raise ValueError(
                f"output_type '{output_type}' is not supported.",
                "Must be one of 'splink_df'/'splinkdf' or 'pandas'",
            )
