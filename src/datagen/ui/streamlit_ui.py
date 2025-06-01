"""
Streamlit UI for Data Generator - Integrated with Singleton SchemaManager
"""

import streamlit as st

# Import the tab functions from the separate files
# Assuming the directory structure is datagen/ui/tabs
from datagen.ui.tabs.helps import help_tab
from datagen.ui.tabs.generator import generator_tab
from datagen.ui.tabs.data_quality import data_quality_tab
from datagen.ui.tabs.analysis import analysis_tab
from datagen.ui.tabs.advance import advanced_tab

DATAGEN_AVAILABLE = True

def main():
    st.set_page_config(
        page_title="Data Generator Pro",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Check if datagen is available before proceeding
    if not DATAGEN_AVAILABLE:
        st.stop()  # Stop the script if the package isn't found

    # Initialize session state variables if they don't exist
    # Keep all session state initialization here in the main app.py
    # This ensures state is consistently available to all tabs on every rerun
    if "generated_data" not in st.session_state:
        st.session_state.generated_data = None
    # Stores the *name* of the currently selected schema
    if "selected_schema_name" not in st.session_state:
        st.session_state.selected_schema_name = None
    # Stores the parsed custom schema dictionary from JSON import (for display in Advanced tab)
    if "imported_schema_dict" not in st.session_state:
        st.session_state.imported_schema_dict = None
    # Remember configuration values across reruns (optional but good UX)
    if "last_num_records" not in st.session_state:
         st.session_state.last_num_records = 100
    if "last_generate_clean" not in st.session_state:
         st.session_state.last_generate_clean = False
    if "last_dirty_ratio" not in st.session_state:
         st.session_state.last_dirty_ratio = 10
    if "last_error_types_expanded" not in st.session_state:
         st.session_state.last_error_types_expanded = True
    if "last_missing_values" not in st.session_state:
         st.session_state.last_missing_values = True
    if "last_invalid_format" not in st.session_state:
         st.session_state.last_invalid_format = True
    if "last_out_of_range" not in st.session_state:
         st.session_state.last_out_of_range = False
    if "last_duplicates" not in st.session_state:
         st.session_state.last_duplicates = False
    if "last_inconsistent" not in st.session_state:
         st.session_state.last_inconsistent = False
    if "last_target_field_enabled" not in st.session_state:
         st.session_state.last_target_field_enabled = False
    if "last_target_fields" not in st.session_state:
         st.session_state.last_target_fields = []
    if "last_export_formats" not in st.session_state:
         st.session_state.last_export_formats = ["CSV"]
    if "last_include_index" not in st.session_state:
         st.session_state.last_include_index = False
    if "last_custom_filename" not in st.session_state:
         st.session_state.last_custom_filename = ""
    if "last_date_suffix" not in st.session_state:
         st.session_state.last_date_suffix = True
    if "perf_max_rows" not in st.session_state:
         st.session_state.perf_max_rows = 100
    if "last_perf_expanded" not in st.session_state:
         st.session_state.last_perf_expanded = False
    if "last_caching_enabled" not in st.session_state:
         st.session_state.last_caching_enabled = True # Although disabled, remember state
    if "last_debug_expanded" not in st.session_state:
         st.session_state.last_debug_expanded = False
    if "last_show_rows" not in st.session_state:
         st.session_state.last_show_rows = 20 # For preview table
    if "last_show_only_errors" not in st.session_state:
         st.session_state.last_show_only_errors = False


    st.title("🎲 Data Generator Pro")
    st.markdown(
        "**Công cụ sinh dữ liệu mẫu chuyên nghiệp với khả năng tạo dữ liệu sạch và dữ liệu lỗi**"
    )

    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🏠 Generator", "📊 Data Quality", "🔍 Analysis", "⚙️ Advanced", "❓ Help"]
    )

    # Call the imported tab functions within their respective tabs
    with tab1:
        generator_tab() # Call function from datagen.ui.tabs.generator_tab

    with tab2:
        data_quality_tab() # Call function from datagen.ui.tabs.data_quality_tab

    with tab3:
        analysis_tab() # Call function from datagen.ui.tabs.analysis_tab

    with tab4:
        advanced_tab() # Call function from datagen.ui.tabs.advanced_tab

    with tab5:
        help_tab() # Call function from datagen.ui.tabs.help


# Entry point
if __name__ == "__main__":
    main()