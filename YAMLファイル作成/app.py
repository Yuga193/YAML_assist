from flask import Flask, render_template, request, redirect, url_for, Response, session
import yaml
import os
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = os.urandom(24)

yaml_data = {}

def generate_yaml(data):
    """Generate a yaml formatted string from a nested dictionary."""
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

def safe_int_conversion(value):
    """Try converting a value to an integer. If fails, return original value."""
    try:
        return int(value)
    except ValueError:
        return value

@app.route("/", methods=["GET", "POST"])
def index():
    global yaml_data
    yaml_data = {}
    
    if request.method == "POST":
        sections = request.form.getlist("section")
        keys = request.form.getlist("key")
        values = request.form.getlist("value")
        new_values = [int(value) for value in request.form.getlist("new_value")] 
        
        last_section = ""
        
        section_data = {}
        for section, key, value, new_value in zip(sections, keys, values, new_values):
            section = safe_int_conversion(section)  # Convert section name to int if possible
            key = safe_int_conversion(key)
            value = safe_int_conversion(value)

            if not section:
                section = last_section
            else:
                last_section = section

            if section not in section_data:
                section_data[section] = []

            section_data[section].append((key, value, new_value))

        for section, items in section_data.items():
            sorted_items = sorted(items, key=lambda x: x[2])
            yaml_data[section] = {item[0]: item[1] for item in sorted_items}

        sorted_sections = sorted(yaml_data.items(), key=lambda x: section_data[x[0]][0][2])
        yaml_data = dict(sorted_sections)

        session['generated_yaml'] = generate_yaml(yaml_data)
        filename = request.form["filename"] + ".yml"
        session['filename'] = filename

        return redirect(url_for("download"))

    return render_template('template_with_delete.html')

@app.route("/download", methods=["GET"])
def download():
    generated_yaml = session.get('generated_yaml', '')
    filename = session.get('filename', 'output.yml')
    filename_encoded = quote(filename) 
    response = Response(generated_yaml, content_type="text/yaml")
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename_encoded}"
    return response

if __name__ == "__main__":
    app.run(debug=True)
