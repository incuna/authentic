import twill

print 'test_00_config'

def test_config_idp():
    twill.commands.reset_browser()
    twill.execute_string('''
go http://localhost:10000/admin/
fv 1 username root
fv 1 password root
submit
go http://localhost:10000/admin/
find 'dministration'
''')
    twill.commands.reset_browser()
    twill.execute_string('''
go http://localhost:10000
fv 1 username user1
fv 1 password user1
submit
url http://localhost:10000
find 'You are authenticated'
''')

def test_config_sp():
    twill.commands.reset_browser()
    twill.execute_string('''
go http://localhost:10001/admin/
fv 1 username root
fv 1 password root
submit
go http://localhost:10001/admin/
find 'dministration'
''')
    twill.commands.reset_browser()
    twill.execute_string('''
go http://localhost:10001
fv 1 username user2
fv 1 password user2
submit
url http://localhost:10001
find 'You are authenticated'
''')

