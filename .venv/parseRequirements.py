import os.path

file = open(os.path.dirname(__file__) + '/../dependencies.md', 'r').read()

start = "## Python Packages"
end = "## UPX"

idx1 = file.find(start)
idx2 = file.find(end)

packages = file[idx1 + len(start) + 1: idx2]

requirements = packages.replace("- ", "")

f = open("requirements.txt", "w")

f = open("requirements.txt", "w")
f.write(requirements)
f.close
