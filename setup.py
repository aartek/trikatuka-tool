from distutils.core import setup
import py2exe

setup(
    console=['spotiauth.py'], requires=['requests', 'web.py']
)
