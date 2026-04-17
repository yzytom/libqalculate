import os
import sys

def generate_definitions(data_dir, output_file):
    files = [
        ("currencies.xml", "currencies_xml"),
        ("datasets.xml", "datasets_xml"),
        ("elements.xml", "elements_xml"),
        ("eurofxref-daily.xml", "eurofxref_daily_xml"),
        ("functions.xml", "functions_xml"),
        ("planets.xml", "planets_xml"),
        ("prefixes.xml", "prefixes_xml"),
        ("units.xml", "units_xml"),
        ("variables.xml", "variables_xml"),
        ("rates.json", "rates_json"),
    ]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('#include <libqalculate/definitions.h>\n\n')
        f.write('const char * definitions_gresource_xml = nullptr;\n\n')
        
        for filename, varname in files:
            filepath = os.path.join(data_dir, filename)
            # Try .xml.in if .xml doesn't exist
            if not os.path.exists(filepath):
                filepath_in = filepath + ".in"
                if os.path.exists(filepath_in):
                    filepath = filepath_in
            
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as data_f:
                    content = data_f.read()
                
                # Escape the content for C++
                escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
                f.write(f'const char * {varname} = "{escaped_content}";\n\n')
            else:
                f.write(f'const char * {varname} = nullptr;\n\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_definitions.py <data_dir> <output_file>")
        sys.exit(1)
    generate_definitions(sys.argv[1], sys.argv[2])
