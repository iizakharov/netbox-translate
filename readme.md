# translate.sh - A simple script that helps you create translations for Netbox
## Description
This script translate netbox-community/netbox to the russian language

translate.sh - run script
translate.py - main script
nbt_data - dicts, utils, reg-vocabulary
  fields.dict - phrases from models .py files
  phrases.dict - phrases from all .py files, for verbose_name, help_text and other params 
  html.dict - all phrases from html templates

## Usage
The contents of the nb-translator folder must be unpacked to the root folder "netbox" and run the script:

```bash
./translane.sh
```
Script clones the folder "netbox" in " netbox_old "( for the possibility of recovery) and translates to the contents of the folder " netbox"
## Dependences
python3, lxml, re

## Warning
The main goal is to show that NetBox can be translated, but this script may break the database. Please don't use it under production environments!
## License
This software is licensed under LGPLv2+.
