import xbmc
import os
    
files_to_clear = ['screen_path.dat', 'term_agree.dat']

for f_name in files_to_clear:
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f_name)
    if os.path.exists(file_path):
        os.remove(file_path)

