import numpy as np
import copy

indent = '    '
indent_length = 4


class CodeParagrah:
    def __init__(self, start, end, indent_num, children):
        self.start = start
        self.end = end
        self.indent_num = indent_num
        self.children = children


def count_indent(code):
    count = 0
    while code.startswith(indent):
        count += 1
        code = code[4:]
    return count


def isBlank(code):
    a = code.strip() == ''
    return a


def find_paragraph(result):
    result.append('END')
    paragraph_stack = []
    for i in range(len(result)):
        code = result[i]
        indent_num = count_indent(code)
        line_num = i + 1
        if isBlank(code):
            continue

        if len(paragraph_stack) == 0 or indent_num >= paragraph_stack[-1][1]:
            paragraph_stack.append([line_num, indent_num, []])
        else:
            pre_indent_num = paragraph_stack[-1][1]
            current_paragraph = CodeParagrah(-1, line_num, pre_indent_num, [])
            while len(paragraph_stack) > 0 and indent_num < paragraph_stack[-1][1]:
                if paragraph_stack[-1][1] != pre_indent_num:
                    current_paragraph.start = paragraph_stack[-1][0]
                    paragraph_stack[-1][2].append(copy.deepcopy(current_paragraph))

                    pre_indent_num = paragraph_stack[-1][1]
                    current_paragraph = CodeParagrah(-1, line_num, pre_indent_num, paragraph_stack[-1][2])

                else:
                    current_paragraph.children += paragraph_stack[-1][2]
                paragraph_stack.pop()

            current_paragraph.start = paragraph_stack[-1][0]
            paragraph_stack[-1][2].append(copy.deepcopy(current_paragraph))
            paragraph_stack.append([line_num, indent_num, []])
    return paragraph_stack[0:-1]


f = open("nn.py")
lines = f.readlines()
result = find_paragraph(lines)
a = 1
