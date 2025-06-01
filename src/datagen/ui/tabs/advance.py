"""
Streamlit UI for the Advanced tab.
Handles custom schema import and application settings.
"""

import streamlit as st
import pandas as pd # Only needed for dataframe display in debug info
import json
import time
from typing import Dict, Any # Needed for create_data_schema_from_dict signature

# Import core datagen components needed for schema management and validation
from datagen.core.schema import SchemaManager, DataSchema # SchemaManager and DataSchema are needed


# Helper function used only within the advanced tab logic (specifically schema import)
def create_data_schema_from_dict(schema_dict: Dict[str, Any]) -> DataSchema:
    """Create DataSchema object from a dictionary definition (parsed JSON)"""
    # Pydantic validation handles a lot, but let's do a basic check first
    if (
        not isinstance(schema_dict, dict)
        or "name" not in schema_dict
        or "description" not in schema_dict
        or "fields" not in schema_dict
        or not isinstance(schema_dict["fields"], dict)
    ):
        raise ValueError(
            "Invalid schema dictionary structure. Ensure it contains 'name' (string), "
            "'description' (string), and 'fields' (a dictionary of field definitions)."
        )

    # Use Pydantic's validation directly by passing the dict to the model constructor
    # Pydantic will raise a ValidationError if the structure or types within are wrong
    try:
        # Pydantic V2+ uses **schema_dict to unpack
        schema = DataSchema(**schema_dict)
        if not schema.fields:
             raise ValueError("The schema 'fields' dictionary is empty or contains no valid field definitions.")
        return schema
    except Exception as e:
        # Catch Pydantic validation errors or other issues during object creation
        raise ValueError(f"Failed to create DataSchema object from dictionary: {e}") from e


# --- Main function for the Advanced Tab UI ---
def advanced_tab():
    """Advanced settings and schema import UI layout"""
    st.subheader("⚙️ Advanced Settings")

    # Custom Schema Import
    st.subheader("🔧 Import Custom Schema (JSON)")

    st.markdown(
        "Import your custom data schema definition in JSON format. See the **Help** tab for a template and guide."
    )

    # File uploader
    json_file = st.file_uploader(
        "Upload JSON Schema File", type=["json"], key="advanced_json_uploader"
    )

    # Or text area for pasting JSON
    json_text = st.text_area(
        "Or paste JSON Schema here", height=300, key="advanced_json_text"
    )

    # Use columns for Load and Clear buttons
    col1, col2 = st.columns(2)

    load_schema_btn = col1.button("⬆️ Load Schema", type="primary", key="advanced_load_schema_btn")
    # Enable Clear button only if there's an imported schema in session state
    clear_schema_btn = col2.button("🗑️ Clear Imported Schema", key="advanced_clear_schema_btn", disabled=st.session_state.get("imported_schema_dict") is None)


    if load_schema_btn:
        schema_dict = None
        source = None
        if json_file:
            try:
                # Decode bytes to string before json.load
                json_string = json_file.getvalue().decode("utf-8")
                schema_dict = json.loads(json_string)
                source = "file"
                st.success("✅ JSON file uploaded and parsed successfully.")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format in the uploaded file.")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.exception(e)

        elif json_text.strip():
            try:
                schema_dict = json.loads(json_text)
                source = "text"
                st.success("✅ JSON text parsed successfully.")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format in the text area.")

        if schema_dict:
            try:
                # Attempt to create the DataSchema object to validate structure and types
                # Use the helper function defined above
                validated_schema_object = create_data_schema_from_dict(schema_dict)

                # Get the SchemaManager singleton
                schema_manager = SchemaManager()

                # Use the name from the validated schema object (Pydantic will handle default if needed)
                schema_name_lower = validated_schema_object.name.lower()

                # Check if a schema with this name already exists and is not the currently imported one (if any)
                # Check against manager's list of schemas, not just session state
                existing_schema = schema_manager.get_schema(schema_name_lower)
                if existing_schema and st.session_state.get("imported_schema_dict"):
                    # Check if the name matches the *currently loaded* imported schema
                    current_imported_name = st.session_state["imported_schema_dict"].get("name", "").lower()
                    if schema_name_lower != current_imported_name:
                         st.warning(f"Schema with name '{validated_schema_object.name}' already exists. Importing will replace it.")
                elif existing_schema:
                     st.warning(f"Schema with name '{validated_schema_object.name}' already exists. Importing will replace it.")


                # Add the validated schema object to the SchemaManager
                schema_manager.add_schema(validated_schema_object)

                with st.spinner("Đang cập nhật schema..."):

                    # Store the dictionary representation in session state for display purposes
                    st.session_state.imported_schema_dict = schema_dict # Store the original dict for display

                    # Optional: Auto-select the newly imported schema in the generator tab
                    st.session_state.selected_schema_name = schema_name_lower

                    # Dội một chút
                    time.sleep(1.5)  # ngủ 1.5 giây

                    # Rerun sau đó
                    st.rerun()
                st.success(
                    f"✅ Custom schema '{validated_schema_object.name}' validated and loaded into SchemaManager!"
                )

                # Rerun to update the schema selectbox immediately (Generator tab)
                st.rerun()


            except ValueError as e:
                st.error(f"❌ Schema validation failed: {str(e)}")
                st.session_state.imported_schema_dict = None  # Clear invalid schema
            except Exception as e:
                st.error(
                    f"❌ An unexpected error occurred during schema processing: {str(e)}"
                )
                st.exception(e)
                st.session_state.imported_schema_dict = None

        elif not json_file and not json_text.strip():
            st.warning("Please upload a JSON file or paste JSON text to load a schema.")

    # Logic for clearing imported schema
    # Use clear_schema_btn from above
    if clear_schema_btn and st.session_state.get("imported_schema_dict"):
        try:
            # Get the name from the dict currently in session state
            schema_name_to_remove = st.session_state["imported_schema_dict"].get("name", "").lower()
            if schema_name_to_remove:
                schema_manager = SchemaManager()
                # Check if the schema exists in the manager before trying to remove
                if schema_manager.get_schema(schema_name_to_remove):
                    schema_manager.remove_schema(schema_name_to_remove)
                    st.success(f"Schema '{schema_name_to_remove.capitalize()}' removed from manager.")
                else:
                    # This case might happen if the app was reloaded or manager state was lost,
                    # but session state still has the old dict.
                    st.warning(f"Schema '{schema_name_to_remove.capitalize()}' not found in manager, but cleared from session state.")

            else:
                 st.warning("Cannot determine the name of the imported schema to remove.")

            with st.spinner("Đang cập nhật schema..."):

                st.session_state.imported_schema_dict = None # Clear the stored dict
                # If the cleared schema was the currently selected one, reset selection
                if st.session_state.get("selected_schema_name") == schema_name_to_remove:
                    st.session_state.selected_schema_name = None

                # Dội một chút
                time.sleep(1.5)  # ngủ 1.5 giây

                # Rerun sau đó
                st.rerun()

        except ValueError as e:
             st.error(f"Error removing schema: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred while clearing schema: {str(e)}")
            st.exception(e)



    # Display currently imported schema definition if exists in state
    # Access imported_schema_dict from session state
    if st.session_state.get("imported_schema_dict"):
        st.markdown("---")
        st.subheader("Current Imported Schema Definition")
        st.json(st.session_state.imported_schema_dict, expanded=False)


    st.markdown("---")

    # Settings section
    st.divider()
    st.subheader("🔧 Application Settings")

    # Performance settings
    with st.expander(
        "⚡ Performance Settings",
        expanded=st.session_state.get("last_perf_expanded", False), # Remember state
    ):
        st.session_state.last_perf_expanded = True # Set expanded state when clicked

        # Store max_display_rows directly in session_state with a key
        max_display_rows = st.number_input(
            "Max rows to display in preview tables (Generator, Analysis)",
            min_value=10,
            max_value=5000, # Increased max for potentially larger dataframes
            value=st.session_state.get("perf_max_rows", 100),  # Remember value
            step=10,
            key="perf_max_rows",  # Store directly in session_state
            help="Sets the maximum number of rows shown in the quick preview and data preview tables.",
        )
        # No need to explicitly store in state here, key handles it.

        enable_caching = st.checkbox(
            "Enable data caching (Future)",
            value=st.session_state.get("last_caching_enabled", True),  # Remember state
            help="Cache generated data for better performance (Feature coming soon)",
            disabled=True,  # Disable checkbox as caching isn't implemented yet
            key="perf_caching",
        )
        st.session_state.last_caching_enabled = enable_caching


    # Debug information
    with st.expander(
        "🐛 Debug Information",
        expanded=st.session_state.get("last_debug_expanded", False), # Remember state
    ):
        st.session_state.last_debug_expanded = True # Set expanded state when clicked

        # Access generated_data from session state
        if st.session_state.get("generated_data") is not None:
            df = st.session_state.generated_data
            st.write("**Data Info:**")
            st.write(f"- Shape: {df.shape}")
            # Calculate memory usage carefully to avoid errors on empty/malformed DFs
            try:
                mem_usage_mb = df.memory_usage(deep=True).sum() / 1024**2
                st.write(
                    f"- Memory usage: {mem_usage_mb:.2f} MB"
                )
            except Exception as mem_err:
                 st.write(f"- Memory usage: Could not calculate ({mem_err})")

            st.write(f"- Data types:\n")
            if not df.empty:
                dtypes_df = df.dtypes.reset_index()
                dtypes_df.columns = ["Column", "DataType"]
                st.dataframe(dtypes_df, hide_index=True, use_container_width=True)
            else:
                st.info("DataFrame is empty, no data types.")
        else:
            st.info("No data generated yet.")

        st.markdown("---")
        st.write("**Session State (Summary):**")
        # Create a copy to modify for display
        session_state_display = {k: v for k, v in st.session_state.items()}
        # Summarize large objects
        if "generated_data" in session_state_display and isinstance(session_state_display["generated_data"], pd.DataFrame):
            df_summary = session_state_display["generated_data"]
            try:
                 mem_usage_mb = df_summary.memory_usage(deep=True).sum() / 1024**2
                 session_state_display["generated_data"] = (
                    f"DataFrame (Shape: {df_summary.shape}, Memory: {mem_usage_mb:.2f} MB)"
                 )
            except:
                  session_state_display["generated_data"] = (
                    f"DataFrame (Shape: {df_summary.shape}, Memory: Error calculating)"
                 )

        if "imported_schema_dict" in session_state_display and isinstance(session_state_display["imported_schema_dict"], dict):
             # Display structure/name instead of full dict if large
             imported_dict = session_state_display["imported_schema_dict"]
             session_state_display["imported_schema_dict_summary"] = {
                 "name": imported_dict.get("name", "N/A"),
                 "fields_count": len(imported_dict.get("fields", {}))
             }
             # Remove the potentially large original dict from the summary display
             del session_state_display["imported_schema_dict"]


        st.json(session_state_display, expanded=False)

        st.markdown("---")
        st.write("**SchemaManager State (via Singleton):**")
        try:
            manager = SchemaManager()
            st.write(f"- Manager ID: {id(manager)}")
            st.write(f"- Loaded Schemas: {manager.list_schemas()}")
            # Optionally display details of schemas in the manager (can be verbose)
            # st.write("- Schema Details:")
            # for name in manager.list_schemas():
            #     schema = manager.get_schema(name)
            #     if schema: # Check if schema object is valid
            #        st.write(f"  - {schema.name}: {len(schema.fields)} fields")
        except Exception as e:
            st.error(f"Could not access SchemaManager state: {e}")