from bs4 import BeautifulSoup as bs
from itertools import chain
import requests
import pprint
import json
import re


class Dan:
    def __init__(self, dan):
        self.dan = dan
        self.urnik = {}

    def dodaj_uro(self, predmet="", profesor="", pouk="", ucilnica="", st_h="", zac_h=""):
        for i in range(st_h):
            if zac_h + i in self.urnik.keys():
                predmet_ = ""
                profesor_ = ""
                pouk_ = ""
                ucilnica_ = ""
                if str(predmet) not in str(self.urnik[zac_h + i][0]):
                    predmet_ = ' | ' + str(predmet)
                if str(profesor) not in str(self.urnik[zac_h + i][1]):
                    profesor_ = ' | ' + str(profesor)
                if str(pouk) not in str(self.urnik[zac_h + i][2]):
                    pouk_ = ' | ' + str(pouk)
                if str(ucilnica) not in str(self.urnik[zac_h + i][3]):
                    ucilnica_ = ' | ' + str(ucilnica)
                tmp_urnik = [
                    str(self.urnik[zac_h + i][0]) + predmet_,
                    str(self.urnik[zac_h + i][1]) + profesor_,
                    str(self.urnik[zac_h + i][2]) + pouk_,
                    str(self.urnik[zac_h + i][3]) + ucilnica_,
                ]
                self.urnik[zac_h + i] = tmp_urnik
            else:
                self.urnik[zac_h + i] = [predmet, profesor, pouk, ucilnica]
    
    def izpisi_dan(self):
        print(str(self.dan) + ":")
        for key, values in self.urnik.items():
            print(str(key) + ": " + str(values))


def parse_ura(data):
    predmet = ""
    pouk = ""
    data0 = data.find_all('a')
    data1 = ((data.text.strip()).replace("\n", "").replace("\t", "")).split()
    for el in data1:
        if el == 'P' or el == 'V' or el == 'V1' or el == 'V2' or el == 'V3' or el == 'V4':
            pouk = el
            break
        predmet = predmet + " " + el
        
    ucilnica = data0[-1].get("title")
    profesor = data0[-2].get("title")

    data2 = data.get("style").split(";")
    data3 = []
    for el in data2[:-1]:
        number = re.findall(r'\d+\.\d+', el)
        data3.append(float(number[0]))
    
    if data3[0] < 20:
        dan = 0
    elif data3[0] < 40:
        dan = 1
    elif data3[0] < 60:
        dan = 2
    elif data3[0] < 80:
        dan = 3
    else:
        dan = 4
    st_h = round(data3[3] / 7.69)
    zac_h = round(data3[2] / 7.69) + 7
    
    return(predmet, pouk, ucilnica, profesor, dan, st_h, zac_h)


def get_link(uni, smer, let):
    url = "https://urnik.fmf.uni-lj.si/letnik/"
    with open("links.json", "r") as f:
        data = json.load(f)
    url_end = data[uni][smer][let]
    return url + str(url_end) + '/'


def json_print():
    with open("links.json", "r") as f:
        data = json.load(f)
        for uni in data:
            print("--------------------------------------------------------\n")
            print(uni)
            for smer in data[uni]:
                print('\t' + str(smer) + ':  \t' + " | ".join(data[uni][smer].keys()))
                print("")
        print("--------------------------------------------------------\n")


def get_urnik(uni="MAT", smer="pra", let="1", dan_=0):
    data = requests.get(get_link(uni, smer, let))
    soup = bs(data.content, 'lxml')
    soup = soup.find('div', class_="poravnaj-na-termine")

    all_classes = [
        'srecanje-absolute-box leftmost', 
        'srecanje-absolute-box rightmost',
        'srecanje-absolute-box leftmost rightmost',
        'srecanje-absolute-box',
    ]

    class_tab = []
    for el in all_classes:
        class_tab.append(soup.find_all('div', el))

    flatten_class = list(chain.from_iterable(class_tab))

    tab_dni = []
    for dan in ["PON", "TOR", "SRE", "CET", "PET"]:
        tab_dni.append(Dan(dan))


    for el in flatten_class:
        predmet, pouk, ucilnica, profesor, dan, st_h, zac_h = parse_ura(el)
        tab_dni[dan].dodaj_uro(predmet, profesor, pouk, ucilnica, st_h, zac_h)

    if dan_ == 0:
        for el in tab_dni:
            el.izpisi_dan()
    else:
        tab_dni[dan_-1].izpisi_dan()

