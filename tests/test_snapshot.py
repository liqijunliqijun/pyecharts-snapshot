import os
import sys
import filecmp
from io import BytesIO
from mock import patch
from nose.tools import raises, eq_
from platform import python_implementation

from pyecharts_snapshot.main import main, make_a_snapshot, PY2

PY27 = sys.version_info[1] == 7 and PY2 and python_implementation() != "PyPy"


class CustomTestException(Exception):
    pass


@raises(SystemExit)
def test_no_params():
    args = ['snapshot']
    with patch.object(sys, 'argv', args):
        main()


@patch('subprocess.Popen')
def test_main(fake_popen):
    fake_popen.return_value.stdout = BytesIO(get_base64_image())
    args = ['snapshot', os.path.join("tests", "fixtures", "render.html")]
    with patch.object(sys, 'argv', args):
        main()
    assert(filecmp.cmp('output.png', get_fixture('sample.png')))


@patch('subprocess.Popen')
def test_jpeg_at_command_line(fake_popen):
    fake_popen.return_value.stdout = BytesIO(get_base64_image())
    args = [
        'snapshot', os.path.join("tests", "fixtures", "render.html"), 'jpeg']
    with patch.object(sys, 'argv', args):
        main()
    assert(filecmp.cmp('output.jpeg', get_fixture('sample.jpeg')))


@patch('subprocess.Popen')
def test_pdf_at_command_line(fake_popen):
    fake_popen.return_value.stdout = BytesIO(get_base64_image())
    args = [
        'snapshot', os.path.join("tests", "fixtures", "render.html"), 'pdf']
    with patch.object(sys, 'argv', args):
        main()
    if PY27:
        # do binary comaprision
        assert(filecmp.cmp('output.pdf', get_fixture('sample.pdf')))
    else:
        # otherwise test the file is produced
        assert(os.path.exists('output.pdf'))


@patch('subprocess.Popen')
def test_delay_option(fake_popen):
    fake_popen.side_effect = Exception("Enough test. Abort")
    sample_delay = 0.1
    args = [
        'snapshot', os.path.join("tests", "fixtures", "render.html"),
        'jpeg', str(sample_delay)]
    try:
        with patch.object(sys, 'argv', args):
            main()
    except Exception:
        eq_(fake_popen.call_args[0][0][4], '100')


@patch('subprocess.Popen')
def test_windows_file_name(fake_popen):
    fake_popen.side_effect = Exception("Enough test. Abort")
    args = [
        'snapshot', "tests\\fixtures\\render.html",
        'jpeg', '0.1']
    try:
        with patch.object(sys, 'argv', args):
            main()
    except Exception:
        eq_(fake_popen.call_args[0][0][2], 'tests/fixtures/render.html')


@patch('subprocess.Popen')
def test_default_delay_value(fake_popen):
    fake_popen.side_effect = CustomTestException("Enough test. Abort")
    args = [
        'snapshot', os.path.join("tests", "fixtures", "render.html"),
        'jpeg']
    try:
        with patch.object(sys, 'argv', args):
            main()
    except CustomTestException:
        eq_(fake_popen.call_args[0][0][4], '500')


@raises(Exception)
@patch('subprocess.Popen')
def test_unknown_file_type_at_command_line(fake_popen):
    fake_popen.return_value.stdout = BytesIO(get_base64_image())
    args = [
        'snapshot', os.path.join("tests", "fixtures", "render.html"),
        'moonwalk']
    with patch.object(sys, 'argv', args):
        main()


@patch('subprocess.Popen')
def test_make_png_snapshot(fake_popen):
    fake_popen.return_value.stdout = BytesIO(get_base64_image())
    test_output = 'custom.png'
    make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                    test_output)
    assert(filecmp.cmp(test_output, get_fixture('sample.png')))


@patch('subprocess.Popen')
def test_make_jpeg_snapshot(fake_popen):
    fake_popen.return_value.stdout = BytesIO(get_base64_image())
    test_output = 'custom.jpeg'
    make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                    test_output)
    assert(filecmp.cmp(test_output, get_fixture('sample.jpeg')))


@patch('subprocess.Popen')
def test_win32_shell_flag(fake_popen):
    fake_popen.side_effect = CustomTestException("Enough. Stop testing")
    try:
        with patch.object(sys, 'platform', 'win32'):
            make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                            'sample.png')
    except CustomTestException:
        eq_(fake_popen.call_args[1]['shell'], True)


@patch('subprocess.Popen')
def test_win32_shell_flag_is_false(fake_popen):
    fake_popen.side_effect = CustomTestException("Enough. Stop testing")
    try:
        make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                        'sample.png')
    except CustomTestException:
        eq_(fake_popen.call_args[1]['shell'], False)


def test_make_a_snapshot_real():
    # cannot produce a consistent binary matching file
    test_output = 'real.png'
    make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                    test_output)
    assert(os.path.exists(test_output))  # exists just fine


def test_make_a_snapshot_real_pdf():
    test_output = 'real.pdf'
    make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                    test_output)
    assert(os.path.exists(test_output))  # exists just fine


@raises(Exception)
def test_unsupported_file_type():
    # cannot produce a consistent binary matching file
    test_output = 'real.shady'
    make_a_snapshot(os.path.join("tests", "fixtures", "render.html"),
                    test_output)


def get_base64_image():
    with open(get_fixture('base64.txt'), 'r') as f:
        content = f.read().replace('\r\n', '')
        return ("," + content).encode('utf-8')


def get_fixture(name):
    return os.path.join("tests", "fixtures", name)
