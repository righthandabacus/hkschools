#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import os
import json
import urlparse
import sys

parser = etree.HTMLParser()
baseurl = 'http://www.chsc.hk/psp2017/'
jsonfile = 'schools.json'
isascii = lambda string: all(ord(c)<128 for c in string)
schools = json.loads(open(jsonfile).read())
lookup = {x['sch_id']:x for x in schools}
print len(lookup)
sys.exit(0)
school_count = 0

for filename in os.listdir('.'):
    if not filename.endswith('.html') or not filename.startswith('school'):
        continue # only look for schoolXX.html
    html = open(filename).read()
    school_count = school_count + 1
    schid = int(''.join(c for c in filename if c.isdigit()))
    school = lookup[schid]
    dom = etree.HTML(html, parser)
    # 基本資料
    xpath = r"//div[@class='xxzl-info']" # xxzl=小學資料?
    basicinfo = dom.xpath(xpath)[0]
    badge = basicinfo.xpath(r".//dt//img")
    if badge:
        school['badgeurl'] = urlparse.urljoin(baseurl, badge[0].get('src'))
    names = [x.strip() for x in basicinfo.xpath(r".//dd[@class='xxzl-info-tit']")[0].itertext()]
    school['names'] = sorted(set(school['names'] + names)) # merge the set of names
    zone = basicinfo.xpath(r".//dd[@class='xxzl-info-bh']/span")[0].text.split() # bh = 編號?
    assert(len(zone) == 4)
    school[u'校網編號'] = zone[-1]
    addr_rows = basicinfo.xpath(r".//dd[contains(@class,'xxzl-info-dz')]/table/tr") # dz = 地址?
    for row in addr_rows:
        cells = [x.text.strip() for x in row.xpath(r".//td")]
        i = 0
        while i < len(cells)-1: # 地址, 電話, 傳真, 電郵
            if cells[i].endswith(':'):
                school[cells[i][:-1]] = cells[i+1]
                i = i+2
            else:
                i = i+1
    # unstructured info
    xpath = r"//div[@class='xxzl-con']/dl[@class='xxzl-list']"
    infotables = dom.xpath(xpath)[0].getchildren()
    section = None
    i = 0
    while i < len(infotables):
        if infotables[i].tag == 'dt':
            section = ''.join(x.strip() for x in infotables[i].itertext())
            school[section] = {}
        elif infotables[i].tag == 'dd':
            rows = infotables[i].xpath(r"./div[@class='sou_table']/table//tr")
            keyprefix = ''
            for row in rows:
                cells = row.xpath(r"./td")
                if len(cells) == 3:
                    key = ''.join(x.strip() for x in cells[0].itertext())
                    value = '\n'.join(x.strip() for x in cells[-1].itertext())
                    school[section][keyprefix + key] = value
                elif len(cells) == 1:
                    if not school[section] and len(rows)==1:
                        # table with single row: just a key-value together with the row above
                        school[section] = '\n'.join(x.strip() for x in cells[-1].itertext())
                    else:
                        keyprefix = ' '.join(x.strip() for x in cells[-1].itertext()) + "="
        i = i+1
open(jsonfile,'wb').write(json.dumps(sorted(schools, key=lambda x:x['id']), ensure_ascii=False, sort_keys=True, indent=4).encode('utf-8'))
print "%d out of %d schools refreshed" % (school_count, len(schools))
