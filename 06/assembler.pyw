comp = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', '!D': '0001101',
    '!A': '0110001', '-D': '0001111', '-A': '0110011',
    'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
    'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
    'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
    'M': '1110000', '!M': '1110001', '-M': '1110011',
    'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
    'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000',
    'D|M': '1010101'
}

dest = {
    'null': '000', 'M': '001', 'D': '010', 'MD': '011',
    'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'
}

jump = {
    'null': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'
}

symbols = {
    'SP': '0', 'LCL': '1', 'ARG': '2', 'THIS': '3',
    'THAT': '4', 'R0': '0', 'R1': '1', 'R2': '2',
    'R3': '3', 'R4': '4', 'R5': '5', 'R6': '6',
    'R7': '7', 'R8': '8', 'R9': '9', 'R10': '10',
    'R11': '11', 'R12': '12', 'R13': '13', 'R14': '14',
    'R15': '15', 'SCREEN': '16384', 'KBD': '24576'
}

labels = {}
variables = {}

def filter_line(line):
    index = line.find('//')
    if index > -1:
        line = line[:index]
    line = line.replace('\n', '')
    line = line.strip()
    return line

def is_blank(line):
    return len(line) == 0

def is_a_command(line):
    return line[0] == '@'

def is_c_command(line):
    return line.find('=') > -1 or line.find(';') > -1

def is_label(line):
    return line[0] == '(' and line[-1] == ')'

def translate_a_command(value):
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
        jump_part = split_sc[1]
    else:
        dest_part = split_equal[0]
        split_sc = split_equal[1].split(';')
        if not len(split_sc) > 1:
            comp_part = split_sc[0]
            jump_part = 'null'
        else:
            comp_part = split_sc[0]
            jump_part = split_sc[1]

    return dest_part, comp_part, jump_part

def filter_variables(line):
    symbol = line[1:]
    if not symbol in symbols.keys() and not symbol in labels.keys():
        try:
            int(symbol)
        except:
            if len(variables) == 0:
                variables[symbol] = '16'
            elif not symbol in variables.keys():
                last_used_space = max([int(m) for m in variables.values()])
                variables[symbol] = str(last_used_space + 1)

def filter_label(line):
    return line.replace('(', '').replace(')', '')

def filter_symbols(line):
    symbol = line[1:]
    if symbol in symbols.keys():
        return symbols[symbol]
    elif symbol in labels.keys():
        return labels[symbol]
    elif symbol in variables.keys():
        return variables[symbol]
    else:
        return symbol

translation = []
with open('pong/Pong.asm', 'r') as file:
    line_counter = 0
    for line in file:
        line = filter_line(line)
        if is_blank(line):
            continue
        elif is_a_command(line):
            line_counter += 1
        elif is_c_command(line):
            line_counter += 1
        elif is_label(line):
            label = filter_label(line)
            labels[label] = line_counter
file.close()

with open('pong/Pong.asm', 'r') as file:
    for line in file:
        line = filter_line(line)
        if is_blank(line):
            continue
        elif is_a_command(line):
            filter_variables(line)
            value = filter_symbols(line)
            translation.append(translate_a_command(value))
        elif is_c_command(line):
            translation.append(translate_c_command(line))
file.close()

with open('pong/Pong.hack', 'w') as file:
    for line in translation:
        file.write(line + '\n')
file.close()
