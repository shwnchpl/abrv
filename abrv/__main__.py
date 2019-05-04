from . import create_app
from getpass import getuser

if __name__ == '__main__':
    app = create_app(test_config={
        'SECRET_KEY': 'dev',
        'DATABASE': {
            'database': 'abrv',
            'user': getuser(),
            'password': '',
        }
    })
    app.run()
