import os
import re

def replace_all(text):
    dic = {'...':'', ' & ':' ', ' = ': ' ', '?':'', '$':'s', ' + ':' ', '"':'', ',':'', '*':'', '.':'', ':':'', "'":''}	
    for i, j in dic.iteritems():
       text = text.replace(i, j)
    return text
