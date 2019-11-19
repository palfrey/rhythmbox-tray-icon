import sys
import re

line_pattern = re.compile("\(rhythmbox:\d+\): (?P<group>.+)-(?P<priority>.+) \*\*: \d+:\d+:\d+\.\d+: (?P<message>.+)")

problems = False
for line in open(sys.argv[1]).readlines():
    if line.strip() == "":
        continue
    try:
        items = line_pattern.search(line).groupdict()
    except AttributeError:
        problems = True
        sys.stdout.write(line)
        continue
    if items['group'] in ['dbind', 'libdmapsharing']:
        continue
    if items['message'].startswith("Unable to start mDNS browsing"):
        continue
    if items['message'].startswith("Unable to grab media player keys"):
        continue
    problems = True
    print(items)

if problems:
    sys.exit(-1)