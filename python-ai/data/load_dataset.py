
from pathlib import Path
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]

DATASET_CANDIDATES = [
    REPO_ROOT / "dataset" / "raw" / "retail_store_inventory.csv",
    REPO_ROOT / "retail_store_inventory.csv",
]


def load_dataset(dataset_path=None):
    """Load the approved RetailAI inventory dataset."""

    if dataset_path is not None:
        path = Path(dataset_path)

        if not path.is_absolute():
            path = REPO_ROOT / path

        if not path.is_file():
            raise FileNotFoundError(
                f"Dataset not found: {path}"
            )
    else:
        path = next(
            (candidate for candidate in DATASET_CANDIDATES
             if candidate.is_file()),
            None,
        )

        if path is None:
            expected = "\n".join(
                str(candidate)
                for candidate in DATASET_CANDIDATES
            )
            raise FileNotFoundError(
                "Could not find the RetailAI dataset. "
                f"Checked:\n{expected}"
            )

    df = pd.read_csv(path)

    print("=" * 55)
    print("RETAILAI - DATASET LOADER")
    print("=" * 55)
    print(f"Loaded from: {path}")
    print(f"Records: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print("\nColumn names:")
    print(df.columns.tolist())
    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))

    return df


if __name__ == "__main__":
    load_dataset()
