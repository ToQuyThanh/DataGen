"""
Streamlit UI for the Data Quality tab.
Displays a data quality report based on generated data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go # Not strictly needed here
from typing import Dict, Any

# Import the utility function for data quality validation
from datagen.utils.helpers import validate_data_quality

# Import SchemaManager if needed for any schema-specific quality checks, otherwise remove.
# It's not used in the current validate_data_quality, so remove for now.
# from datagen.core.schema import SchemaManager


# --- Main function for the Data Quality Tab UI ---
def data_quality_tab():
    """Data quality analysis tab UI layout"""
    # Access generated_data from session state
    if st.session_state.get("generated_data") is not None:
        df = st.session_state.generated_data

        st.subheader("📊 Data Quality Report")

        try:
            if df.empty:
                st.info("Generated data is empty. Cannot generate quality report.")
                return

            # Ensure validate_data_quality handles empty dataframe gracefully if needed
            # It's imported from datagen.utils.helpers
            quality_report = validate_data_quality(df)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Records",
                    quality_report["total_records"],
                    help="Total number of records in dataset",
                )

            with col2:
                st.metric(
                    "Total Fields",
                    quality_report["total_fields"],
                    help="Number of fields/columns",
                )

            with col3:
                total_missing = quality_report["missing_values"]["count"]
                st.metric(
                    "Missing Values",
                    total_missing,
                    help=f"Missing value percentage: {quality_report['missing_values']['percentage']}%",
                )

            with col4:
                duplicate_count = quality_report["duplicates"]["count"]
                st.metric(
                    "Duplicate Records",
                    duplicate_count,
                    help=f"Duplicate percentage: {quality_report['duplicates']['percentage']}%",
                )

            # 🔍 Missing Values Analysis
            if total_missing > 0:
                st.subheader("🔍 Missing Values Analysis")

                by_field = quality_report["missing_values"]["by_field"]
                # Filter out fields with 0 missing count for cleaner display
                missing_data = [
                    {
                        "Field": field,
                        "Missing Count": count,
                        "Missing %": round((count / len(df)) * 100, 2) if len(df) > 0 else 0,
                    }
                    for field, count in by_field.items()
                    if count > 0 # Only include fields with missing values
                ]

                if missing_data:
                    missing_df = pd.DataFrame(missing_data)
                    # Sort by Missing Count or % for better visibility
                    missing_df = missing_df.sort_values(by="Missing Count", ascending=False)

                    st.dataframe(missing_df, use_container_width=True, hide_index=True)

                    # Optional: Add a bar chart
                    try:
                        fig = px.bar(
                            missing_df,
                            x="Field",
                            y="Missing %",
                            title="Missing Values by Field",
                            color="Missing %",
                            color_continuous_scale="Reds",
                            # text_auto=True # Add percentages on bars (requires recent plotly/streamlit)
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as chart_err:
                        st.warning(f"Could not render missing values chart: {chart_err}")


                else:
                     # This case shouldn't happen if total_missing > 0, but as a fallback
                    st.info("No fields with missing values found in the report details.")


            # 📈 Data Type Distribution
            st.subheader("📈 Data Type Distribution")
            if quality_report.get("data_types"):
                type_counts = pd.Series(quality_report["data_types"]).value_counts()
                if not type_counts.empty:
                    fig = px.pie(
                        values=type_counts.values,
                        names=type_counts.index,
                        title="Distribution of Data Types",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data type information available in the report.")
            else:
                st.info("No data type information available.")

            # Optional: Show memory usage
            st.caption(f"🧠 Memory usage: {quality_report.get('memory_usage_mb', 'N/A')} MB") # Use .get for safety


        except Exception as e:
            st.error(f"Error generating quality report: {str(e)}")
            st.exception(e)

    else:
        st.info("🎲 Generate data first to see quality analysis")