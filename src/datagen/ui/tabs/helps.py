import streamlit as st


def help_tab():
    """Help tab with instructions and schema template"""
    st.subheader("❓ Help & Documentation")

    st.markdown(
        """
    Welcome to Data Generator Pro! This tool helps you create realistic sample data,
    including clean data and data with intentional quality issues.

    Use the tabs above to navigate:
    *   **🏠 Generator:** Configure data generation settings and preview schemas.
    *   **📊 Data Quality:** Analyze the quality of generated data.
    *   **🔍 Analysis:** Explore the generated data with summary statistics and visualizations.
    *   **⚙️ Advanced:** Import custom schemas and export generated data.
    *   **❓ Help:** Find instructions and schema templates (this tab).
    """
    )

    st.markdown("---")
    st.subheader("Custom Schema Guide")

    st.markdown(
        """
    The **Advanced** tab allows you to import a custom schema using a JSON definition.
    When a valid JSON schema is imported, it is added to the internal schema manager
    and becomes available for selection in the **Generator** tab just like the predefined schemas.

    Your JSON schema must be a dictionary with the following top-level keys:

    *   `name` (string, **required**): A unique name for your schema (e.g., "MyUserData"). This name will appear in the selectbox.
    *   `description` (string, **required**): A brief description of the schema.
    *   `fields` (dictionary, **required**): A dictionary where keys are the field names (column names in the output data)
        and values are dictionaries defining each field's configuration.

    Each field configuration within the `fields` dictionary should contain:

    *   `type` (string, **required**): The data type/Faker provider name. Examples:
        `string`, `integer`, `float`, `boolean`, `date`, `email`, `phone_number`, `uuid`,
        `first_name`, `last_name`, `address`, `city`, `job_title`, `ipv4`, `date_of_birth`, etc.
        The available types correspond to [Faker providers](https://faker.readthedocs.io/en/master/providers.html).
        For simple cases or when a specific Faker provider isn't available or needed, use `string`, `integer`, `float`, `boolean`.
        Use `choice` type for categorical data with a predefined list of options.
    *   `required` (boolean, optional, default: `true`): If `false`, the field can have missing values introduced by the dirty data generator.
    *   `constraints` (dictionary, optional): Defines constraints or arguments for the field type/provider. The keys and values here depend entirely on the specific `type` and what arguments its corresponding Faker provider or custom generator accepts.
        *   For `integer`/`float`: `{"min_value": ..., "max_value": ...}`
        *   For `string` or text-based types that support length limits: `{"max_length": ...}`
        *   For `choice` type: `{"choices": ["Option1", "Option2", ... ]}`
        *   For `date_of_birth`: `{"minimum_age": ..., "maximum_age": ...}`
        *   For `date`/`datetime`: `{"start_date": "YYYY-MM-DD" or "-Nd" (N days ago)}`
        *   Other constraints/arguments might be supported depending on the specific `type` (Faker provider arguments).

    **Example JSON Schema Template:**
    """
    )

    json_template = """
{
  "name": "SampleUsers",
  "description": "A sample schema for user data with various types",
  "fields": {
    "user_id": {
      "type": "uuid",
      "required": true,
      "description": "Unique user identifier"
    },
    "username": {
      "type": "user_name",
      "required": true,
      "description": "Username"
    },
    "email": {
      "type": "email",
      "required": true,
      "description": "Email address",
      "constraints": {
         "domain": "example.com"
      }
    },
    "birth_date": {
      "type": "date",
      "required": false,
      "description": "User's date of birth",
      "constraints": {
        "minimum_age": 18,
        "maximum_age": 65
      }
    },
    "status": {
      "type": "choice",
      "required": true,
      "description": "User's status (categorical)",
      "constraints": {
        "choices": ["active", "inactive", "suspended"]
      }
    },
     "login_count": {
       "type": "integer",
       "required": true,
       "description": "Number of logins",
       "constraints": {
         "min_value": 0,
         "max_value": 1000
       }
     },
     "balance": {
        "type": "float",
        "required": true,
        "description": "Account balance",
        "constraints": {
            "min_value": 0.0,
            "max_value": 10000.0,
            "precision": 2
        }
     },
    "last_login_ip": {
      "type": "integer",
      "required": false,
      "description": "Last login IP address"
    },
    "registration_datetime": {
       "type": "date",
       "required": true,
       "description": "Registration timestamp"
    }
  }
}
    """
    st.code(json_template, language="json")

    st.markdown(
        """
    You can copy the template above, modify it, and then paste it into the text area
    or save it as a `.json` file to upload in the **Advanced** tab.

    Make sure your JSON is valid before importing.
    """
    )

    # Optional: Add a button to download the template JSON
    st.download_button(
        label="📥 Download JSON Schema Template",
        data=json_template.encode("utf-8"),  # Encode data
        file_name="custom_schema_template.json",
        mime="application/json",
        key="help_download_template" # Add unique key
    )

    st.markdown("---")
    st.subheader("Common Error Types")
    st.markdown(
        """
    In the **Generator** tab, you can introduce various error types into the generated data:

    *   **Missing Values:** Some fields will be left empty (set to `None` or equivalent).
    *   **Invalid Format:** Values may not match the expected format (e.g., wrong date string, non-numeric in a number field). *Note: The current implementation might represent these as `None`/`NaN` if generation fails due to incorrect type or constraint violation.*
    *   **Out of Range:** Numeric or date values fall outside defined constraints (`min_value`, `max_value`, age limits, etc.).
    *   **Duplicates:** Entire rows are duplicated.
    *   **Inconsistent:** Values across different fields in a row might be logically inconsistent (e.g., age and birth date don't match). *Note: This is harder to implement generally and might be limited in the current version.*

    The `Error Rate (%)` controls the *probability* that a record will have *at least one* selected error type applied to a field. When "Target specific field" is *not* enabled, errors are applied randomly across fields based on their compatibility with the error type. When "Target specific field" *is* enabled, errors are concentrated on the chosen field.
    """
    )
