dagar = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag']
cleaners = ['<tr>', '</tr>', '<td>', '</td>']

class dag:
    def __init__(self, html):
        self.dag = 'Default'
        for d in dagar:
            if html.count(d):
                self.dag = d
                break

        self.ratter = []
        html = html.split('\n')
        for line in html:
            for x in range(1, 10):
                if line.count('{}:'.format(x)):
                    line = line.replace('</tr>, <tr><td>', '')
                    line = line.replace('</td>', '')
                    line = line.replace('&amp;', '&')
                    self.ratter.append(line)

    def getRatter(self):
        return self.ratter

    def getDag(self):
        return self.dag


def vecka(html):
    matlistor = html.split('<th')

    veckodagar = []

    for lista in matlistor:
        p = dag(lista)
        if not p.getDag() == 'Default':
            veckodagar.append(p)

    return veckodagar

class user_class:
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password



