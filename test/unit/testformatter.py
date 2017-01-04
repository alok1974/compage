import unittest


from compage import formatter


class TestFormatters(unittest.TestCase):
    def setUp(self):
        self.dict_string = (
            '{\n'
            '    "foo": [\n'
            '        "bar"\n'
            '    ]\n'
            '}'
        )

        self.formatted_dict = formatter.FormattedDict()
        self.formatted_dict['foo'] = ['bar']
        self.formatted_default_dict = formatter.FormattedDefaultDict(list)
        self.formatted_default_dict['foo'].append('bar')
        self.width01 = 79
        self.width02 = 3
        self.msg = "Foo"
        self.iterable = ['Foo', 'Bar', 'Baz']
        self.format_char = "*"
        self.camel_case = "fooBar"
        self.expected_string_00 = "*Foo*, *Bar*, *Baz*"
        self.expected_string_01 = "---\n{0}\n---".format(self.msg)

        self.expected_string_02 = (
            "{sep}\n"
            "{msg}\n"
            "{sep}").format(sep="*" * self.width01, msg=self.msg)

        self.expected_string_03 = "{msg}\n{sep}".format(
            msg=self.msg, sep="-" * self.width01)

        self.expected_string_04 = "{sep}\n{msg}".format(
            msg=self.msg, sep="-" * self.width01)

        self.expected_string_05 = "Foo\nBar\nBaz"
        self.expected_string_06 = "foo_bar"

    def test_formatted_dict_repr(self):
        self.assertEquals(
            self.formatted_dict.__repr__(),
            self.dict_string,
        )

    def test_formatted_default_dict_repr(self):
        self.assertEquals(
            self.formatted_default_dict.__repr__(),
            self.dict_string,
        )

    def test_wrap(self):
        self.assertEquals(formatter.wrap(self.msg, width=1), "F\no\no")

    def test_format_iterable(self):
        self.assertEquals(
            formatter.format_iterable(
                self.iterable,
                format_char=self.format_char,
            ),
            self.expected_string_00,
        )

    def test_format_header_01(self):
        self.assertEquals(
            formatter.format_header(self.msg, auto_length=True),
            self.expected_string_01,
        )

    def test_format_header_02(self):
        self.assertEquals(
            formatter.format_header(
                self.msg, format_char="*",
                width=self.width01,
            ),
            self.expected_string_02,
        )

    def test_format_header_03(self):
        self.assertEquals(
            formatter.format_header(self.msg, top=False, width=self.width01),
            self.expected_string_03,
        )

    def test_format_header_04(self):
        self.assertEquals(
            formatter.format_header(
                self.msg, bottom=False,
                width=self.width01,
            ),
            self.expected_string_04,
        )

    def test_format_header_05(self):
        self.assertEquals(
            formatter.format_header(
                self.msg, top=False,
                bottom=False,
                width=self.width02
            ),
            self.msg,
        )

    def test_format_output(self):
        self.assertEquals(
            formatter.format_output(self.iterable, width=3),
            self.expected_string_05,
        )

    def test_camel_case_to_snake_case(self):
        self.assertEquals(
            formatter.camel_case_to_snake_case(self.camel_case),
            self.expected_string_06,
        )

    def test_hex_to_alpha(self):
        self.assertEqual(formatter.hex_to_alpha('f718b'), 'fhbib')


if __name__ == '__main__':
    unittest.main()
