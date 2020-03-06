from os import listdir

html = {}

for LeFile in listdir('./public'):
    if LeFile.count('.html'):
        html[LeFile.replace('.html', '')] = open('./public/{}'.format(LeFile), 'r').read()

def mke_html(filename, file_params) -> str:
    ret = html[filename]
    if ret.count('%s') == len(file_params):
        ret = ret % file_params
        return ret
    else:
        return '<h1>Internal Server Error</h1>'