from collections import defaultdict
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
        self.mem_usage = None
        self.cpu_usage = None
        self.type = 'Lower Level'

    def generate_same_level_paragraph(self):
        new_child = []
        last_end = self.end
        for child in self.children:
            if child.end != last_end:
                new_child.append(CodeParagrah(child.end, last_end, self.indent_num, []) )
                new_child[-1].type = 'Same Level'
            last_end = child.start
            child.generate_same_level_paragraph()
            new_child.append(child)
        if last_end > self.start+1:
            new_child.append(CodeParagrah(self.start+1, last_end, self.indent_num, []))
            new_child[-1].type = 'Same Level'
        self.children = new_child

    def get_cpu_usage(self, cpu_usage_dict):
        if self.cpu_usage != None:
            return self.cpu_usage
        self.cpu_usage = 0.0
        last_end = self.end
        for child in self.children:
            self.cpu_usage += child.get_cpu_usage(cpu_usage_dict)
            for line_num in range(child.end, last_end):
                self.cpu_usage += cpu_usage_dict[line_num]
            last_end = child.start
        for line_num in range(self.start, last_end):
            self.cpu_usage += cpu_usage_dict[line_num]
        return self.cpu_usage

    def get_mem_usage(self, mem_usage_dict):
        if self.mem_usage != None:
            return self.mem_usage
        self.mem_usage = 0.0
        last_end = self.end
        for child in self.children:
            self.mem_usage += child.get_mem_usage(mem_usage_dict)
            for line_num in range(child.end, last_end):
                self.mem_usage += mem_usage_dict[line_num]
            last_end = child.start
        for line_num in range(self.start, last_end):
            self.mem_usage += mem_usage_dict[line_num]
        return self.mem_usage


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

def generate_cpu_dict(cpu_result):
    cpu_usage_dict = defaultdict(float)
    for func in cpu_result:
        for line in cpu_result[func]:
            cpu_usage_dict[line[0]] = line[1]
    return cpu_usage_dict

def generate_mem_dict(mem_result):
    mem_usage_dict = defaultdict(float)
    for func in mem_result:
        for line in mem_result[func]:
            mem_usage_dict[line[0]] = line[1]
    return mem_usage_dict

def parseMProf(profileName):
    """
    A map from function name to a tuple list.
    tuple: (line number, memory increment, code content)
    """
    with open(profileName, 'r') as f:
        lines = f.readlines()
    f.close()
    lineCount = 0
    memUse = defaultdict(list)
    while lineCount < len(lines):
        if lines[lineCount].startswith("Filename"):
            lineCount += 5
            lineSplit = lines[lineCount].split()
            funcName = lineSplit[2].split('(')[0]
            lineCount += 1
            while lines[lineCount] != "\n":
                lineSplit = lines[lineCount].split()
                if len(lineSplit) == 1:
                    lineCount += 1
                    continue
                lineNo = int(lineSplit[0])
                if len(lineSplit) < 3 or lineSplit[2] != "MiB":
                    memIncr = 0
                    lineCode = ' '.join(lineSplit[1:])
                    if lineCode.startswith('#'):
                        lineCount += 1
                        continue
                else:
                    memIncr = float(lineSplit[3])
                    lineCode = ' '.join(lineSplit[6:])
                memUse[funcName].append((lineNo, memIncr, lineCode))
                lineCount += 1
        lineCount += 1
    return memUse

def parseLineProf(profileName):
    """
    A map from function name to a list of tuple.
    tuple: (line number, total time, per time, time percentage, code content).
    total time = per time * function call times.
    all time = sum of total time.
    time percentage = total time / all time.
    """
    with open(profileName, 'r') as f:
        lines = f.readlines()
    f.close()
    lineCount = 2
    cpuUse = defaultdict(list)
    while lineCount < len(lines):
        if lines[lineCount].startswith("Total time"):
            lineCount += 7
            lineSplit = lines[lineCount].split()
            funcName = lineSplit[2].split('(')[0]
            lineCount += 1
            while lines[lineCount] != "\n":
                lineSplit = lines[lineCount].split()
                if len(lineSplit) == 1:
                    lineCount += 1
                    continue
                lineNo = int(lineSplit[0])
                if not lineSplit[1].isdigit():
                    cpuTime = 0
                    cpuPerTime = 0
                    cpuRatio = 0
                    lineCode = ' '.join(lineSplit[1:])
                    if lineCode.startswith('#'):
                        lineCount += 1
                        continue
                else:
                    cpuTime = float(lineSplit[2])
                    cpuPerTime = float(lineSplit[3])
                    cpuRatio = float(lineSplit[4])
                    lineCode = ' '.join(lineSplit[5:])
                cpuUse[funcName].append((lineNo, cpuTime, cpuPerTime, cpuRatio, lineCode))
                lineCount += 1
        lineCount += 1
    return cpuUse

def denote_paragraph(source_file, cpu_file, mem_file):
    cpu_result = parseLineProf(cpu_file)
    mem_result = parseMProf(mem_file)

    cpu_usage_dict = generate_cpu_dict(cpu_result)
    mem_usage_dict = generate_mem_dict(mem_result)

    f = open(source_file)
    lines = f.readlines()
    result = find_paragraph(lines)
    for r in result:
        if len(r[2]) != 0:
            r[2][0].generate_same_level_paragraph()
            r[2][0].get_cpu_usage(cpu_usage_dict)
            r[2][0].get_mem_usage(mem_usage_dict)
            # print(r[0], r[2][0].get_cpu_usage(cpu_usage_dict), r[2][0].get_mem_usage(mem_usage_dict))
    return result

if __name__ == '__main__':
    result = denote_paragraph("converter.py", "video_l_profile.txt", "video_m_profile.txt")