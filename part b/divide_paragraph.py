import numpy as np
import copy

indent = '    '
indent_length = 4

class CodeParagrah:
    def __init__(self, start, end, indent_num, children = []):
        self.start = start
        self.end = end
        self.indent_num = indent_num
        self.children = children


def count_indent(code):
    count = 0
    while code.startswith(indent):
        count+=1
        code = code[4:]
    return count

def find_paragraph(result):
    result += '\n'
    paragraph_stack = []
    for i in range(len(result)):
        code = result[i]
        indent_num = count_indent(code)
        line_num = i+1
        if len(paragraph_stack) == 0 or indent_num >= paragraph_stack[-1][1]:
            paragraph_stack.append( [line_num, indent_num, None] )
        else:
            pre_indent_num = paragraph_stack[-1][1]
            current_paragraph = CodeParagrah(-1, line_num, pre_indent_num)
            while len(paragraph_stack) > 0 and indent_num < paragraph_stack[-1][1]:
                if  paragraph_stack[-1][1] != pre_indent_num:
                    current_paragraph.start = paragraph_stack[-1][0]
                    paragraph_stack[-1][2] = copy.deepcopy(current_paragraph)

                    pre_indent_num = paragraph_stack[-1][1]
                    current_paragraph = CodeParagrah(-1, line_num, pre_indent_num, paragraph_stack[-1][2])

                else:
                    if paragraph_stack[-1][2] != None:
                        current_paragraph.children.append(paragraph_stack[-1][2])

                paragraph_stack.pop()
            current_paragraph.start = paragraph_stack[-1][0]
            paragraph_stack[-1][2] = copy.deepcopy(current_paragraph)
    return paragraph_stack

f = open("gif_maker.py")
lines = f.readlines()
result = find_paragraph(lines)
a = 1



