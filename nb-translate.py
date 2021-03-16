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


def getVersion(project):
    """
    Get the version number from GitHub
    """
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


def get_files(directory_name):
    """
    Create a list of the files for translating
    """
    fl = []
    for root, dirs, files in os.walk(directory_name, topdown=False):
        for name in files:
            fl.append(os.path.join(root, name))
    return fl


def copy_files(source_file, source_dir, copy_dir):
    """
    Copy source directory into new translate directory
    """
    nf = source_file.replace(source_dir, copy_dir)
    os.makedirs(os.path.dirname(nf), exist_ok=True)
    copyfile(source_file, nf)


def add_verbose_name_if_not_exist(file):
    """
    Скрипт принудительного создании имени класса
    Add verbose_name to class Meta if not exist
    :param file: path ro file
    :return: edited file
    """
    reg = re.compile('[A-Z]\w+(?=\()')
    class_reg = re.compile('^class (?=[A-Z])')
    plural_reg = re.compile('(?!=[\"\'])[A-Za-z]\w+(?=[\'\"])')
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if ('class ' in data[i]) & (not ('Meta' in data[i])) & (not (class_reg.search(data[i]) == None)):
                names = reg.search(data[i])
                class_name = names.group()
                x = re.findall('[A-Z][^A-Z]+', class_name)
                class_name = ' '.join(x)
            if 'class Meta:' in data[i]:
                try:
                    flag = 0
                    for j in data[i:i + 4]:
                        if 'verbose_name' in j and flag != 2:
                            flag = 1
                            verbose_plural = plural_reg.search(j)
                            verbose_plural = verbose_plural.group()
                        if 'verbose_name_plural' in j:
                            flag = 2
                    if flag == 0:
                        data[i] += f'\n        verbose_name = "{class_name}"\n' \
                                   f'        verbose_name_plural = "{class_name}s"\n'
                    elif flag == 1:
                        data[i + 2] += f'        verbose_name_plural = "{verbose_plural}s"\n'

                except Exception as E:
                    print('add_verbouse_name_if_not_exist EXCEPTION')
                    print(E)
                    print(file)
                    print(data[i])
            elif 'class MPTTMeta:' in data[i]:
                flag = 0
                for j in data[i - 10:i]:
                    if 'class Meta:' in j:
                        flag += 1
                    if 'verbose_name' in j:
                        flag += 2
                if flag == 0:
                    data[i - 1] += f'    class Meta:\n' \
                                   f'        verbose_name = "{class_name}"\n' \
                                   f'        verbose_name_plural = "{class_name}s"\n\n'
                elif flag == 1:
                    data[i - 1] = f'        verbose_name = "{class_name}"\n' \
                                  f'        verbose_name_plural = "{class_name}s"\n' + data[i - 1] + '\n'

        with open(file, 'w+') as f1:
            f1.writelines(data)
    return


def set_rus_lang_in_settings(file):
    """
    :param file: file settings.py
    :return: file settings.py with LANGUAGE_CODE = 'ru'
    """
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if data[i] == "LANGUAGE_CODE = 'en-us'\n":
                data[i] = "LANGUAGE_CODE = 'ru'\n"
        with open(file, 'w+') as f1:
            f1.writelines(data)
    print('LANGUAGE SET TO "RUS" in settings')
    return


def search_form_translate(file):
    """
    :param file: /netbox/netbox/forms.py
    :return: /netbox/netbox/forms.py with RUS translate
    """
    search_data = 'translate_data/search_form.py'
    with open(search_data) as f:
        data = f.readlines()
        with open(file, 'w') as f1:
            f1.writelines(data)
    print('Search form - Done!')
    return


def hard_code_translate(file):
    """
    Hardcode translate html template
    """
    searchable = '                    {% block title %}{% if obj.pk %}Editing {{ obj_type }} {{ obj }}{% else %}Add a new {{ obj_type }}{% endif %}{% endblock %}'
    plugin = '                    {% block title %}{% if obj.pk %}Реадактирование {{ obj_type }} {{ obj }}{% else %}Создание {{ obj_type }}{% endif %}{% endblock %}\n'
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if searchable[19:] in data[i]:
                data[i] = plugin
        with open(file, 'w+') as f1:
            f1.writelines(data)
    return


def translate_titles(file):
    """
    Check title name in views.py and translate with dictionary "rus_dict"
    """
    rus_dict = {
        'Console Connections': "            'title': 'Консольные Соединения'\n",
        'Power Connections': "            'title': 'Силовые Соединения'\n",
        'Interface Connections': "            'title': 'Интерфейсные Соединения'\n"
    }
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if "'title': " in data[i]:
                for k, v in rus_dict.items():
                    if k in data[i]:
                        data[i] = v
                        break
        with open(file, 'w+') as f1:
            f1.writelines(data)


def generate_fields_patterns(fields):
    """
    Generate patterns for field name
    """
    gen_fields = {}
    for field in fields:
        gen_fields[field] = r'([ ]{,4}' + field + '\s?=\s?\w+\.?\w+\((\n*[ ]{5,8}[a-zA-Z0-9а-яА-Я_]*\s?=?\s?[a-zA-Z0-9а-яА-Я _\-,\.\'\"\(\)\[\]\\\/\+\{\}]*\n)*[ ]{,4}\))'
    return gen_fields


def get_all_fields_from_file(file):
    """
    Find all fields from file where variable is model field
    """
    all_fields = []
    row_fields = re.findall(r'\w+\s?=\s?models.\w+\(', file)
    for field in row_fields:
        filtered_field = re.match(r'^[^_]\w+', field)
        if filtered_field:
            filtered_field = filtered_field.group(0)
            if filtered_field not in all_fields:
                all_fields.append(filtered_field)
    return all_fields


def check_field_param(param, field_string):
    """
    Check the verbose_name or help_text in row field
    """
    if field_string and param:
        return bool(re.search(param, field_string))


def create_field_param(param_name, param_value, raw_string):
    """
    Create field param in mathes string row
    """
    #print('RAW: ' + raw_string)
    if param_name and param_value and raw_string:
        split_row = re.split(r'([ ]{,4}\w+\s?=\s?\w+\.?\w+\()((\n*[ ]{5,8}[a-zA-Z0-9а-яА-Я_]*\s?=?\s?[a-zA-Z0-9а-яА-Я _\-,\.\'\"\(\)\[\]\\\/\+\{\}]*\n)*[ ]{,4}\))', raw_string, maxsplit=1)

        if split_row:
            complete_row = split_row[1] + '\n        ' + param_name + ' = "' + param_value + '",' + split_row[2]
    return complete_row


def get_translated_field(field_name):
    """
    Get translated row from dictionary
    """
    return False


def get_dictionary(dict_file):
    """
    Get dictionary file and make
    """
    po_patterns = [
        r'msgid\s\"(.+)\"\nmsgstr\s\"(.+)\"',
    ]
    o = open(dict_file, 'r', encoding='utf8')
    c = o.read()
    for p in po_patterns:
        m = re.findall(p, c)
    o.close()
    d = dict(m)
    return d


def generate_dictionary_file(phrases, output_file):
    """
    Generate dictionary file. For output file use file_name.dict
    Main dictionaries:
    fields.dict - phrases from models .py files
    phrases.dict - phrases from all .py files, for verbose_name, help_text and other params
    html.dict - all phrases from html templates
    class.dict - phrases from models files only for Classes
    """
    dict_rows = ""
    for phrase in phrases:
        dict_rows += '\nmsgid "' + phrase + '"\nmsgstr  "' + phrase + '"\n'
    f_d = open(output_file, 'w+')
    f_d.write(dict_rows)
    f_d.close()


def get_all_classes_names(file):
    """
    Get all classes names from models
    """
    all_fields = []
    row_fields = re.findall(r'\w+\s?=\s?models.\w+\(', file)
    for field in row_fields:
        filtered_field = re.match(r'^[^_]\w+', field)
        if filtered_field:
            filtered_field = filtered_field.group(0)
            # print(filtered_field)
            if filtered_field not in all_fields:
                all_fields.append(filtered_field)
    return all_fields


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
    r'<input type=\"submit\".+value=\"\s?(\w+)\s?\"\s?/>',
    r'>\s?(\w+)\s?<span',
    r'<\/span>\s?([\w\s]+)\s?<span',
    r'<div class="panel-body text-muted">\s?([\w\s]+)<\/div>',
    r'(?!=</i>)([\sA-Z][A-Za-z]+)</button>'
]

phrases_patterns = [
    r'verbose_name\s?=\s?[\'\"](.+)[\'\"]',
    r'help_text\s?=\s?([\'\"](.+)[\'\"])',
    r'verbose_name_plural\s?=\s?[\'\"](.+)[\'\"]',
    r'label\s?=\s?[\'\"](.+)[\'\"]'
]

# set main variables
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
dict_html = get_dictionary('html.dict')

print(dict_phrases)

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
    if fe == '.html' and 'jquery-ui-' not in fn:
        o = open(f, 'r')
        c = o.read()
        for hp in html_patterns:
            matches = re.findall(hp, c)
            for m in matches:
                #print('---------HTML-PHRASES-FOR--------')
                #print(f)
                #print(m)
                if m not in all_phrases_from_html:
                    all_phrases_from_html.append(m)
        o.close()

#print(len(all_phrases_from_html))

'''
Translate files
'''
for f in files:
    if (os.path.basename(f) == 'models.py') or ('models' in os.path.dirname(f) and ('.py' in os.path.basename(f))):
        add_verbose_name_if_not_exist(f)
    elif os.path.basename(f) == 'settings.py':
        set_rus_lang_in_settings(f)
    elif os.path.basename(f) == 'object_edit.html':
        hard_code_translate(f)
    fn, fe = os.path.splitext(f)
    if '/netbox/netbox/forms' in f and fe == '.py':
        search_form_translate(f)
    elif 'netbox/dcim/views' in f and fe == '.py':
        translate_titles(f)
    if fe == '.py' and 'migrations' not in f:
        copy_files(f, source_dir, translate_dir)
        o = open(f, 'r')
        c = o.read()
        for pp in phrases_patterns:
            matches = re.finditer(pp, c)
            for m in matches:
                raw = m.group(0)
                if raw:
                    orig = re.findall(pp, raw)[0]
                    print('++++++++++++++++++++++++++++++++')
                    print(f)
                    print(pp)
                    print('++++++++++++++++++++++++++++++++')
                    print(orig)
                    print('++++++++++++++++++++++++++++++++')
                    tran = str(dict_phrases.get(orig)).replace('"', '\\"')
                    print(tran)
                    if dict_phrases.get(orig):
                        c = c.replace(raw, raw.replace(orig, tran))
        # for fields patterns
        if '/models/' in f or 'models.py' in f:
            fields = get_all_fields_from_file(c)
            pattern_fields = generate_fields_patterns(fields)
            for key in pattern_fields:
                matches = re.finditer(pattern_fields[key], c)
                for m in matches:
                    raw = m.group(0)
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
        nf = f.replace(source_dir, translate_dir)
        os.makedirs(os.path.dirname(nf), exist_ok=True)
        w = open(nf, 'w+')
        w.write(c)
        o.close()
        w.close()
    # for html patterns
    if fe == '.html' and 'jquery-ui-' not in fn:
        o = open(f, 'r')
        c = o.read()
        for hp in html_patterns:
            matches = re.finditer(hp, c)
            for m in matches:
                raw = m.group(0)
                if raw:
                    orig = re.findall(hp, raw)[0]
                    #print('++++++++++++++++++++++++++++++++')
                    #print(f)
                    #print(hp)
                    #print('++++++++++++++++++++++++++++++++')
                    #print(orig)
                    #print('++++++++++++++++++++++++++++++++')
                    tran = str(dict_html.get(orig)).replace('"', '\\"')
                    #print(tran)
                    if dict_html.get(orig):
                        c = c.replace(raw, raw.replace(orig, tran))
        nf = f.replace(source_dir, translate_dir)
        os.makedirs(os.path.dirname(nf), exist_ok=True)
        w = open(nf, 'w+')
        w.write(c)
        o.close()
        w.close()
