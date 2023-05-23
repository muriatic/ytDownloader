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

# import lines 
lines[:] = [x for x in lines if x.startswith(("import", "from"))]
lines[:] = [x.replace("\n", "") for x in lines]

# find the part left or right of import that we want
importLines = [x for x in lines if x.startswith("import")]
fromLines = [x for x in lines if x not in importLines]

# get the part we want
importLines[:] = [x.split('import ')[1] for x in importLines]
fromLines[:] = [x.split(' import')[0].split('from ')[1].split('.')[0] for x in fromLines]

# remove duplicates
importLines[:] = list(set(importLines))
fromLines[:] = list(set(fromLines))

# remove duplicates
packages = list(set(importLines + fromLines))

# unnecessary to include in yt_downloader.py but necessary for dependencies.md
packages.append('pyinstaller')

# for some weird reason eel is saved as a package as Eel so we need to adjust it in the list
packages[:] = [x.replace("eel", "Eel") for x in packages]

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