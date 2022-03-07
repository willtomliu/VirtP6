from collections import defaultdict


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


if __name__ == '__main__':
    parseLineProf("video_l_profile.txt")
    parseMProf("video_m_profile.txt")
