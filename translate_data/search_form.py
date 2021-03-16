from django import forms

from utilities.forms import BootstrapMixin

OBJ_TYPE_CHOICES = (
    ('', 'Все категории'),
    ('Внешние каналы', (
        ('provider', 'Поставщики'),
        ('circuit', 'Внешние каналы'),
    )),
    ('Устройства', (
        ('site', 'Сайты'),
        ('rack', 'Стойки'),
        ('rackgroup', 'Группа стоек'),
        ('devicetype', 'ипы устройств'),
        ('device', 'Устройства'),
        ('virtualchassis', 'Виртуальные шасси'),
        ('cable', 'Кабели'),
        ('powerfeed', 'Питание'),
    )),
    ('IP адреса', (
        ('vrf', 'VRF'),
        ('aggregate', 'Сети'),
        ('prefix', 'Подсети'),
        ('ipaddress', 'IP адреса'),
        ('vlan', 'VLAN'),
    )),
    ('Ключи', (
        ('secret', 'Ключи'),
    )),
    ('Учреждения', (
        ('tenant', 'Учреждения'),
    )),
    ('Виртуализации', (
        ('cluster', 'Кластеры'),
        ('virtualmachine', 'Виртуальные машины'),
    )),
)


class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        label='Поиск'
    )
    obj_type = forms.ChoiceField(
        choices=OBJ_TYPE_CHOICES, required=False, label='Тип'
    )
