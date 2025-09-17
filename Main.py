from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from pyairtable import Api
from config import API_KEY, BASE_ID, TABLE_NAME
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_airtable_data():
    """Fetch data from Airtable with proper error handling"""
    try:
        logger.info(f"Attempting to connect to Airtable base: {BASE_ID}")
        logger.info(f"Table name: {TABLE_NAME}")
        
        api = Api(API_KEY)
        table = api.table(BASE_ID, TABLE_NAME)
        
        # Try to fetch records
        records = table.all()
        logger.info(f"Successfully fetched {len(records)} records")
        
        # Transform data - use "id" not "Record id"
        data = [{"id": r["id"], **r["fields"]} for r in records]
        return data, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error fetching Airtable data: {error_msg}")
        
        # Provide specific error messages based on the error type
        if "403" in error_msg:
            user_error = "Access denied. Please check your API token permissions, base ID, and table name."
        elif "401" in error_msg:
            user_error = "Authentication failed. Please check your API token."
        elif "404" in error_msg:
            user_error = "Base or table not found. Please verify your base ID and table name."
        else:
            user_error = f"Unexpected error: {error_msg}"
            
        return None, user_error

@app.route("/")
def index():
    data, error = get_airtable_data()
    
    if error:
        # Return error page or message
        return f"""
        <h1>Error Loading Data</h1>
        <p>{error}</p>
        <h2>Troubleshooting Steps:</h2>
        <ul>
            <li>Verify your Airtable API token has the correct permissions</li>
            <li>Check that the base ID is correct: {BASE_ID}</li>
            <li>Check that the table name is correct: {TABLE_NAME}</li>
            <li>Ensure the token has read access to the base and table</li>
        </ul>
        """, 500
    
    return render_template("table.html", data=data)

@app.route("/edit", methods=["POST"])
def edit_record():
    """Handle form submission to update Airtable record"""
    try:
        # Get form data
        record_id = request.form.get("id")
        patient_name = request.form.get("Patient Name")
        pharmacy = request.form.get("Pharmacy")
        status = request.form.get("Status")
        dob = request.form.get("DOB")
        
        # Validate required fields
        if not record_id:
            flash("Record ID is required", "error")
            return redirect(url_for("index"))
        
        # Connect to Airtable
        api = Api(API_KEY)
        table = api.table(BASE_ID, TABLE_NAME)
        
        # Prepare update data (only include non-empty fields)
        update_fields = {}
        if patient_name:
            update_fields["Patient Name"] = patient_name
        if pharmacy:
            update_fields["Pharmacy"] = pharmacy
        if status:
            update_fields["Status"] = status
        if dob:
            update_fields["DOB"] = dob
            
        if not update_fields:
            flash("At least one field must be provided for update", "error")
            return redirect(url_for("index"))
        
        # Update the record
        updated_record = table.update(record_id, update_fields)
        logger.info(f"Successfully updated record {record_id}")
        flash(f"Record {record_id} updated successfully!", "success")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error updating record: {error_msg}")
        
        if "404" in error_msg:
            flash("Record not found. Please check the ID.", "error")
        elif "403" in error_msg:
            flash("Permission denied. Check your API token permissions.", "error")
        elif "422" in error_msg:
            flash("Invalid data format. Please check your input.", "error")
        else:
            flash(f"Update failed: {error_msg}", "error")
    
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add_record():
    """Handle form submission to create new Airtable record"""
    try:
        # Get form data
        patient_name = request.form.get("Patient Name")
        pharmacy = request.form.get("Pharmacy")
        status = request.form.get("Status")
        dob = request.form.get("DOB")
        
        # Validate required fields
        if not all([patient_name, pharmacy, status, dob]):
            flash("All fields are required for creating a new record", "error")
            return redirect(url_for("index"))
        
        # Connect to Airtable
        api = Api(API_KEY)
        table = api.table(BASE_ID, TABLE_NAME)
        
        # Prepare new record data
        new_record_fields = {
            "Patient Name": patient_name,
            "Pharmacy": pharmacy,
            "Status": status,
            "DOB": dob
        }
        
        # Create the record
        created_record = table.create(new_record_fields)
        record_id = created_record["id"]
        logger.info(f"Successfully created record {record_id}")
        flash(f"New record created successfully! ID: {record_id}", "success")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating record: {error_msg}")
        
        if "403" in error_msg:
            flash("Permission denied. Check your API token permissions.", "error")
        elif "422" in error_msg:
            flash("Invalid data format. Please check your input.", "error")
        else:
            flash(f"Creation failed: {error_msg}", "error")
    
    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_record():
    """Handle form submission to delete Airtable record"""
    try:
        # Get form data
        record_id = request.form.get("id")
        
        # Validate required fields
        if not record_id:
            flash("Record ID is required for deletion", "error")
            return redirect(url_for("index"))
        
        # Connect to Airtable
        api = Api(API_KEY)
        table = api.table(BASE_ID, TABLE_NAME)
        
        # Delete the record
        deleted_record = table.delete(record_id)
        logger.info(f"Successfully deleted record {record_id}")
        flash(f"Record {record_id} deleted successfully!", "success")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting record: {error_msg}")
        
        if "404" in error_msg:
            flash("Record not found. Please check the ID.", "error")
        elif "403" in error_msg:
            flash("Permission denied. Check your API token permissions.", "error")
        else:
            flash(f"Deletion failed: {error_msg}", "error")
    
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
