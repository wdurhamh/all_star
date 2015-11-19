import requests
import re
import sys
from bs4 import BeautifulSoup

def get_weight(text):
    weight_pos = text.find('Weight')
    if (weight_pos == -1):
        return ''
    #weight: ###
    #012345678
    start_index = weight_pos+8
    weight = text[start_index:start_index+3]
    return weight

def get_height(text):
    height_pos = text.find('Height')
    if (height_pos == -1):
        return ''
    #height: #-##
    #012345678
    start_index = height_pos + 8
    height_string = text[start_index:start_index + 4].replace(' ','')
    feet_inches = int(height_string[0:1])*12
    inches = int(height_string[2:])
    return str(feet_inches + inches)

def get_stats(text):
    stats_pos = text.find('Career:')
    #Career: ### G, ##.# PPG ##  RPG, #.## APG
    #0123456
    pos = stats_pos +7
    char = text[stats_pos]
    while char != 'G':
        pos += 1
        char = text[pos]
    pos += 3
    ppg_string = ''
    char = text[pos]
    while char != ' ':
        ppg_string +=char
        pos += 1
        char = text[pos]
    rpg_string = ''
    pos += 6
    char  = text[pos]
    while char != ' ':
        rpg_string += char
        pos += 1
        char = text[pos]
    apg_string = ''
    pos += 6
    char = text[pos]
    while char != ' ':
        apg_string += char
        pos += 1
        char = text[pos]
    return ppg_string, rpg_string, apg_string

def get_fgp(text):
    beg = text.find('Career') + 300
    pos = text.find('Career', beg, len(text))
    #need to grap seventh line down from here
    temp = text[pos:pos+500]
    lines = temp.split('\n')
    return lines[7]

base_url = 'http://www.sports-reference.com/cbb/players/'
suffix = '-1.html'
#read in names frmo raw_text
name_file = sys.argv[1]
out_file = sys.argv[2]
mode = 'w'
if len(sys.argv) >3 and (sys.argv[3] == '-a' or sys.argv[3] == '--append'):
    mode = 'a'
names = open(name_file, 'r')
out = open(out_file, mode)
out.write('Name, ppg, fgp, rpg, apg, height, weight, all-star;\n')

allstar_ref = 'https://en.wikipedia.org/wiki/List_of_NBA_All-Stars'
r = requests.get(allstar_ref)
soup = BeautifulSoup(r.content)
allstars = soup.find_all('span', {'class' : 'sortkey'})
front_tag = '<span class="sortkey">'
back_tag = '</span>'
for i in range(len(allstars)):
    start = len(front_tag)
    end = len(allstars[i]) - len(back_tag) - 1
    allstars[i] = ((str)(allstars[i]))[start:end]
    #flip name format ASSUMES no multiple first/last names
    current = allstars[i].split(', ')
    allstars[i] = (str)(current[-1] + ' ' + current[0])

for name in names:
    name = name.replace('\n','')
    html_name = name.replace(' ','-')
    html_name = html_name.replace('\n', '').replace("'", "").replace('.','').lower()
    url = base_url + html_name + suffix
    print url
    response = requests.get(url)
    height = weight = ppg = rpg = apg = fgp = ''
    text = re.sub('<[^>]+>', '', response.text)
    weight = get_weight(text)
    height = get_height(text)
    isAllStar = 0
#    print 'Finding', repr(name)
#    print repr(allstars[128])
    if name in allstars:
        isAllStar = 'y'
    else:
        isAllStar = 'n'
        
    if height != '' or weight != '':
        ppg,rpg,apg = get_stats(text)
        fgp = get_fgp(text)
        print "Weight: ", weight, "Height: ", height, ppg, rpg, apg, fgp, "AllStar: ", isAllStar
        out.write(name + ',' + ppg + ',' + fgp + ',' + rpg + ',' + apg + ',' + height + ',' + weight + ',' + isAllStar +'\n')
    else:
        out.write(name + ',-,-,-,-,-,-,y\n') 
 
    
