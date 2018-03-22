# -*- coding: utf-8 -*-

from libs.db.store import db

rs = db.execute('select id, name_cn from location')

d = {}

for (id, name_cn) in rs:
    d[name_cn] = id


rs = db.execute('select cnap_id, child_name from bank')

for (cnap_id, child_name) in rs:
    id = d.get(child_name)
    print child_name
    if not id:
        continue
    db.execute('update bank set child_location_id=%s '
               'where cnap_id=%s', (id, cnap_id))
db.commit()
