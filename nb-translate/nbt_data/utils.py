import os, re
from shutil import copyfile
from nbt_data.vocabulary import html_dict


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


def add_verb_name_to_field(file):
    t_str = '        verbose_name="Устройство",\n'
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if 'device = models.ForeignKey(' in data[i]:
                if 'verbose_name=' in data[i + 1]:
                    return
                data[i] += t_str
                break
        with open(file, 'w+') as f1:
            f1.writelines(data)
    return


def add_verbose_name_if_not_exist(file):
    """
    Скрипт принудительного создании имени класса
    Add verbose_name to class Meta if not exist
    :param file: path ro file
    :return: edited file
    """
    if '/venv/' in file or '/__pycache__/' in file:
        return
    reg = re.compile(r'[A-Z]\w+(?=\()')
    class_reg = re.compile(r'^class (?=[A-Z])')
    plural_reg = re.compile(r'(?!=[\"\'])(\b[\w ]+)(?=[\'\"\n])')
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
                    for j in data[i:i + 10]:
                        if 'verbose_name' in j and flag != 2:
                            flag = 1
                            verbose_plural = plural_reg.search(j)
                            verbose_plural = verbose_plural.group()
                            # print(verbose_plural)
                        if 'verbose_name_plural' in j:
                            flag = 2
                    if flag == 0:
                        data[i] += f'        verbose_name = "{class_name}"\n' \
                                   f'        verbose_name_plural = "{class_name}s"\n'
                    elif flag == 1:
                        data[i + 2] += f'        verbose_name_plural = "{verbose_plural}s"\n'

                except Exception as E:
                    print('add_verbouse_name_if_not_exist EXCEPTION')
                    print(E)
                    print(file)
                    print(data[i])
            elif 'class MPTTMeta:' in data[i]:
                # print('in MPTTMeta')
                flag = 0
                for j in data[i - 10:i]:
                    if 'class Meta:' in j:
                        flag = 1
                    if 'verbose_name' in j and flag == 1:
                        flag = 2
                        break
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
    # print('LANGUAGE SET TO "RUS" in settings')
    return


def search_form_translate(file):
    """
    :param file: /netbox/netbox/forms.py
    :return: /netbox/netbox/forms.py with RUS translate
    """
    search_data = 'nbt_data/translate_data/search_form.py'
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


def add_label_to_field(file):
    dict_html = get_dictionary('nbt_data/dictionary/html.dict')
    reg = re.compile('([a-z_]+)(?=[\s]?=)')
    reg_str = re.compile('[ ]+([a-z_]+)(?=\s=\s[\w\.]+\(\n)')
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if ' '*12 in data[i]:
                continue
            if reg_str.search(data[i]) is not None:
                names = reg.search(data[i])
                class_name = names.group()
                exceptions = ['pk', 'q', 'parent']
                if class_name in exceptions:
                    continue
                flag = 0
                for j in data[i+1:i+8]:
                    if 'label=' in j:
                        flag = 1
                        break
                    if ')\n' in j:
                        break
                class_name = dict_html.get(class_name.title())
                if flag == 0:
                    data[i] += f"        label='{class_name}',\n"
                    print(f'Добавлен label {class_name}')
        with open(file, 'w+') as f1:
            f1.writelines(data)
    return


def add_link_in_nav_menu(file):
    with open(file) as f:
        data = f.readlines()
        for i in range(len(data)):
            if html_dict['statistic']['search'] in data[i] or html_dict['statistic']['search_r'] in data[i]:
                for j in data[i+2:i+5]:
                    if 'Статистика' in j:
                        return
                else:
                    data[i + 1] += html_dict['statistic']['swap']
        with open(file, 'w+') as f1:
            f1.writelines(data)
    return
