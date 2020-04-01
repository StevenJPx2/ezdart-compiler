import re
import time
import os
from collections import deque


class StringWidget(object):
    def __init__(self, object_string):
        self.object_string = self.parse_obj_str(object_string)
        self.children = None

    def _find_children(self, string, children=None):
        code_stack = deque()
        count = 0
        if children is None:
            children = []

        index = 0
        while index != len(string):
            char = string[index]
            if char == "~":
                if string[index : index + 6] == "~start":
                    code_stack.append("~start")
                    index += 6
                    count += 1
                elif string[index : index + 4] == "~end":

                    if count == 1:
                        count = 0
                        child_string = ""
                        start_count = 0
                        while True:
                            c = code_stack.pop()
                            if c == "~end":
                                child_string += self.rev_str(c)
                                start_count += 1
                            elif c == "~start":
                                if start_count > 0:
                                    child_string += self.rev_str(c)
                                    start_count -= 1
                                else:
                                    children.append(self.rev_str(child_string))
                                    break
                            else:
                                child_string += c
                    else:
                        code_stack.append("~end")
                        count -= 1
                    index += 4
                else:
                    index += 1

            else:
                index += 1
                code_stack.append(char)

        self.children = children

        return children

    @staticmethod
    def _find_end_of_fn(string):
        count = 0
        for index in range(len(string)):
            char = string[index]
            if char == "(":
                count += 1

            elif char == ")":
                if count > 1:
                    count -= 1
                else:
                    index += 1
                    break

        return index

    @staticmethod
    def _find_child(object_string, index):
        while index < len(object_string):
            char = object_string[index]
            if char == "^":
                return object_string[index + 1 :]
            if re.match(r"\s", char):
                index += 1
            else:
                return False
        return False

    @staticmethod
    def _find_widget_attr(string, has_child):
        name_split = string.split("(", maxsplit=1)
        name = name_split[0].strip()
        string = name_split[1]
        if has_child == 0:
            string = string.split("~start", maxsplit=1)[0] + "~~"
        if has_child == 1:
            string = string.split("^", maxsplit=1)[0]

        code_stack = deque()
        index = 0
        count = 0
        attr = ""
        while index < len(string):
            char = string[index]
            if char == "(":
                count += 1
            elif char == ")":
                if count > 0:
                    count -= 1

                else:
                    attr = "".join(code_stack)
                    break
            elif char == "~":
                if string[index : index + 2] == "~~":
                    attr = "".join(code_stack)
                    break

            code_stack.append(char)
            index += 1

        return attr

    @staticmethod
    def _find_w(string, has_child, index):
        only_code = string.split("(", maxsplit=1)[1]
        if has_child == 0:
            only_code = only_code.split("~start", maxsplit=1)[0] + "~~"
            index = 0
            while index < len(only_code):
                char = only_code[index]
                if char == "~":
                    if only_code[index : index + 2] == "~~":
                        break
                index += 1

            return only_code[:index]

        return string[: index - 1].split("(", maxsplit=1)[1]

    def _is_tertiary(self, string, index):
        name_split = string.split("(", maxsplit=1)
        name = name_split[0]

        return False

    def parse_obj_str(self, object_string):
        # object_string = "".join(object_string.split())
        index = self._find_end_of_fn(object_string)
        x = self._find_child(object_string, index)
        children = False
        if not x:
            children = self._find_children(object_string)

        if children:
            has_child = 0
        elif x:
            has_child = 1
        else:
            has_child = 2

        compiled_string = object_string.split("(", maxsplit=1)[0]
        tertiary_attributes = self._is_tertiary(object_string, index)
        # widget_attributes = self._find_widget_attr(object_string, has_child)
        if self._find_widget_attr(object_string, has_child) != self._find_w(
            object_string, has_child, index
        ):
            print(
                self._find_widget_attr(object_string, has_child),
                self._find_w(object_string, has_child, index),
                sep="\n",
            )
        widget_attributes = self._find_w(object_string, has_child, index)
        # print(f"Name: {compiled_string.strip()},", children, "\n\n=====\n\n")

        compiled_string += "(" + widget_attributes

        if x:
            compiled_child = StringWidget(x).object_string
            compiled_string += "child: " + compiled_child + ",)\n"
        elif children:
            children = list(map(lambda x: StringWidget(x).object_string, children))
            compiled_string += "children: <Widget> [\n"

            for child in children:
                compiled_string += child + ",\n"

            compiled_string += f"]\n,)\n"

        else:
            compiled_string += ")\n"
        return compiled_string

    @staticmethod
    def rev_str(x):
        return "".join(reversed(list(x)))


def rev_str(x):
    return "".join(reversed(list(x)))


def compile_ezdart_to_dart(code_string, code_list=None):

    code_stack = deque()

    count = 0
    index = 0
    flag = 0
    while index < len(code_string):
        char = code_string[index]
        if char == "<":
            if code_string[index : index + 2] == "<%":
                count += 1
                code_stack.append("<%")
                index += 2
            else:
                code_stack.append("<")
                index += 1

        elif char == "%":
            if code_string[index : index + 2] == "%>":
                if count > 1:
                    count -= 1
                    code_block = ""
                    while True:
                        try:
                            c = code_stack.pop()
                        except IndexError:
                            raise SystemExit()

                        if c != "<%":
                            code_block += c
                        else:
                            code_block = rev_str(code_block)
                            code_string = code_string.replace(
                                "<%" + code_block + "%>",
                                StringWidget(code_block).object_string,
                            )
                            flag = 1
                            index = 0
                            code_stack.clear()
                            break
                else:
                    pass
            else:
                index += 1
        else:
            code_stack.append(char)
            index += 1
    return code_string


def parse_dart_code_to(ezdart_code, filename=None):
    assert "code--start" in ezdart_code
    assert "code--end" in ezdart_code

    code_string = ezdart_code.split("code--start")[1].split("code--end")[0]

    code_blocks = compile_ezdart_to_dart(code_string)

    if filename is None:
        print(code_blocks)
    else:
        norm_filename = os.path.abspath(filename)
        open(norm_filename, "w").write(code_blocks)
        print("Compiled!\nFormatting...")
        os.system(f"dartfmt -w '{norm_filename}'")
        print("Formatted!")


if __name__ == "__main__":
    CODE_STRING = open("test.edart", "r").read()
    parse_dart_code_to(CODE_STRING, "test.dart")
