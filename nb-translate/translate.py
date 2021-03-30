#!/usr/nbt_data/env python3

import json, os, re, sys, urllib, urllib.request, zipfile
import pprint
from lxml import etree
from pathlib import Path
from shutil import copyfile

from nbt_data.vocabulary import html_patterns, phrases_patterns
from nbt_data.utils import get_files, get_dictionary, add_verbose_name_if_not_exist, set_rus_lang_in_settings, \
    hard_code_translate, search_form_translate, translate_titles, copy_files, get_all_fields_from_file, \
    generate_fields_patterns, check_field_param, create_field_param, add_verb_name_to_field, add_label_to_field, \
    add_link_in_nav_menu

# set main variables
nb = 'netbox'
source_dir = nb
translate_dir = source_dir + '-translated'
all_fields_from_netbox = []
all_phrases_from_py = []
all_phrases_from_html = []

# get files
files = get_files(source_dir)

# get dictionaries
dict_fields = get_dictionary('nbt_data/dictionary/fields.dict')
dict_phrases = get_dictionary('nbt_data/dictionary/phrases.dict')
dict_html = get_dictionary('nbt_data/dictionary/html.dict')


'''
Get phrases from verbose_name, help_text, verbose_name_plural, label
'''
for f in files:
    fn, fe = os.path.splitext(f)
    if '/forms' in f and fe == '.py':
        add_label_to_field(f)
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

'''
Get phrases from html templates and html tags
'''
for f in files:
    fn, fe = os.path.splitext(f)
    if fe == '.html' and 'inc/nav_menu' in fn:
        add_link_in_nav_menu(f)
    if fe == '.html' and 'jquery-ui-' not in fn:
        o = open(f, 'r')
        c = o.read()
        for hp in html_patterns:
            matches = re.findall(hp, c)
            for m in matches:
                if m not in all_phrases_from_html:
                    all_phrases_from_html.append(m)
        o.close()

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
    if 'netbox/netbox/forms' in f and fe == '.py':
        search_form_translate(f)
    elif 'netbox/dcim/views' in f and fe == '.py':
        translate_titles(f)
    elif 'dcim/models/device_components' in f and fe == '.py':
        add_verb_name_to_field(f)
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
                    # print('++++++++++++++++++++++++++++++++')
                    # print(f)
                    # print(pp)
                    # print('++++++++++++++++++++++++++++++++')
                    # print(orig)
                    # print('++++++++++++++++++++++++++++++++')
                    tran = str(dict_phrases.get(orig)).replace('"', '\\"')
                    # print(tran)
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
                    try:
                        orig = re.findall(hp, raw)[0]
                        tran = str(dict_html.get(orig)).replace('"', '\\"')
                        if dict_html.get(orig):
                            c = c.replace(raw, raw.replace(orig, tran))
                    except Exception as e:
                        orig = raw
                        tran = str(dict_html.get(orig)).replace('"', '\\"')
                        if dict_html.get(orig):
                            c = c.replace(raw, raw.replace(orig, tran))
                        # else:
                        #     print('ERROR HTML')
                        #     print(f)
                        #     print(f'Row: {raw} - {len(raw)} reg:{hp}')
        nf = f.replace(source_dir, translate_dir)
        os.makedirs(os.path.dirname(nf), exist_ok=True)
        w = open(nf, 'w+')
        w.write(c)
        o.close()
        w.close()
