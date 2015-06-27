from reqhandlers.request_handlers import *

sys.argv[1:] = ['7878']
print sys.argv

urls = (
    '/', Hello,
    '/login_previous', LoginPrevious,
    '/login_current', LoginCurrent,
    '/sign_out_previous', SignOutPrevious,
    '/sign_out_current', SignOutCurrent,
    '/user_auth_callback', UserAuthorized,
    '/playlists', Playlists,
    '/transfer', Transfer,
    '/checkusers', Checkusers
)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
