import importlib_metadata
import sys

"""Download your browser's version of ChromeDriver from https://chromedriver.chromium.org/downloads"""

sys.path.append('../ytDownloader')

dists = importlib_metadata.distributions()

name = []
version = []

for dist in dists:
    name.append(dist.metadata["Name"])
    version.append(dist.version)

nameVersion = dict(zip(name, version))

fileName = 'yt_downloader.py'

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

# find the part left or right of import that we want
fromLines = [x.split('import ')[0] for x in lines if x.startswith('from')]
importLines = [x.split('import ')[1] for x in lines if x.startswith('import')]

# get the part we want
fromLines[:] = [x.split('from ')[1] for x in fromLines if x.startswith('from')]
fromLines[:] = [x.split('.')[0] for x in fromLines]

# remove duplicates
fromLines[:] = list(set(fromLines))

# combine the lists
packages = fromLines+importLines


# unnecessary to include in yt_downloader.py but necessary for dependencies.md
packages.append('pyinstaller')

# remove spaces
packages[:] = [x.replace(" ", "") for x in packages]

# alphabetize
packages.sort()

# create dictionary of packages and versions installed AND used
versionPackage = {k: nameVersion[k] for k in packages if k in nameVersion}


requirementLine = []

n = 0
for package in versionPackage:
    requirementLine.append('- ' + package + '==' + list(versionPackage.values())[n])
    n += 1

f = open('dependencies.md')
readFile = f.read()
f.close()

everythingBefore = readFile.split('## Python Packages')[0].strip('\n')
everythingAfter = readFile.split('## Python Packages')[1]

everythingAfter = '##' + everythingAfter.split('##')[1]

newRequirements = '## Python Packages\n' + '\n'.join(requirementLine)

newWrite = everythingBefore + '\n' + newRequirements + '\n' + everythingAfter

f = open('dependencies.md', 'w')
f.write(newWrite)
f.close()

print("dependencies.md updated")