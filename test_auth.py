from repository.mysql_repo import MySQLRepository
from services.auth_service import AuthService

repo = MySQLRepository()
auth = AuthService(repo)

ok, msg = auth.register('jihane', 'dojo1234')
print(f'Signup : {ok} -- {msg}')

user, msg = auth.login('jihane', 'dojo1234')
print(f'Login OK : {user.username if user else None} -- {msg}')

user2, msg2 = auth.login('jihane', 'mauvais')
print(f'Login KO : {user2} -- {msg2}')