"""
Streamlit UI for the Analysis tab.
Displays summary statistics and visualizations of generated data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go # Not strictly needed here
from typing import Dict, Any # Needed for generate_summary_stats signature


# Helper function used only within the analysis tab logic
def generate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate summary statistics for the dataframe"""
    stats = {"numeric_summary": None, "categorical_summary": None}

    # Numeric columns
    numeric_df = df.select_dtypes(include=["number"])
    if not numeric_df.empty:
        numeric_stats = numeric_df.describe().T.reset_index()
        numeric_stats.rename(columns={"index": "Field"}, inplace=True)
        stats["numeric_summary"] = numeric_stats

    # Categorical columns
    categorical_summary_dict = {}
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        # Use a heuristic threshold like 50 unique values for showing counts
        unique_count = df[col].nunique()
        if unique_count <= 50 and df[col].count() > 0:
            # Include missing values in counts for completeness
            value_counts = df[col].value_counts(dropna=False)
            value_counts_display = value_counts.head(20).to_dict() # Limit display to top 20

            mode_val = df[col].mode()
            categorical_summary_dict[col] = {
                "unique_values": unique_count,
                "most_frequent": mode_val.iloc[0] if not mode_val.empty else None,
                "value_counts": value_counts_display,
            }
        elif df[col].count() > 0: # High cardinality but has data
             mode_val = df[col].mode()
             categorical_summary_dict[col] = {
                 "unique_values": unique_count,
                 "most_frequent": mode_val.iloc[0] if not mode_val.empty else None,
                 "value_counts": None, # Don't show counts
             }
        # Else: Column is all missing, skip

    if categorical_summary_dict:
        stats["categorical_summary"] = categorical_summary_dict

    return stats


# --- Main function for the Analysis Tab UI ---
def analysis_tab():
    """Data analysis and visualization tab UI layout"""
    # Access generated_data from session state
    if st.session_state.get("generated_data") is not None:
        df = st.session_state.generated_data

        st.subheader("🔍 Data Analysis")

        try:
            # Check if df is empty
            if df.empty:
                st.info("Generated data is empty. Cannot perform analysis.")
                return

            # Summary statistics
            stats = generate_summary_stats(df)

            # Numeric data analysis
            if (
                stats["numeric_summary"] is not None
                and not stats["numeric_summary"].empty
            ):
                st.subheader("📊 Numeric Fields Summary")
                st.dataframe(
                    stats["numeric_summary"].round(2), use_container_width=True, hide_index=True
                )

                # Create distribution plots for numeric columns
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if len(numeric_cols) > 0:
                    selected_col = st.selectbox(
                        "Select field for distribution plot",
                        numeric_cols,
                        key="analysis_numeric_plot",
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.histogram(
                            df,
                            x=selected_col,
                            title=f"Distribution of {selected_col}",
                            nbins=30,
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.box(
                            df, y=selected_col, title=f"Box Plot of {selected_col}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric fields found for summary.")

            # Categorical data analysis
            if stats["categorical_summary"]:
                st.subheader("📋 Categorical Fields Summary")

                # Display expanders only for fields that have info
                fields_with_categorical_summary = [
                    f for f, info in stats["categorical_summary"].items() if info
                ]
                if fields_with_categorical_summary:
                    for field in fields_with_categorical_summary:
                        info = stats["categorical_summary"][
                            field
                        ]  # Get info for the field
                        with st.expander(f"📊 {field} Analysis"):
                            col1, col2 = st.columns([1, 2])

                            with col1:
                                st.metric(
                                    "Unique Values", info.get("unique_values", "N/A")
                                )
                                if info.get("most_frequent") is not None: # Check for None explicitly
                                    # Handle cases where most_frequent might be a list (multiple modes)
                                    if isinstance(info['most_frequent'], list):
                                        st.write(
                                            f"**Most Frequent:** {', '.join(map(str, info['most_frequent']))}"
                                        )
                                    else:
                                         st.write(
                                            f"**Most Frequent:** {info['most_frequent']}"
                                        )
                                else:
                                    st.write(
                                        "**Most Frequent:** N/A"
                                    )

                            with col2:
                                if info.get("value_counts"):
                                    # Value counts are already limited to top 20 in generate_summary_stats
                                    value_counts_df = pd.DataFrame(
                                        list(info["value_counts"].items()),
                                        columns=["Value", "Count"],
                                    )

                                    fig = px.bar(
                                        value_counts_df,
                                        x="Value",
                                        y="Count",
                                        title=f"Value Counts for {field}",
                                    )
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    if info.get("unique_values", 0) > 50:
                                        st.info(
                                            f"Value counts omitted for high cardinality field ({info['unique_values']} unique values)."
                                        )
                                    else:
                                        st.info(
                                            f"No value counts available for {field} (might be all missing or no data)."
                                        )
                else:
                    st.info("No categorical fields found with summary information.")

            else:
                st.info("No categorical fields found for summary.")

        except Exception as e:
            st.error(f"Error generating analysis: {str(e)}")
            st.exception(e)

        # Data preview with filtering
        st.subheader("👀 Data Preview")

        col1, col2 = st.columns([3, 1])

        with col1:
            # Access perf_max_rows from session state (set in Advanced tab, read here)
            max_preview_rows = st.session_state.get("perf_max_rows", 100)
            show_rows = st.slider(
                "Number of rows to display",
                5,
                max_preview_rows,
                st.session_state.get("last_show_rows", min(20, max_preview_rows)), # Remember last value, capped by max
                key="preview_row_slider",
            )
            st.session_state.last_show_rows = show_rows

        with col2:
            show_only_errors = st.checkbox(
                "Show only records with errors",
                value=st.session_state.get("last_show_only_errors", False), # Remember last value
                key="preview_errors_checkbox"
            )
            st.session_state.last_show_only_errors = show_only_errors


        display_df = df.copy()

        if show_only_errors:
            # A simple check for missing values to indicate potential errors introduced by dirty factory
            # A more robust check would depend on how errors are marked in the generated data
            error_mask = display_df.isnull().any(axis=1)
            display_df = display_df[error_mask]

            if len(display_df) == 0:
                st.info("No records with missing values found based on this simple check.")
            else:
                st.write(
                    f"Showing {len(display_df):,} records with potential errors out of {len(df):,} total"
                )

        st.dataframe(
            display_df.head(show_rows), use_container_width=True, hide_index=True
        )

    else:
        st.info("🎲 Generate data first to see analysis")