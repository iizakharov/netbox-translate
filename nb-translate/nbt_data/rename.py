import os
from translate import source_dir, translate_dir

s_d, t_d = '../' + source_dir, '../' + translate_dir
os.rename(s_d, 'netbox_old')
os.rename(t_d, 'netbox')