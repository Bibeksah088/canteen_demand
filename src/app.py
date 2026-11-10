"""
Canteen Demand Estimator
A lightweight daily batch preparation planner for college canteens.
Runs both in CLI mode (with built-in fallback) and interactive Streamlit UI.
"""

import os
import sys
import csv
import argparse

REQUIRED_COLUMNS = ["date", "item", "quantity_prepared", "quantity_sold", "leftover"]

# Try importing third-party libraries; gracefully degrade for headless CLI if absent
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def load_and_validate_data_raw(filepath: str):
    """
    Standard-library CSV reader and validator.
    Detects missing values, bad rows, and invalid arithmetic.
    Returns: (clean_records, warnings)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at: {filepath}")

    warnings = []
    clean_records = []

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or corrupted.")

        missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"CSV is missing required columns: {missing_cols}. Found: {reader.fieldnames}")

        for idx, row in enumerate(reader, start=2):
            item = (row.get("item") or "").strip()
            date = (row.get("date") or "").strip()

            try:
                prepared = float(row.get("quantity_prepared", 0))
                sold = float(row.get("quantity_sold", 0))
                leftover = float(row.get("leftover", 0))
            except (ValueError, TypeError):
                warnings.append(f"Row {idx} skipped: Non-numeric quantity in record for '{item}' on {date}.")
                continue

            if prepared < 0 or sold < 0 or leftover < 0:
                warnings.append(f"Row {idx} skipped: Negative quantity ({prepared}, {sold}, {leftover}) for '{item}'.")
                continue

            if sold > prepared:
                warnings.append(
                    f"Row {idx} skipped: Sold ({sold}) cannot exceed Prepared ({prepared}) for '{item}' on {date}."
                )
                continue

            if prepared != (sold + leftover):
                discrepancy = prepared - (sold + leftover)
                warnings.append(
                    f"Row {idx} note: Prepared ({prepared}) != Sold ({sold}) + Leftover ({leftover}) [variance {discrepancy:+.1f}]. Retaining data."
                )

            clean_records.append({
                "date": date,
                "item": item,
                "quantity_prepared": prepared,
                "quantity_sold": sold,
                "leftover": leftover
            })

    if not clean_records:
        raise ValueError("No valid rows could be parsed from the dataset.")

    return clean_records, warnings


def calculate_metrics(records, safety_stock_pct: float = 0.10):
    """
    Computes summary metrics and batch recommendations.
    Formula: Recommended = round(Average Demand * (1 + Safety Stock %))
    """
    grouped = {}
    for r in records:
        item = r["item"]
        if item not in grouped:
            grouped[item] = []
        grouped[item].append(r)

    summary = []
    for item, rows in grouped.items():
        n = len(rows)
        tot_prep = sum(r["quantity_prepared"] for r in rows)
        tot_sold = sum(r["quantity_sold"] for r in rows)
        tot_left = sum(r["leftover"] for r in rows)

        avg_prep = tot_prep / n
        avg_sold = tot_sold / n
        avg_left = tot_left / n

        leftover_rate = (tot_left / tot_prep * 100.0) if tot_prep > 0 else 0.0
        stockouts = sum(1 for r in rows if r["quantity_sold"] == r["quantity_prepared"] and r["leftover"] == 0)

        recommended = int(round(avg_sold * (1.0 + safety_stock_pct)))

        summary.append({
            "Item": item,
            "Observations": n,
            "Avg Prepared": round(avg_prep, 1),
            "Avg Demand (Sold)": round(avg_sold, 1),
            "Avg Leftover": round(avg_left, 1),
            "Leftover Rate (%)": round(leftover_rate, 1),
            "Stockout Days": stockouts,
            "Recommended Prep": recommended
        })

    return summary


def plot_comparison_chart(rec_records):
    """Generates comparison chart using Matplotlib if available."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    items = [r["Item"] for r in rec_records]
    x = range(len(items))
    width = 0.25

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
    ax.bar([p - width for p in x], [r["Avg Prepared"] for r in rec_records], width=width, label="Avg Prepared", color="#6c757d")
    ax.bar(x, [r["Avg Demand (Sold)"] for r in rec_records], width=width, label="Avg Actual Sold", color="#28a745")
    ax.bar([p + width for p in x], [r["Recommended Prep"] for r in rec_records], width=width, label="Recommended Tomorrow", color="#007bff")

    ax.set_ylabel("Portions / Units")
    ax.set_title("Canteen Demand: Current Average vs. Recommended Prep")
    ax.set_xticks(list(x))
    ax.set_xticklabels(items, rotation=15, ha="right")
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig


def run_cli(csv_path: str, safety_stock: float):
    """Executes headless command line report."""
    print("==================================================")
    print("  CANTEEN DEMAND ESTIMATOR - CLI REPORT")
    print("==================================================")
    print(f"Loading data from: {csv_path}")
    print(f"Safety stock buffer: {safety_stock * 100:.1f}%\n")

    try:
        clean_records, warnings = load_and_validate_data_raw(csv_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    if warnings:
        print(f"[!] Validation Warnings ({len(warnings)} found):")
        for w in warnings:
            print(f"    - {w}")
        print()

    rec_list = calculate_metrics(clean_records, safety_stock_pct=safety_stock)

    header = f"{'Item':<12} | {'Obs':<4} | {'Avg Prep':<8} | {'Avg Sold':<8} | {'Avg Left':<8} | {'Leftover %':<10} | {'Stockouts':<9} | {'Rec Prep':<8}"
    print(header)
    print("-" * len(header))
    for r in rec_list:
        print(f"{r['Item']:<12} | {r['Observations']:<4} | {r['Avg Prepared']:<8.1f} | {r['Avg Demand (Sold)']:<8.1f} | {r['Avg Leftover']:<8.1f} | {r['Leftover Rate (%)']:<10.1f} | {r['Stockout Days']:<9} | {r['Recommended Prep']:<8}")

    print("\n[i] Recommendation Formula: round(Avg Demand * (1 + Safety Stock %))")
    print("==================================================")


def run_streamlit_app():
    """Streamlit Dashboard interface."""
    import streamlit as st

    st.set_page_config(page_title="Canteen Demand Estimator", page_icon="🍲", layout="wide")

    st.title("🍲 Canteen Daily Demand Estimator")
    st.caption("Helping college canteen staff prepare the right batch size based on real sales & leftover history.")

    st.sidebar.header("⚙️ Configuration")
    csv_file = st.sidebar.text_input("CSV File Path", value="data.csv")

    safety_stock_slider = st.sidebar.slider(
        "Safety Stock Buffer (%)",
        min_value=0,
        max_value=30,
        value=10,
        step=1,
        help="Extra buffer added above average demand to prevent lunch stockouts."
    )
    safety_stock = safety_stock_slider / 100.0

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Formula:**\n"
        r"$\text{Recommended} = \text{round}(\overline{\text{Demand}} \times (1 + \text{Safety Stock}))$"
    )

    if not os.path.exists(csv_file):
        st.warning(f"File `{csv_file}` not found. Please place your collected `data.csv` in the root folder.")
        return

    try:
        clean_records, warnings = load_and_validate_data_raw(csv_file)
    except Exception as err:
        st.error(f"Failed to load dataset: {err}")
        return

    if warnings:
        with st.expander(f"⚠️ Data Quality Audit ({len(warnings)} notes/issues handled)", expanded=False):
            for w in warnings:
                st.write(f"- {w}")

    rec_list = calculate_metrics(clean_records, safety_stock_pct=safety_stock)
    
    if PANDAS_AVAILABLE:
        rec_df = pd.DataFrame(rec_list)
        clean_df = pd.DataFrame(clean_records)
    else:
        rec_df = rec_list
        clean_df = clean_records

    # KPI summary
    total_prep = sum(r["quantity_prepared"] for r in clean_records)
    total_left = sum(r["leftover"] for r in clean_records)
    overall_leftover_pct = (total_left / total_prep * 100.0) if total_prep > 0 else 0.0
    total_stockout_days = sum(r["Stockout Days"] for r in rec_list)
    total_prep_recommended = sum(r["Recommended Prep"] for r in rec_list)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Menu Items Tracked", len(rec_list))
    col2.metric("Overall Leftover Rate", f"{overall_leftover_pct:.1f}%")
    col3.metric("Stockout Instances", total_stockout_days)
    col4.metric("Total Recommended Units", total_prep_recommended)

    st.markdown("---")

    c_left, c_right = st.columns([1.1, 0.9])

    with c_left:
        st.subheader("📋 Recommended Batch Quantities for Tomorrow")
        if PANDAS_AVAILABLE:
            st.dataframe(
                rec_df.style.highlight_max(axis=0, subset=["Recommended Prep"], color="#e6f2ff"),
                use_container_width=True
            )
        else:
            st.write(rec_list)

    with c_right:
        st.subheader("📊 Actual vs Recommended Quantities")
        fig = plot_comparison_chart(rec_list)
        if fig:
            st.pyplot(fig)
        else:
            st.info("Matplotlib not available to render chart.")

    with st.expander("🔍 View Raw Verified Data Rows", expanded=False):
        if PANDAS_AVAILABLE:
            st.dataframe(clean_df, use_container_width=True)
        else:
            st.write(clean_records)


if __name__ == "__main__":
    is_streamlit = (
        "streamlit" in sys.modules
        or any("streamlit" in arg for arg in sys.argv)
        or os.environ.get("_STREAMLIT_RUN") is not None
    )

    if not is_streamlit and ("run" not in sys.argv):
        parser = argparse.ArgumentParser(description="Canteen Demand Estimator CLI")
        parser.add_argument("--csv", type=str, default="data.csv", help="Path to data.csv")
        parser.add_argument("--safety-stock", type=float, default=0.10, help="Safety stock fraction (e.g. 0.10 for 10%)")
        args = parser.parse_args()
        run_cli(args.csv, args.safety_stock)
    else:
        run_streamlit_app()
