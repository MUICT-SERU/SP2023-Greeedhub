from fileversioninger.tool import suggest_new_filename, append_suffix_to, remove_extension_from
from tests.asserts import assert_equal


def test_it_suggests_the_first_increment_if_no_predicate_function_supplied():
    actual = suggest_new_filename('foo.txt')
    assert_equal('foo#001.txt', actual)


def test_it_uses_the_predicate_function_to_suggest_an_available_increment():
    predicate = lambda a: True if a in ['foo#001.txt', 'foo#002.txt', 'foo#003.txt'] else False
    actual = suggest_new_filename('foo.txt', predicate)
    assert_equal('foo#004.txt', actual)


def test_can_suggest_a_non_existing_filename_using_filename_with_hash_middle_of_name():
    predicate = lambda a: True if a in ['foo#bar#001.txt', 'foo#bar#002.txt'] else False
    actual = suggest_new_filename('foo#bar#002.txt', predicate)
    assert_equal('foo#bar#003.txt', actual)


def test_can_append_suffix_with_hash_and_zero_left_padding():
    actual = append_suffix_to('foo')
    assert_equal('foo#001', actual)

    actual = append_suffix_to('foo', 9)
    assert_equal('foo#009', actual)

    actual = append_suffix_to('foo', 99)
    assert_equal('foo#099', actual)

    actual = append_suffix_to('foo', 1001)
    assert_equal('foo#1001', actual)


def test_can_suggest_a_non_existing_filename_using_filename_starting_and_ending_with_hash():
    predicate = lambda a: False

    actual = suggest_new_filename('#bar.file', predicate)
    assert_equal('#bar#001.file', actual)

    actual = suggest_new_filename('bar#.file', predicate)
    assert_equal('bar##001.file', actual)


def test_it_removes_file_extensions_from_string():
    actual = remove_extension_from('foobar.txt')
    expected = 'foobar'
    assert_equal(actual, expected)

    actual = remove_extension_from('foobar')
    expected = 'foobar'
    assert_equal(actual, expected)


def test_can_handle_file_names_without_extensions():
    actual = suggest_new_filename('bar', lambda a: False)
    assert_equal('bar#001', actual)


def test_can_handle_file_names_with_multiple_dots():
    actual = suggest_new_filename('foo.bar.txt', lambda a: False)
    assert_equal('foo.bar#001.txt', actual)


def test_can_handle_file_names_without_a_name():
    actual = suggest_new_filename('.txt', lambda a: False)
    assert_equal('#001.txt', actual)


def test_it_handles_files_that_end_with_a_dot():
    actual = suggest_new_filename('file.', lambda a: False)
    assert_equal('file.#001', actual)


def test_it_handles_files_without_extension_and_hash_in_the_middle():
    actual = suggest_new_filename('foo#bar', lambda a: False)
    assert_equal('foo#bar#001', actual)


def test_it_handles_files_with_hash_inside_and_ends_with_hash_too():
    actual = suggest_new_filename('foo#bar#', lambda a: False)
    assert_equal('foo#bar##001', actual)
