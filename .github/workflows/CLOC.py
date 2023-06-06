import os

languages = ['.py', '.html', '.css', '.js']

pretty_languages = ['Python', 'HTML', 'CSS', 'JavaScript']

current_folder = os.getcwd()

web_folder = os.path.join(current_folder, 'web')

assets_folder = os.path.join(web_folder, 'assets')

tools_folder = os.path.join(current_folder, '.tools')

directories = [os.getcwd(), web_folder, assets_folder, tools_folder]

files = []

for directory in directories:
    # had to be changed bc of the way that linux (ubuntu-latest) does directories, it uses / instead \
    directory_files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.extend(directory_files)

LOC_by_language = []

for language in languages:
    language_LOC = 0
    # get list of files that end with specific type
    files_of_language = [f for f in files if f.endswith(language)]
    
    # files_found.append([type(f) for f in files if f.endswith(language)])
    if files_of_language:
        for file in files_of_language:
            file_LOC = 0
            with open(file, 'r') as fp:
                for file_LOC, line in enumerate(fp):
                    pass
            language_LOC += file_LOC
    LOC_by_language.append(language_LOC)

ttl_loc = 0
new_contents = []
with open('README.md', 'r') as readme:
    contents = readme.readlines()

    content_before_LOC = contents[ :contents.index('<Lines of Code>\n')+1]
    content_before_LOC.append('\n')
    content_after_LOC = contents[contents.index('<Lines of Code/>\n'): ]

    lines_of_code = []
    lines_of_code.append("## Code Stats:\n")

    for (a, b) in zip(pretty_languages, LOC_by_language):
        lines_of_code.append(f'- {a}: {b}\n')
        ttl_loc += b

    lines_of_code.append(f'- Total Lines of Code: {ttl_loc}\n')

    new_contents = content_before_LOC + lines_of_code + content_after_LOC

# with open('README.md', 'w') as readme:
#     for line in new_contents:
#         readme.write(line)
