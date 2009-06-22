from distutils.core import setup
import py2exe
opts = {
        "py2exe": {
        "bundle_files": 1,
        'optimize': 2,
        "dist_dir" : "../files",
        "dll_excludes": [ 'tcl84.dll', 'tk84.dll' ],
        }
    }
setup(
  windows=["chresgui.py"],
  name="chres - an utility for image size conversion",
  url="http://www.linuxabordo.com.br",
  data_files=[('tcl84.dll'),('tk84.dll'),('chresgui.ico'),('trash.ico')],
  options=opts,
  description="chres - an utility for image size conversion",
  author="Marcelo Barros de Almeida",
  author_email="marcelobarrosalmeida@gmail.com",
  long_description="""
    chres - an utility for image size conversion.
    """
)

