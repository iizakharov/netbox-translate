# nb-translate.py - A simple script that helps you create translations for Netbox
## Usage
```bash
nb-translate.py  <script_name>
nb-translate.py  <script_name> <translation_source>
```
## Example
```bash
bbl.py  netbox-community/netbox
bbl.py  netbox-community/netbox your_local_file.po
```
## Dependences
lxml

## Warning
The main goal is to show that NetBox can be translated, but this script may break the database. Please don't use it under production environments!
## License
This software is licensed under LGPLv2+.