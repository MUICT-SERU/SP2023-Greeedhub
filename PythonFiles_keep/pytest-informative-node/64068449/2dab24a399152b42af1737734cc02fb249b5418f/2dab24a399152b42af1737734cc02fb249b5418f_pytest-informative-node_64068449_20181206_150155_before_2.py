# -*- coding: utf-8 -*-
import pytest
import os


def test_no_ini_config(testdir):
    testdir.makepyfile(f'''
            def test_node_id():
                """@custom_nodeid
                """
                assert 1
            ''')
    result = testdir.runpytest('-v')
    result.stdout.fnmatch_lines(['*::test_node_id* PASSED*'])


@pytest.mark.parametrize('delimiter', [' ', '*', '!@'], ids=['empty', '*', '!@'])
@pytest.mark.parametrize('switch', [' ', 'true', 'false'], ids=['empty', 'enable', 'disable'])
def test_node_id_delimiter_and_switch(delimiter, switch, testdir):
    testdir.makeini(f"""
        [pytest]
        addopts : -v
        [informative_node_id]
        enable    : {switch.strip()}
        delimiter : {delimiter.strip()}
        """)

    testdir.makepyfile(f'''
        def test_node_id():
            """{delimiter.strip() or '@'}custom_nodeid
            """
            assert 1
        ''')
    result = testdir.runpytest('-v')
    if switch == 'true':
        result.stdout.fnmatch_lines(['*::custom_nodeid* PASSED*'])
    else:
        result.stdout.fnmatch_lines(['*::test_node_id* PASSED*'])


def test_package_level(testdir):
    testdir.makeini(f"""
    [pytest]
    [informative_node_id]
    enable    : true
    """)
    testdir.mkpydir('my_package_one')
    testdir.mkpydir('my_package_two')
    testdir.mkpydir('my_package_three')
    testdir.mkdir('my_package_four')
    with open('my_package_one/__init__.py', 'w') as fp:
        fp.write('''"""@ package1"""''')

    with open('my_package_two/__init__.py', 'w') as fp:
        fp.write('''"""@ package2"""''')

    testdir.makepyfile(test_module_one='''
        """@module1"""
        class TestCls_one:
            """@ cls_1"""
            def test_a(self):
                """@method_a"""
                assert 1
            def test_b(self):
                """@method_b"""
                assert 1

        class TestCls_two:
            """@ cls_2"""
            def test_a(self):
                """@method_a"""
                assert 1
            def test_b(self):
                """@method_b"""
                assert 1
        ''')
    testdir.makepyfile(test_module_two='''
            """@module2"""
            class TestCls_one:
                """@cls_1"""
                def test_a(self):
                    """@method_a"""
                    assert 1
                def test_b(self):
                    """@method_b"""
                    assert 1

            class TestCls_two:
                """@ cls_2"""
                def test_a(self):
                    """@method_a"""
                    assert 1
                def test_b(self):
                    """@method_b"""
                    assert 1
            ''')

    os.rename('test_module_one.py', 'my_package_one/test_module_one.py')
    os.rename('test_module_two.py', 'my_package_one/test_module_two.py')

    testdir.makepyfile(test_module_one='''
        """@module1"""
        class TestCls_one:
            """@cls_1"""
            def test_a(self):
                """@method_a"""
                assert 1
            def test_b(self):
                """@method_b"""
                assert 1

        class TestCls_two:
            """@ cls_2"""
            def test_a(self):
                """@method_a"""
                assert 1
            def test_b(self):
                """@method_b"""
                assert 1
        ''')
    testdir.makepyfile(test_module_two='''
            """@module2"""
            import pytest
            
            class TestCls_one:
                """@cls_1"""
                def test_a(self):
                    """@method_a"""
                    assert 1
                def test_b(self):
                    """@method_b"""
                    assert 1

            class TestCls_two:
                """@ cls_2"""
                def test_a(self):
                    """@method_a"""
                    assert 1
                def test_b(self):
                    """@method_b"""
                    assert 1
            class TestCls_three:
                """@ cls_3"""
                @pytest.mark.parametrize('number',[1,2],ids=['one','two'])
                def test_a(self,number):
                    """@method_parametrized"""
                    assert 1
            def test_a():
                """@top_level_function"""
                assert 1
            
            @pytest.mark.parametrize('number',[1,2],ids=['one','two'])
            def test_b(number):
                """@top_level_function_parametrized"""
                assert 1
            ''')

    os.rename('test_module_one.py', 'my_package_two/test_module_one.py')
    os.rename('test_module_two.py', 'my_package_two/test_module_two.py')

    testdir.makepyfile(test_module_three='''
            """@module3"""
            class TestCls_one:
                """@cls_1"""
                def test_a(self):
                    """@method_a"""
                    assert 1
                def test_b(self):
                    """@method_b"""
                    assert 1
            ''')

    os.rename('test_module_three.py', 'my_package_three/test_module_three.py')

    testdir.makepyfile(test_module_four='''
                """@module4"""
                class TestCls_one:
                    """@cls_1"""
                    def test_a(self):
                        """@method_a"""
                        assert 1
                    def test_b(self):
                        """@method_b"""
                        assert 1
                ''')

    os.rename('test_module_four.py', 'my_package_four/test_module_four.py')
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        'my_package_four*module4*cls_1*method_a* PASSED*',
        'my_package_four*module4*cls_1*method_b* PASSED*',
        'package1*module1*cls_1*method_a* PASSED*',
        'package1*module1*cls_1*method_b* PASSED*',
        'package1*module1*cls_2*method_a* PASSED*',
        'package1*module1*cls_2*method_b* PASSED*',
        'package1*module2*cls_1*method_a* PASSED*',
        'package1*module2*cls_1*method_b* PASSED*',
        'package1*module2*cls_2*method_a* PASSED*',
        'package1*module2*cls_2*method_b* PASSED*',
        'my_package_three*module3*cls_1*method_a* PASSED*',
        'my_package_three*module3*cls_1*method_b* PASSED*',
        'package2*module1*cls_1*method_a* PASSED*',
        'package2*module1*cls_1*method_b* PASSED*',
        'package2*module1*cls_2*method_a* PASSED*',
        'package2*module1*cls_2*method_b* PASSED*',
        'package2*module2*cls_1*method_a* PASSED*',
        'package2*module2*cls_1*method_b* PASSED*',
        'package2*module2*cls_2*method_a* PASSED*',
        'package2*module2*cls_2*method_b* PASSED*',
        'package2*module2*cls_3*method_parametrized*one* PASSED*',
        'package2*module2*cls_3*method_parametrized*two* PASSED*',
        'package2*module2*top_level_function* PASSED*',
        'package2*module2*top_level_function_parametrized*one** PASSED*',
        'package2*module2*top_level_function_parametrized*two** PASSED*',
    ])


if __name__ == '__main__':
    pytest.main()
