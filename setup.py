from distutils.core import setup
import py2exe

setup(
    name='Trikatuka',
    description='Spotify playlists migration tool',
    author='Artur Nowakowski',
    url='https://aknowakowski.blogspot.com',
    console=['app.py'],
    requires=['requests', 'web.py'],
    data_files=[
        ('templates',['templates/index.html',
                             'templates/layout.html',
                             'templates/loginSuccessful.html',
                             'templates/loginUnsuccessful.html']),
        ('static/css',['static/css/style.css','static/css/uikit.min.css']),
        ('static/fonts',['static/fonts/FontAwesome.otf','static/fonts/fontawesome-webfont.eot',
                         'static/fonts/fontawesome-webfont.ttf',
                         'static/fonts/fontawesome-webfont.woff',
                         'static/fonts/fontawesome-webfont.woff2'])]
)
