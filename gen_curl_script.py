#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
schools = json.loads(open('schools.json').read())
for school in schools:
    print "curl '%s' > school%d.html" % (school['nexthop'], school['id'])
