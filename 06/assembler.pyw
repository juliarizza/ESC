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
    'null': '000',
    'M'   : '001',
    'D'   : '010',
    'MD'  : '011',
    'A'   : '100',
    'AM'  : '110',
    'AMD' : '111'
}

jump = {
    'null': '000',
    'JGT' : '001',
    'JEQ' : '010',
    'JGE' : '011',
    'JLT' : '100',
    'JNE' : '101',
    'JLE' : '110',
    'JMP' : '111'
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
    dest_part, comp_part, jump_part = split_line(line)
    command = "111{}{}{}".format(
        comp[comp_part], dest[dest_part], jump[jump_part]
    )
    return command

def split_line(line):
    split_equal = line.split('=')
    if not len(split_equal) > 1:
        dest_part = 'null'
        split_sc = split_equal[0].split(';')
        comp_part = split_sc[0]
        jump_part = split_sc[1].replace('\n', '')
    else:
        dest_part = split_equal[0]
        split_sc = split_equal[1].split(';')
        if not len(split_sc) > 1:
            comp_part = split_sc[0].replace('\n', '')
            jump_part = 'null'
        else:
            comp_part = split_sc[0]
            jump_part = split_sc[1].replace('\n', '')

    return dest_part, comp_part, jump_part

translation = []
with open('max/MaxL.asm', 'r') as file:
    for line in file:
        if is_blank(line):
            continue
        elif is_a_command(line):
            translation.append(translate_a_command(line))
        elif is_label(line):
            continue
        else:
            translation.append(translate_c_command(line))
    file.close()

with open('max/MaxL.hack', 'w') as file:
    for line in translation:
        file.write(line + '\n')
    file.close()
