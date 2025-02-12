import os
import json
import zipfile
import vobject
import datetime

# Define input ZIP file
ZIP_FILE = "input/Contacts.zip"

# Extract .vcf files from ZIP
def extract_vcf_files(zip_path, extract_to="temp_contacts"):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    
    return [os.path.join(extract_to, f) for f in os.listdir(extract_to) if f.endswith(".vcf")]

# Convert vCard objects to JSON-serializable format
def parse_vcf(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        vcard = vobject.readOne(f.read())

    contact = {}

    # Extract all attributes
    for attr, values in vcard.contents.items():
        parsed_values = []

        for v in values:
            try:
                if attr == "tel":  # Handle multiple phone numbers correctly
                    tel_type = v.params.get("TYPE", ["other"])  # Extract type (mobile, home, work, etc.)
                    phone_number = str(v.value).strip()
                    parsed_values.append({"type": tel_type, "number": phone_number})
                else:
                    parsed_values.append(str(v.value))  # Convert all other attributes to string
            except AttributeError:
                parsed_values.append(str(v))  # Fallback

        # Special handling for phone numbers (always store as a list)
        if attr == "tel":
            contact[attr] = parsed_values  # Always a list
        else:
            contact[attr] = parsed_values if len(parsed_values) > 1 else parsed_values[0]

    return contact

# Save contacts to JSON file
def save_to_json(contacts):
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    output_json = f"output/apple_contacts_{timestamp}.json"

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4)

    print(f"Saved {len(contacts)} contacts to {output_json}")

# Process all .vcf files and save to JSON
def process_vcf_to_json(zip_file):
    vcf_files = extract_vcf_files(zip_file)
    contacts = [parse_vcf(file) for file in vcf_files]
    save_to_json(contacts)

# Run the script
if __name__ == "__main__":
    process_vcf_to_json(ZIP_FILE)