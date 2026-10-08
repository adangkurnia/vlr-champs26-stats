import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def load_to_parquet(
    df: pd.DataFrame,
    file_path: str,
    compression: str = "gzip",
    keep_index: bool = False,
) -> None:
    """
    Saves a pandas DataFrame to a Parquet file safely.

    Parameters:
        df (pd.DataFrame): The DataFrame to save.
        file_path (str): Target path for the .parquet file.
        compression (str): Compression type ('snappy', 'gzip', 'brotli', 'lz4', 'zstd', or None).
        keep_index (bool): Whether to include the DataFrame's index in the Parquet file.
    """

    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Write DataFrame to Parquet
        df.to_parquet(
            path=file_path, engine="pyarrow", compression=compression, index=keep_index
        )
        logger.info("Successfully saved DataFrame to %s", file_path)

    except FileExistsError as e:
        logger.error("Error saving DataFrame to Parquet: %s", e)
    except OSError as e:
        logger.error("Error saving DataFrame to Parquet: %s", e)
