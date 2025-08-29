from langchain_core.tools import tool
import os, pandas as pd, numpy as np, matplotlib.pyplot as plt


def _ensure_outputs_path(out: str, fallback: str) -> str:
    """Ensure the OUTPUT_DIR exists and return a valid path for saving files."""
    output_dir = os.getenv("OUTPUT_DIR", "/app/outputs")
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, out or fallback)


@tool
def profile_table(file: str) -> str:
    """Generate a statistical profile (summary statistics) of the input dataset.

    Args:
        file (str): Path to the CSV file containing tabular data.

    Returns:
        str: A string representation of the dataset's descriptive statistics.
    """
    df = pd.read_csv(file)
    return str(df.describe(include="all"))


@tool
def plot_chart(file: str, x: str, y: str, out: str = "plot.png") -> str:
    """Plot column `y` against column `x` from the given dataset and save the chart.

    Args:
        file (str): Path to the CSV file.
        x (str): Name of the column to use for the X-axis.
        y (str): Name of the column to use for the Y-axis.
        out (str, optional): Output filename (relative to OUTPUT_DIR). Defaults to "plot.png".

    Returns:
        str: A message with the path where the chart image was saved.
    """
    df = pd.read_csv(file)
    plt.figure(figsize=(8, 5))
    plt.plot(df[x], df[y])
    path = _ensure_outputs_path(out, "plot.png")
    plt.savefig(path)
    return f"Saved plot to {path}"


