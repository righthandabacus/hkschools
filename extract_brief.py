#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import os
import json
import urlparse


parser = etree.HTMLParser()
baseurl = 'http://www.chsc.hk/psp2017/'
isascii = lambda string: all(ord(c)<128 for c in string)
schools = []
sch_ids = set([])

for filename in os.listdir('.'):
    if not filename.endswith('.html') or not filename.startswith('district'):
        continue # only look for districtXX.html
    html = open(filename).read()
    dom = etree.HTML(html, parser)
    xpath = r"//span[@class='school-md-xxcon-tit']"
    district_name = dom.xpath(xpath)[0].text.strip()
    xpath = r"//div[@class='sou_table']/table//tr"
    tablerows = dom.xpath(xpath)
    for row in tablerows:
        cells = row.xpath(r".//td")
        if not cells:
            continue # table header row, ignore
        try:
            bg, name, network, gender, subsidy, religion = cells
        except ValueError:
            continue # bottom row: 「資料由學校提供及核實。如欲進一步了解學校發展，可直接向有關學校查詢」
        bg = bg.xpath(r".//img")
        name = name.xpath(r".//a")[0]
        school = {}
        if bg:
            school['type'] = bg[0].get('title') # 直屬中學/聯繫中學/一條龍中學
        school['nexthop'] = urlparse.urljoin(baseurl, name.get('href'))
        school['names'] = filter(None, [x.strip() for x in name.itertext()])
        school['namec'] = next((n for n in school['names'] if not isascii(n)), '')
        school['namee'] = next((n for n in school['names'] if isascii(n)), '')
        school['district'] = district_name
        school['sch_id'] = int(dict(urlparse.parse_qsl(urlparse.urlsplit(school['nexthop']).query))['sch_id'])
        if school['sch_id'] in sch_ids:
            continue # in two zones, school 530, 457, 401, 400, 402, 401, 400, 402, 530, 457
        else:
            sch_ids.add(school['sch_id'])
        schools.append(school)
open('schools.json','wb').write(json.dumps(schools, ensure_ascii=False, sort_keys=True, indent=4).encode('utf-8'))
print "%d schools written" % len(schools)
