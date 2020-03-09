This is a python code for custom DNS Server. 

You may face following Errors:- 

1. Traceback (most recent call last):
  File "1DNS.py", line 24, in <module>
    zonedata = load_zones()
  File "1DNS.py", line 18, in load_zones
    data = json.load(zonedata)
  File "/usr/lib/python3.6/json/__init__.py", line 299, in load
    parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
  File "/usr/lib/python3.6/json/__init__.py", line 354, in loads
    return _default_decoder.decode(s)
  File "/usr/lib/python3.6/json/decoder.py", line 339, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/lib/python3.6/json/decoder.py", line 355, in raw_decode
    obj, end = self.scan_once(s, idx)

Cause:-  The Python json module is strict in its interpretation of JSON. The usual problem is that wherever you are getting your alleged JSON from, is not generating strictly valid JSON. A common mistake is {...}{...} or {...},{...} rather than the valid list-of-dicts [{...},{...}]

Solution :- Check if the zone file is in correct json format. To check the same you can use any online json validator.
