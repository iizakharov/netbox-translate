#!/usr/bin/env python3

import json, os, re, sys, urllib, urllib.request, zipfile
import pprint
from lxml import etree
from pathlib import Path
from shutil import copyfile

'''
Validate if project name is supported
'''
projects = [
    'netbox-community/netbox',
]
project = 'netbox-community/netbox'
if project not in projects:
    print('This project name is not supported!')
    sys.exit(1)

'''
Get the version number from GitHub
'''


def getVersion(project):
    f = urllib.request.urlopen('https://github.com/' + project + '/releases/latest')
    c = f.read()
    html = etree.HTML(c)
    etree.tostring(html, pretty_print=True, method='html')
    values = html.xpath("//div[contains(@class,'label-latest')]/div/div/ul/li/a/span/text()")
    version = values[0]

    if version:
        return version
    else:
        url = urllib.request.urlopen("https://api.github.com/repos/netbox-community/netbox/releases/latest")
        data = json.loads(url.read().decode())
        version = data['tag_name']
        return version


versionString = getVersion(project)
version = versionString.replace('v', '')

print('Fetching the Netbox version', version)

'''
Download the zip file from GitHub and uncompress it
'''
fn = 'netbox-' + version + '.zip'
if not Path(fn).is_file():
    print('Downloading the ZIP file.')
    z = urllib.request.urlopen('https://github.com/netbox-community/netbox/archive/' + versionString + '.zip')
    c = z.read()
    f = open(fn, 'wb')
    f.write(c)
    f.close()
else:
    print('The ZIP file was already downloaded.')

dn = 'netbox-' + version
if not Path(dn).is_dir():
    print('Extracting the files.')
    f = zipfile.ZipFile(fn, 'r')
    f.extractall('.')
    f.close()
else:
    print('The files were already extracted.')

'''
Create a list of the files for translating
'''
def get_files(directory_name):
    fl = []
    for root, dirs, files in os.walk(directory_name, topdown=False):
        for name in files:
            fl.append(os.path.join(root, name))
    return fl


'''
Copy source directory into new translate directory
'''
def copy_files(source_file, source_dir, copy_dir):
    nf = source_file.replace(source_dir, copy_dir)
    os.makedirs(os.path.dirname(nf), exist_ok=True)
    copyfile(source_file, nf)


'''
Generate patterns for field name
'''
def generate_fields_patterns(fields):
    gen_fields = {}
    for field in fields:
        gen_fields[field] = r'([ ]{,4}' + field + '\s?=\s?\w+\.?\w+\((\n*[ ]{5,8}[a-zA-Z0-9а-яА-Я_]*\s?=?\s?[a-zA-Z0-9а-яА-Я _\-,\.\'\"\(\)\[\]\\\/\+\{\}]*\n)*[ ]{,4}\))'
        #print(gen_fields[field])
    return gen_fields


'''
Find all fields from file where variable is model field
'''
def get_all_fields_from_file(file):
    all_fields = []
    row_fields = re.findall(r'\w+\s?=\s?models.\w+\(', file)
    for field in row_fields:
        filtered_field = re.match(r'^[^_]\w+', field)
        if filtered_field:
            filtered_field = filtered_field.group(0)
            #print(filtered_field)
            if filtered_field not in all_fields:
                all_fields.append(filtered_field)
    return all_fields


'''
Check the verbose_name or help_text in row field
'''
def check_field_param(param, field_string):
    if field_string and param:
        return bool(re.search(param, field_string))


'''
Create field param in mathes string row
'''
def create_field_param(param_name, param_value, raw_string):
    #print('RAW: ' + raw_string)
    if param_name and param_value and raw_string:
        split_row = re.split(r'([ ]{,4}\w+\s?=\s?\w+\.?\w+\()((\n*[ ]{5,8}[a-zA-Z0-9а-яА-Я_]*\s?=?\s?[a-zA-Z0-9а-яА-Я _\-,\.\'\"\(\)\[\]\\\/\+\{\}]*\n)*[ ]{,4}\))', raw_string, maxsplit=1)

        if split_row:
            complete_row = split_row[1] + '\n        ' + param_name + ' = "' + param_value + '",' + split_row[2]
    return complete_row


'''
Get translated row from dictionary
'''
def get_translated_field(field_name):
    return False


'''
Get dictionary file and make
'''
def get_dictionary(dict_file):
    po_patterns = [
        r'msgid\s\"(.+)\"\nmsgstr\s\"(.+)\"',
    ]
    o = open(dict_file, 'r', encoding='utf8')
    c = o.read()
    for p in po_patterns:
        m = re.findall(p, c)
    d = dict(m)
    return d


'''
Generate dictionary file. For output file use file_name.dict
Main dictionaries:
fields.dict - phrases from models .py files 
phrases.dict - phrases from all .py files, for verbose_name, help_text and other params 
html.dict - all phrases from html templates 
class.dict - phrases from models files only for Classes
'''
def generate_dictionary_file(phrases, output_file):
    dict_rows = ""
    for phrase in phrases:
        dict_rows += '\nmsgid "' + phrase + '"\nmsgstr  "' + phrase + '"\n'
    f_d = open(output_file, 'w+')
    f_d.write(dict_rows)
    f_d.close()

'''
Set html patterns
'''
html_patterns = [
    r'<a\s.+?>\s?([^(\n|?:{{|<)].+?[^(?:}}|>|\n)])<\/a>',
    r'<th>\s?([^(\n|?:{{|<)].+?[^(?:}}|>)])</th>',
    r'<th\s.+?>\s?([^(\n|?:{{|<)].+?[^(?:}}|>)])</th>',
    r'<td>\s?([^(\n|?:{{|<|\")].+?[^(?:}}|>|\")])</td>',
    r'<td\s.+?>\s?([^(\n|?:{{|<|\")].+?[^(?:}}|>|\")])</td>',
    r'\splaceholder=\"(.+?)\"',
    r'\stitle=\"([^(?:\.ui\-icon\-|?:{{)].+?)\"',
    r'<p(?:\s.+)?>(?!{[{\%])(?!<a)(.+?[^>])(?!</a>)(?!}[\%}])<\/p>',
    r'<h\d(?:\s.+)?>(?!{[{\%])(?!<a)(.+?[^(?:</a>])(?!}[\%}])<\/h\d>',
    r'<button\s?.*?>(?!{{)(.+?[^>])(?!}})</button>',
    r'</span>\s+(.+?[^>])\n\s*?</button>',
    r'</span>\s+(.+?[^>])\n\s*?</a>',
    r'</i>\s+(.+?[^>])\n\s*?</div>',
    r'</i>\s*?(.+?[^>])\s*?</a>',
    r'<title\s?.*?>(?!{{)(.+?)(?!}})</title>',
    r'<label\s?.*?>(?!{{)(.+?)(?!}})</label>',
    r'<strong\s?.*?>(?!{{)(.+?[^>])(?!}})</strong>',
    r'<li(?:.+)?>(?!<a)(?!<span)(?!{{)(.+?[^>])(?!}})</li>',
]

# set variables
source_dir = dn
translate_dir = dn + '-translated'
all_fields_from_netbox = []
all_phrases_from_py = []
all_phrases_from_html = []

# get files
files = get_files(source_dir)

# get dictionaries
dict_fields = get_dictionary('fields.dict')
dict_phrases = get_dictionary('phrases.dict')


'''
Get phrases from verbose_name, help_text, verbose_name_plural, label
'''
for f in files:
    fn, fe = os.path.splitext(f)
    if fe == '.py' and not 'migrations' in f:
        # print(f)
        o = open(f, 'r')
        c = o.read()
        matches = re.findall(r'verbose_name.+|help_text.+|verbose_name_plural.+|label.+', c)
        # print(matches)
        for m in matches:
            m_ph = re.findall(r'[\'\"].+[\'\"]', m)
            for mp in m_ph:
                mp = mp.replace('\'', '')
                mp = mp.replace('\"', '')
                #print('---------PHRASES-FOR-"' + mp + '"-------')
                #print(f)
                #print(m)

                if mp not in all_phrases_from_py:
                    all_phrases_from_py.append(mp)
        o.close()

#print(all_phrases_from_py)

'''
Get phrases from html templates and html tags
'''
for f in files:
    fn, fe = os.path.splitext(f)
    if fe == '.html' and not 'jquery-ui-' in fn:
        o = open(f, 'r')
        c = o.read()
        for hp in html_patterns:
            matches = re.findall(hp, c)
            for m in matches:
                print('---------HTML-PHRASES-FOR--------')
                print(f)
                print(m)
                if m not in all_phrases_from_html:
                    all_phrases_from_html.append(m)
        o.close()

print(len(all_phrases_from_html))

'''
Translate files
'''
for f in files:
    fn, fe = os.path.splitext(f)
    if fe == '.py' and not 'migrations' in f:
        copy_files(f, source_dir, translate_dir)
        o = open(f, 'r')
        c = o.read()
        phrases = []
        fields = get_all_fields_from_file(c)
        #print(f)
        new_fields = get_all_fields_from_file(c)
        #print(new_fields)
        for flds in new_fields:
            if flds not in all_fields_from_netbox:
                all_fields_from_netbox.append(flds)
        pattern_fields = generate_fields_patterns(fields)
        for key in pattern_fields:
            matches = re.finditer(pattern_fields[key], c)
            for m in matches:
                raw = m.group(0)
                #print(m)
                if raw:
                    original_str = re.findall(pattern_fields[key], raw)[0][0]
                    #print('-------------------------------')
                    #print(f)
                    #print(pattern_fields[key])
                    #print('++++++++++++++++++++++++++++++++')
                    #print(original_str)
                    #print('++++++++++++++++++++++++++++++++')
                    #print(bool(re.search('verbose_name', original_str)))
                    if not check_field_param('verbose_name', original_str) and dict_fields.get(key):
                        new_str = create_field_param('verbose_name', dict_fields.get(key), original_str)
                        c = c.replace(raw, raw.replace(original_str, new_str))
                    # else
        nf = f.replace(source_dir, translate_dir)
        os.makedirs(os.path.dirname(nf), exist_ok=True)
        w = open(nf, 'w+')
        w.write(c)
        o.close()
        w.close()
    if fe == '.html' and not 'jquery-ui-' in fn:
        o = open(f, 'r')
        c = o.read()
        for hp in html_patterns:
            matches = re.findall(hp, c)


'''
Generate dictionary file
'''
#generate_dictionary_file(all_phrases_from_html, 'html.dict')