from os import listdir

html = {}

for LeFile in listdir('./public'):
    if LeFile.count('.html'):
        html[LeFile.replace('.html', '')] = open('./public/{}'.format(LeFile), 'r').read()

def get_html(filename) -> str:
    ret = html[filename]
    
    return ret