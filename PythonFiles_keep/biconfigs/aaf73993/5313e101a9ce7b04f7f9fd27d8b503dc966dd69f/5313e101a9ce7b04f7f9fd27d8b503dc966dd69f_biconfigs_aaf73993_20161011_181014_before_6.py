from biconfigs import support_cson, Biconfigs

def test_cson():
    configs = Biconfigs('.test.demo.cson', parser='cson', debug=True)
    configs['options'] = {'debug': True,
                          'username': 'Anthony',
                          'list': [] }

    configs.options.list.append('example')
