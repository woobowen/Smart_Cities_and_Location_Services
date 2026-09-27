"""Regression for the user-supplied identity through repeated report generation."""
import json
import pytest

from task1.goal3.identity import read_identity, write_report_metadata


def test_identity_survives_regeneration(tmp_path):
    identity = read_identity()
    assert identity['student_name'] == '吴博闻'
    assert identity['student_id'] == '10245102410'
    config = tmp_path/'task1/config/assignment.json'
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps(identity, ensure_ascii=False), encoding='utf8')
    (tmp_path/'task1/reports').mkdir()
    target = write_report_metadata(tmp_path)
    expected = target.read_bytes()
    target.write_text('待补姓名 / 待补学号', encoding='utf8')
    assert write_report_metadata(tmp_path).read_bytes() == expected
    assert b'10245102410' in expected
    assert '吴博闻' in expected.decode('utf8')


@pytest.mark.parametrize('invalid', [10245102410, 10245102410.0, '1.024510241e10'])
def test_id_must_remain_digit_string(tmp_path, invalid):
    value = read_identity()
    value['student_id'] = invalid
    target = tmp_path/'task1/config/assignment.json'
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(value), encoding='utf8')
    with pytest.raises(ValueError, match='STUDENT_ID_MUST_BE_AN_ASCII_DIGIT_STRING'):
        read_identity(tmp_path)
