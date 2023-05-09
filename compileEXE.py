import virtualenv
from os.path import join, expanduser

venv_dir = join(expanduser("~"), ".venv")
virtualenv.create_environment(venv_dir)

