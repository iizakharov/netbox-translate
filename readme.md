# nb-translate.py - A simple script that helps you create translations for Netbox
## Description
This script translate netbox-community/netbox to the russian language

test.py - main script

fields.dict - phrases from models .py files
phrases.dict - phrases from all .py files, for verbose_name, help_text and other params 
html.dict - all phrases from html templates
class.dict - phrases from models files only for Classes

For generating dictionaries files use method generate_dictionary_file

## Usage
```bash
python3 test.py
```
## Dependences
python3, lxml, re

## Warning
The main goal is to show that NetBox can be translated, but this script may break the database. Please don't use it under production environments!
## License
This software is licensed under LGPLv2+.