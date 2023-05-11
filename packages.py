import importlib_metadata

dists = importlib_metadata.distributions()

name = []
version = []

for dist in dists:
    name.append(dist.metadata["Name"])
    version.append(dist.version)

nameVersion = dict(zip(name, version))

fileName = 'ytDownloader.py'

lines = []

with open(fileName, 'r') as input:
   for line in input:
        if '### END OF IMPORT ###' in line:
            break
        lines.append(line)

# remove comments ### or """
lines[:] = [x for x in lines if not x.startswith('"""')]
lines[:] = [x for x in lines if not x.startswith('###')]

# remove new lines
lines[:] = [x for x in lines if not x.startswith('\n')]
lines[:] = [x.removesuffix('\n') for x in lines if x.endswith('\n')]

fromLines = [x.split('import ')[0] for x in lines if x.startswith('from')]
importLines = [x.split('import ')[1] for x in lines if x.startswith('import')]

fromLines[:] = [x.split('from ')[1] for x in fromLines if x.startswith('from')]
fromLines[:] = [x.split('.')[0] for x in fromLines if '.' in x]

fromLines[:] = list(set(fromLines))

packages = fromLines+importLines

packages[:] = [x.replace(" ", "") for x in packages]

versionPackage = {k: nameVersion[k] for k in packages if k in nameVersion}

print(versionPackage)


