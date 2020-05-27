
"""
import requests

regions = requests.get("https://api.pandemiia.in.ua/hospitals/regions/").json()
regions = list(filter(lambda x: x["hospitals_in_region"] > 0, regions))
regions_keys = [reg["key"] for reg in regions]

print(regions)



for region_key in regions_keys:
    hospitals = requests.get("https://api.pandemiia.in.ua/hospitals/?region={region_key}").json()
  
"""

import pytz
import re
import datetime
from dateutil import tz

# p = re.compile("^E[^\n]+$")

# timezones=pytz.all_timezones
# timezones = [t for t in timezones if p.match(t)]
# print(timezones)

kiev_tz = tz.gettz("Europe/Kiev")
time_to_work = datetime.time(hour=14, minute=15, second=0, tzinfo=kiev_tz)

print(time_to_work.tzinfo)
# print(kiev.localize(time_to_work))