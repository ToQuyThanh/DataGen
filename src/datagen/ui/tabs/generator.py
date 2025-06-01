"""
Streamlit UI for the Generator tab.
Handles schema selection, configuration, data generation, and export.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Keep if go traces are used, else remove. px is sufficient here.
from typing import Dict, Any, List
import json
import datetime
import time
import io

# Import core datagen components needed for generation and schema interaction
# Access to SchemaManager Singleton is needed
from datagen.core.generator import DataGenerator
from datagen.core.schema import SchemaManager, DataSchema
from datagen.core.dirty import DirtyDataFactory
# validate_data_quality is used in data_quality_tab, not generator_tab. Remove import.
# from datagen.utils.helpers import validate_data_quality

# Helper functions used only within the generator tab logic
def get_constraints_text(field_config: Dict[str, Any]) -> str:
    """Get human-readable constraints text from a field configuration dictionary"""
    constraints_list = []

    # Keys often nested under 'constraints' or sometimes directly in field_config
    all_config = field_config.copy() # Work on a copy
    if 'constraints' in field_config and isinstance(field_config['constraints'], dict):
         all_config.update(field_config['constraints']) # Merge constraints into top-level for easier access


    if "min_value" in all_config:
        constraints_list.append(f"Min: {all_config['min_value']}")
    if "max_value" in all_config:
        constraints_list.append(f"Max: {all_config['max_value']}")
    if "max_length" in all_config:
        constraints_list.append(f"Length: {all_config['max_length']}")
    if "choices" in all_config and isinstance(all_config['choices'], list):
        constraints_list.append(f"Choices: {len(all_config['choices'])}")
    if "start_date" in all_config:
        constraints_list.append(f"Start Date: {all_config['start_date']}")
    if "end_date" in all_config:
        constraints_list.append(f"End Date: {all_config['end_date']}")
    if "minimum_age" in all_config:
        constraints_list.append(f"Min Age: {all_config['minimum_age']}")
    if "maximum_age" in all_config:
        constraints_list.append(f"Max Age: {all_config['maximum_age']}")
    if "domain" in all_config: # Example for email
         constraints_list.append(f"Domain: {all_config['domain']}")
    if "precision" in all_config: # Example for float
        constraints_list.append(f"Precision: {all_config['precision']}")

    # Add any other common constraints/args here if needed

    return " | ".join(constraints_list) if constraints_list else "None"

def download_template(schema_object: DataSchema):
    """Download CSV template (headers only) for a DataSchema object"""
    if not schema_object or not schema_object.fields:
        st.warning(
            "Cannot download template: Schema object is invalid or has no fields."
        )
        return

    template_df = pd.DataFrame(columns=list(schema_object.fields.keys()))

    buffer = io.BytesIO()
    template_df.to_csv(buffer, index=False, encoding="utf-8")
    buffer.seek(0)

    # Use schema name in filename
    file_name = f"{schema_object.name.lower().replace(' ', '_')}_template.csv"

    st.download_button(
        "📥 Download Template (CSV)",
        buffer,
        file_name,
        "text/csv",
        key=f"dl_template_{schema_object.name.lower()}", # Unique key includes schema name
        use_container_width=True,
    )


def copy_schema_json(schema_dict: Dict[str, Any]):
    """Provide schema JSON for download"""
    schema_json_str = json.dumps(schema_dict, indent=2)

    # Use schema name in filename, default to 'schema' if name is missing
    file_name = f"{schema_dict.get('name', 'schema').lower().replace(' ', '_')}.json"

    st.download_button(
        "📋 Download Schema JSON",
        schema_json_str.encode("utf-8"),
        file_name,
        "application/json",
        key=f"dl_json_{file_name}", # Unique key
        use_container_width=True,
        help="Click to download the schema JSON file.",
    )


def generate_data(
    schema_object: DataSchema, # Accept schema object directly
    num_records: int,
    dirty_ratio: int,
    error_types: Dict[str, bool],
    target_field: List[str] = None, # Target field can be a list
):
    """Generate data based on configuration"""

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Initialize components
        status_text.text("Initializing components...")
        progress_bar.progress(10)

        # These classes are stateless per generation, so creating new ones is fine.
        # The SchemaManager Singleton is accessed implicitly within DataGenerator and DirtyDataFactory if needed,
        # but for generation, they primarily rely on the passed schema_object.
        generator = DataGenerator()
        dirty_factory = DirtyDataFactory()
        # SchemaManager() # No need to get the manager instance here explicitly unless modifying its state

        if not schema_object:
            st.error("Error: Schema object is missing.")
            return

        # Generate clean data
        status_text.text("Generating clean data...")
        progress_bar.progress(30)

        # Use the schema_object directly
        clean_data = generator.generate_batch(schema_object, num_records)

        # Convert to DataFrame early for easier manipulation by dirty factory if needed
        df = pd.DataFrame(clean_data)


        # Apply dirty data if needed
        if dirty_ratio > 0:
            status_text.text("Applying data quality issues...")
            progress_bar.progress(60)

            selected_errors = [k for k, v in error_types.items() if v]

            if selected_errors:
                 # Pass the schema_object to apply_errors as it might need field type info
                df = dirty_factory.apply_errors(
                    df, # Pass DataFrame
                    schema_object, # Pass schema object
                    ratio=dirty_ratio / 100.0, # Pass ratio as float probability
                    target_field=target_field, # Pass list of target fields or None
                    error_types=selected_errors,  # Pass selected error types as list
                )
            else:
                st.warning("No error types selected to apply dirty data.")


        status_text.text("Finalizing data...")
        progress_bar.progress(90)

        # Store the generated data in session state
        st.session_state.generated_data = df

        progress_bar.progress(100)
        status_text.text("✅ Data generation completed!")

        st.success(
            f"✅ Successfully generated {len(df):,} records with {len(df.columns)} fields"
        )

        # Display a quick preview after generation
        with st.expander("👀 Quick Preview", expanded=True):
            # Access perf_max_rows from session state (set in Advanced tab, read here)
            preview_rows = min(len(df), st.session_state.get("perf_max_rows", 100))
            st.dataframe(
                df.head(preview_rows), use_container_width=True, hide_index=True
            )


    except Exception as e:
        st.error(f"❌ Error generating data: {str(e)}")
        st.exception(e)
    finally:
        # Ensure progress bar and status text are cleared
        progress_bar.empty()
        status_text.empty()


# --- Main function for the Generator Tab UI ---
def generator_tab():
    """Main data generation tab UI layout"""
    col1, col2 = st.columns([1, 2])

    # Ensure SchemaManager is initialized (Singleton handles this)
    schema_manager = SchemaManager()
    available_schemas = schema_manager.list_schemas()

    if not available_schemas:
        st.error("No schemas available in the SchemaManager. Please check installation or import a custom schema.")
        return # Stop rendering the tab if no schemas are loaded

    with col1:
        st.subheader("⚙️ Configuration")

        # Schema selection - Use names directly from the SchemaManager
        # Capitalize names for display consistency
        display_schema_names = [name.capitalize() for name in available_schemas]

        # Determine the default selection
        default_schema_index = 0
        if st.session_state.selected_schema_name in available_schemas:
             default_schema_index = available_schemas.index(st.session_state.selected_schema_name)
        # If previously selected schema is no longer available, default to 'customer' if exists, otherwise the first one
        elif "customer" in available_schemas:
             default_schema_index = available_schemas.index("customer")
        elif available_schemas:
             default_schema_index = 0 # Default to the first available schema

        selected_display_name = st.selectbox(
            "📋 Select Schema",
            display_schema_names,
            index=default_schema_index,
            help="Choose a predefined or imported schema",
            key="generator_schema_select" # Add a unique key
        )

        # Convert display name back to lowercase schema name for internal use
        selected_schema_name_lower = selected_display_name.lower()
        st.session_state.selected_schema_name = selected_schema_name_lower # Store the actual schema name

        # Get the selected schema object from the manager
        current_schema_object = schema_manager.get_schema(selected_schema_name_lower)

        if not current_schema_object:
             st.error(f"Failed to retrieve schema '{selected_schema_name_lower}' from SchemaManager.")
             return # Stop if the selected schema object can't be retrieved

        # Number of records
        num_records = st.number_input(
            "📈 Number of Records",
            min_value=1,
            max_value=100000,
            value=st.session_state.get("last_num_records", 100),  # Remember last value
            step=10,
            help="Total number of records to generate",
            key="generator_num_records" # Add a unique key
        )
        st.session_state.last_num_records = num_records  # Store for next rerun

        # Data quality settings
        st.divider()
        st.subheader("🎯 Data Quality")

        generate_clean = st.checkbox(
            "Generate clean data only",
            value=st.session_state.get(
                "last_generate_clean", False
            ),  # Remember last value
            help="Generate only clean data without any errors",
            key="generator_generate_clean" # Add a unique key
        )
        st.session_state.last_generate_clean = generate_clean  # Store for next rerun

        target_field = None  # Initialize target_field

        # Variables for error types and ratio, initialized based on clean/dirty state
        dirty_ratio = 0
        missing_values = invalid_format = out_of_range = duplicates = inconsistent = False

        if not generate_clean:
            dirty_ratio = st.slider(
                "Error Rate (%)",
                min_value=0,
                max_value=50,
                value=st.session_state.get(
                    "last_dirty_ratio", 10
                ),  # Remember last value
                help="Percentage of records with errors",
                key="generator_dirty_ratio" # Add a unique key
            )
            st.session_state.last_dirty_ratio = dirty_ratio  # Store for next rerun

            # Error types in expandable section
            with st.expander(
                "🔧 Error Types",
                expanded=st.session_state.get("last_error_types_expanded", True) ,
            ):  # Remember state
                # Using keys tied to session state to remember expander state
                st.session_state.last_error_types_expanded = True # If expanded is True, update session state on click

                col_a, col_b = st.columns(2)

                with col_a:
                    missing_values = st.checkbox(
                        "Missing Values",
                        value=st.session_state.get("last_missing_values", True),
                        key="generator_missing_values" # Add unique key
                    )
                    invalid_format = st.checkbox(
                        "Invalid Format",
                        value=st.session_state.get("last_invalid_format", True),
                        key="generator_invalid_format" # Add unique key
                    )
                    out_of_range = st.checkbox(
                        "Out of Range",
                        value=st.session_state.get("last_out_of_range", False),
                        key="generator_out_of_range" # Add unique key
                    )

                with col_b:
                    duplicates = st.checkbox(
                        "Duplicates",
                        value=st.session_state.get("last_duplicates", False),
                        key="generator_duplicates" # Add unique key
                    )
                    inconsistent = st.checkbox(
                        "Inconsistent",
                        value=st.session_state.get("last_inconsistent", False),
                        key="generator_inconsistent" # Add unique key
                    )

                # Store error type preferences
                st.session_state.last_missing_values = missing_values
                st.session_state.last_invalid_format = invalid_format
                st.session_state.last_out_of_range = out_of_range
                st.session_state.last_duplicates = duplicates
                st.session_state.last_inconsistent = inconsistent

            # Target field for errors - Updated to support multiple selection
            target_field_enabled = st.checkbox(
                "Target specific field(s) for errors",
                value=st.session_state.get(
                    "last_target_field_enabled", False
                ),  # Remember state
                help="Apply errors to specific field(s) instead of random fields",
                key="generator_target_field_enabled" # Add unique key
            )
            st.session_state.last_target_field_enabled = (
                target_field_enabled  # Store for next rerun
            )

            if target_field_enabled:
                # We already have the current_schema_object from the selectbox logic
                if current_schema_object and current_schema_object.fields:
                    # Get field names for the multiselect
                    field_names = list(current_schema_object.fields.keys())

                    # Determine default values - support both single field (backward compatibility) and multiple fields
                    default_fields = []
                    if "last_target_fields" in st.session_state:
                        # New multiselect format
                        default_fields = [
                            field
                            for field in st.session_state.last_target_fields
                            if field in field_names
                        ]
                    # Removed backward compatibility for single field to simplify session state

                    target_fields = st.multiselect(
                        "Target Field(s)",
                        field_names,
                        default=default_fields,
                        key=f"generator_target_fields_select_{selected_schema_name_lower}", # Unique key includes schema name
                        help="Select one or more fields to apply errors to. Leave empty to apply to random fields.",
                    )

                    # Store selected fields for next session
                    st.session_state.last_target_fields = target_fields

                    # Assign target_field for the generate_data function
                    target_field = target_fields if target_fields else None

                    # Display selected fields info
                    if target_field: # Check if target_field is not None or empty list
                        if len(target_field) == 1:
                            st.info(
                                f"Errors will be applied to field: **{target_field[0]}**"
                            )
                        else:
                            st.info(
                                f"Errors will be applied to {len(target_field)} fields: **{', '.join(target_field)}**"
                            )
                    else:
                        st.info(
                            "No specific fields selected. Errors will be applied to random fields."
                        )

                else:
                    st.info(
                        "Select a schema with defined fields to choose target fields."
                    )
                    target_field = (
                        None  # Ensure target_field is None if no schema/fields
                    )

            else: # If generate clean is selected, or target field is disabled
                target_field = None # Ensure target_field is None if targeting is disabled


    with col2:
        st.subheader("📋 Schema Preview")

        # We already have the current_schema_object
        schema_object = current_schema_object
        schema_dict_for_preview = None # Use this to display dict info

        if schema_object:
             # Use model_dump() for Pydantic V2+ to get the dict representation
            # mode='json' ensures date/datetime are json serializable
            schema_dict_for_preview = schema_object.model_dump(mode='json')

            # --- Display Logic ---
            st.write(
                f"**Schema Name:** {schema_dict_for_preview.get('name', 'N/A')}"
            )
            st.write(
                f"**Description:** {schema_dict_for_preview.get('description', 'N/A')}"
            )
            st.markdown("---")

            if (
                "fields" in schema_dict_for_preview
                and schema_dict_for_preview["fields"]
            ):
                schema_data = []
                for field_name, field_config in schema_dict_for_preview[
                    "fields"
                ].items():
                    schema_data.append(
                        {
                            "Field": field_name,
                            "Type": field_config.get("type", "string"),
                            "Required": (
                                "✅" if field_config.get("required", True) else "❌"
                            ),
                            "Constraints": get_constraints_text(field_config),
                        }
                    )

                schema_df = pd.DataFrame(schema_data)
                st.dataframe(
                    schema_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Field": st.column_config.TextColumn(
                            "Field", width="medium"
                        ),
                        "Type": st.column_config.TextColumn("Type", width="small"),
                        "Required": st.column_config.TextColumn(
                            "Required", width="small"
                        ),
                        "Constraints": st.column_config.TextColumn(
                            "Constraints", width="large"
                        ),
                    },
                )

                # Quick actions (Download Template / Copy Schema JSON)
                col_a, col_b = st.columns(2)
                with col_a:
                    download_template(schema_object)

                with col_b:
                    copy_schema_json(schema_dict_for_preview)

            else:
                st.warning("No fields defined in the schema.")

        else:
            st.error(f"Could not retrieve schema '{selected_schema_name_lower}' for preview.")


    # Generation button
    st.divider()
    generate_btn = st.button(
        "🎲 Generate Data",
        type="primary",
        use_container_width=True,
        help="Click to generate data with current settings",
        key="generator_generate_btn" # Add a unique key
    )

    if generate_btn:
        # Check if a schema object is actually loaded
        if not schema_object:
            st.error("Please select a valid schema before generating data.")
        else:
            # Only include error types if not generating clean data
            error_types_config = None
            if not generate_clean:
                error_types_config = {
                    "missing_values": missing_values,
                    "invalid_format": invalid_format,
                    "out_of_range": out_of_range,
                    "duplicate": duplicates,
                    "inconsistent": inconsistent,
                }

            # Pass the schema object directly instead of the name
            generate_data(
                schema_object, num_records, dirty_ratio, error_types_config, target_field
            )

    # Export section
    # Access generated_data from session state
    if st.session_state.generated_data is not None:
        df = st.session_state.generated_data

        st.subheader("💾 Export Options")

        # Export format selection
        export_formats = st.multiselect(
            "Select export formats",
            ["CSV", "Excel", "JSON", "Parquet"],
            default=st.session_state.get(
                "last_export_formats", ["CSV"]
            ),  # Remember last value
            key="generator_export_formats_select", # Add a unique key
        )
        st.session_state.last_export_formats = export_formats  # Store for next rerun

        # Export settings
        col1, col2 = st.columns(2)

        with col1:
            include_index = st.checkbox(
                "Include row index",
                value=st.session_state.get("last_include_index", False),
                key="generator_include_index", # Add a unique key
            )
            st.session_state.last_include_index = include_index
            # compress_files = st.checkbox("Compress files", value=False) # Compression is often format-specific and handled by the library

        with col2:
            custom_filename = st.text_input(
                "Custom filename (optional)",
                value=st.session_state.get("last_custom_filename", ""),
                key="generator_custom_filename", # Add a unique key
            )
            st.session_state.last_custom_filename = custom_filename
            date_suffix = st.checkbox(
                "Add timestamp suffix",
                value=st.session_state.get("last_date_suffix", True),
                key="generator_date_suffix", # Add a unique key
            )
            st.session_state.last_date_suffix = date_suffix

        # Generate download buttons
        st.subheader("📥 Download Files")

        if not export_formats:
            st.info(
                "Select at least one export format above to enable download buttons."
            )
        else:
            try:
                base_name = custom_filename or st.session_state.selected_schema_name or "generated_data" # Use schema name as default filename

                if date_suffix:
                    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = f"{base_name}_{date_str}"

                # Create a container for buttons to handle dynamic columns better
                num_cols_for_buttons = min(len(export_formats), 4)
                btn_container = st.container()
                download_cols = btn_container.columns(num_cols_for_buttons)

                # Distribute buttons across columns
                for i, fmt in enumerate(export_formats):
                    current_col = download_cols[
                        i % num_cols_for_buttons
                    ]  # Cycle through columns

                    # Use a try block for each format download button
                    try:
                        with current_col:
                            # Ensure a unique key for each download button based on format and base_name
                            download_key = f"dl_{fmt.lower()}_{base_name}"
                            if fmt == "CSV":
                                csv_data = df.to_csv(index=include_index).encode(
                                    "utf-8"
                                )
                                st.download_button(
                                    "📄 CSV",
                                    csv_data,
                                    f"{base_name}.csv",
                                    "text/csv",
                                    key=download_key,
                                    use_container_width=True,
                                )

                            elif fmt == "Excel":
                                buffer = io.BytesIO()
                                df.to_excel(
                                    buffer, index=include_index, engine="xlsxwriter"
                                )
                                buffer.seek(0)
                                st.download_button(
                                    "📊 Excel",
                                    buffer,
                                    f"{base_name}.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=download_key,
                                    use_container_width=True,
                                )

                            elif fmt == "JSON":
                                json_data = df.to_json(
                                    orient="records", indent=2
                                ).encode("utf-8")
                                st.download_button(
                                    "🔧 JSON",
                                    json_data,
                                    f"{base_name}.json",
                                    "application/json",
                                    key=download_key,
                                    use_container_width=True,
                                )

                            elif fmt == "Parquet":
                                parquet_data = df.to_parquet(index=include_index)
                                st.download_button(
                                    "📦 Parquet",
                                    parquet_data,
                                    f"{base_name}.parquet",
                                    "application/octet-stream",
                                    key=download_key,
                                    use_container_width=True,
                                )

                    except Exception as e:
                        current_col.error(f"Export Error ({fmt}): {str(e)}")

            except Exception as e:
                st.error(f"Error setting up export options: {str(e)}")
                st.exception(e)

    else:
        st.info("Generate data first to see export options")