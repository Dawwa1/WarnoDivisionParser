import re
import json
import logging  # not necassary, but its pretty cool to have a log file

# Function to parse the descriptor blocks
def parse_descriptors(data):
    # Regex to match each descriptor block containing "Descriptor_Deck_Division_"
    pattern = r'(Descriptor_Deck_Division_\w+ is TDeckDivisionDescriptor\s*\(.*?\))(?=\nDescriptor_Deck_Division)'
    matches = re.findall(pattern, data, re.DOTALL)

    descriptors = {}
    for match in matches:
        lines: list = match.splitlines()
        
        descriptor_name = lines[0].split(' ')[0]
        descriptors[descriptor_name] = {}
        
        descriptor = descriptors[descriptor_name]
        
        pack_list = []

        for line in lines:
            line: str = line.strip()
            if "(~/" in line:
                pack_list.append(line)
            if "PackList" in line:
                descriptor["PackList"] = []
            elif ('=' in line) and ('[' in line):
                
                # Splits list string
                split_line = line.split('=')
                
                # Selects the element with list elements and splits each
                list_elements: list[str] = re.findall(r'\w+', split_line[1])
                
                # Makes a JSON array with all the values of list_elements
                descriptor[split_line[0]] = [i for i in list_elements]
                
            elif '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                value = value.strip('\'"')
                if value.startswith('GUID:'):
                    value = value.replace('GUID:', '').strip('{}')
                descriptor[key] = value

            descriptor["PackList"] = pack_list
            
    return descriptors
            

if __name__ == '__main__':
    try:
        path = r""  # Path to Divisions.ndf file

        with open(path, 'r') as f:
            data = f.read()

        parsed_data = parse_descriptors(data)
        
        # Write the data to a JSON file
        with open('descriptors.json', 'w') as json_file:
            json.dump(parsed_data, json_file, indent=4)

        print("Parsed data, written to 'descriptors.json' file.")
        
    except FileNotFoundError:
        print(f"File not found @ \"{path}\" | Please provide a valid path to the Divisions.ndf file.")
        
    except Exception as e:
        logging.basicConfig(filename='warno_parser.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
        logger = logging.getLogger(__name__)
        logger.error(e)
        print("An error occurred while parsing the data, please check the log file for more information.")
