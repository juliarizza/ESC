comp = {
    '0'  : '0101010',
    '1'  : '0111111',
    '-1' : '0111010',
    'D'  : '0001100',
    'A'  : '0110000',
    '!D' : '0001101',
    '!A' : '0110001',
    '-D' : '0001111',
    '-A' : '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'D+A': '0000010',
    'D-A': '0010011',
    'A-D': '0000111',
    'D&A': '0000000',
    'D|A': '0010101',
    'M'  : '1110000',
    '!M' : '1110001',
    '-M' : '1110011',
    'M+1': '1110111',
    'M-1': '1110010',
    'D+M': '1000010',
    'D-M': '1010011',
    'M-D': '1000111',
    'D&M': '1000000',
    'D|M': '1010101'
}

dest = {
    'M'  : '001',
    'D'  : '010',
    'MD' : '011',
    'A'  : '100',
    'AM' : '110',
    'AMD': '111'
}

jump = {
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

def is_blank(line):
    empty_line = line == '\n'
    comment = line[:2] == '//'
    return empty_line or comment

def is_a_command(line):
    return line[0] == '@'

def is_label(line):
    return line[0] == '(' and line[-1] == ')'

def translate_a_command(line):
    value = line[1:]
    command = "0{0:015b}".format(int(value))
    return command

def translate_c_command(line):
    split_equal = line.split('=')
    dest_part = split_equal[0]
    comp_part = split_equal[1].replace('\n', '')
    command = "111{}{}000".format(comp[comp_part], dest[dest_part])
    return command

translation = []
with open('add\Add.asm', 'r') as file:
    for line in file:
        print(line)
        if is_blank(line):
            continue
        elif is_a_command(line):
            translation.append(translate_a_command(line))
        elif is_label(line):
            continue
        else:
            translation.append(translate_c_command(line))
    file.close()

with open('add\Add.hack', 'w') as file:
    for line in translation:
        file.write(line + '\n')
    file.close()
