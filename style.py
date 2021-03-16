import os
import re

USER_TYPES_ = [
    'typedef',
    'class',
    'struct',
    'union',
    'enum'
]

C_TYPES_ = {
    'short': 'int16_t',
    'unsigned short': 'uint16_t',
    'long long': 'int64_t',
    'unsigned long long': 'uint64_t/size_t',
    'unsigned': 'uint32_t',
}

TYPES_ = [
    'void',
    'int',
    'char',
    'bool',
    'signed',
    'unsigned',
    'short',
    'long',
    'float',
    'double'
]

EXTENSION_ = [
    '.cpp',
    '.c',
    '.m',
    '.hpp',
    '.h'
]

ERRORS_ = {
    'FORMATTING': {},
    'EXTENSION': {},
    'HEADER_FILES': {},
    'VARIABLE_DECLARATION': {},
    'NAMESPACE': {},
    'EXCEPTIONS': {},
    'BASIC_DATA_TYPES': {},
}

OPERATORS_ = [
    'while',
    'for',
    'if',
]


class Pair:
    def __init__(self):
        self.first_elem = -1
        self.second_elem = -1

    def is_empty(self):
        return self.first_elem == -1 or self.second_elem == -1


def insert_dict(dic: str, pos, elem, lines):
        ERRORS_.get(dic)[pos] = {elem: lines}


def print_errors(dic: dict, file):
    file_name = file.replace('//', '/')
    if file_name.find('./src/') != -1:
        file_name = file_name.replace('./src/', '') + ' |'

    for title, value in dic.items():
        for line, errors in value.items():
            print('\n============================================================')
            print(file_name, line, end=' ')
            for error, lines in errors.items():
                print(error, '(' + title.lower() + ')', '\n' ,lines)


def clear_errors(dic: dict):
    for key, value in dic.items():
        value.clear()


def is_lambda(line: str):
    return re.search('(\[[\w\s\*&=,]*\])\s?([\w\s\.,<>:]*)(\([\w\s\*&=,]*\))', line) != None


def is_func(line, symbol = '', inFunc = False):
    hasType = False
    for type in TYPES_:
        split_l = str(line).partition(' ')
        if split_l[0] == type:
            hasType = True
            break
    if not inFunc:
        return hasType and str(line).find('(') != -1 and str(line).find(')') != -1
    else:
        return hasType and str(line).find('(') != -1 and str(line).find(')') != -1 and\
               line.find('(') < line.find(symbol) and line.find(')') > line.find(symbol)


def string_position(line: str):
    pos = Pair()
    if (line.find('"') != -1 and line.count('"') % 2 == 0) \
            or (line.find('"') != -1 and line.find('\\') > line.find('"')):
        pos.first_elem = line.find('"')
        pos.second_elem = line.find('"', pos.first_elem + 1)
    return pos


def is_empty_line(line: str):
    for char in line:
        if not char.isspace():
            return False
    return True


def is_empty_errors(dic: dict):
    for title, value in dic.items():
        if len(value) != 0:
            return False
    return True


def find_all(a_str, sub):
    start = 0
    pos = []
    while True:
        start = a_str.find(sub, start)
        if start == -1: break
        pos.insert(0, start)
        start += len(sub)
    return pos


def is_between(line: str, pos: Pair, sub_line: str):
    return line.find(sub_line) != -1 and line.find(sub_line) > pos.first_elem and line.find(sub_line) < pos.second_elem


def in_string_or_comment(line:str, pos_str: Pair, pos_comment: int, sub_line):
    return (pos_comment != -1 or not pos_str.is_empty()) and \
            (is_between(line, pos_str, sub_line) or line.find(sub_line) > pos_comment)


def make_header_guard(file, path):
    name = file.name.split('/')[-1]
    return str('ENGINE' + path.replace('/', '_').replace('.', '').upper() + '_' + name.split('.')[0].upper()
               + '_' + name.split('.')[1].upper() + '_')


def text_formatting(file, path):
    number = 1
    indent = 0
    last_indent = 0
    last_line = ''
    count_empty_line = 0
    hasComm = False
    inSwitch = False
	lines = file.readlines()
    print(lines[-1])
    for line in lines:
        pos_comment = -1
        pos_string = string_position(line)
        hasOper = ''
        current_indent = 0
        typeInLine = ''
        userType = ''

        pos = Pair()
        pos.first_elem = line.find('(')
        pos.second_elem = line.find(')')

        if line.find('switch') != -1:
            inSwitch = True
        elif line.find('}') != -1 and inSwitch:
            inSwitch = False

        if line.find('//') != -1 and not pos_string.is_empty() or \
                not is_between(line, pos_string, '//'):
            pos_comment = line.find('//')

        if line.find('= R"') != -1 and not in_string_or_comment(line, pos_string, pos_comment, '= R"'):
            hasComm = True
        elif line.find('"') != -1:
            hasComm = False
        if hasComm:
            continue

        if is_empty_line(line):
            count_empty_line += 1
        else:
            count_empty_line = 0

        if line.find('{') != -1 and line.find('namespace') == -1 and last_line.find('namespace') == -1 and \
                not is_between(line, pos, '{'):
            indent += 1
        elif line.find('}') != -1 and not is_between(line, pos, '}'):
            indent -= 1

        for type in TYPES_:
            if re.search('\s?(' + type + ')\W?', line) != None:
                typeInLine = type
                break

        for type in USER_TYPES_:
            if line.find(type) != -1:
                userType = type
                break

        for operator in OPERATORS_:
            if line.find(operator) != -1 and (line.find('#') == -1 or line.find('#') > line.find(operator)):
                hasOper = operator
                break

        for char in line:
            if char == '\t':
                current_indent += 1
            elif char == ' ':
                insert_dict('FORMATTING', str(number) + ' line |', '1.11', last_line + line)
                break
            else:
                break

        if current_indent != indent and line.find('{') == -1 and not is_empty_line(line) and not inSwitch:
            if current_indent < indent:
                insert_dict('FORMATTING', str(number) + ' line |',
                            'Not enough whitespace',  last_line + line)
            else:
                insert_dict('FORMATTING', str(number) + ' line |',
                            'Too many whitespace', last_line + line)

        if line.find('#ifndef') != -1 and file.name.find('.hpp') != -1 and \
                line.split()[1] != make_header_guard(file, path) and number == 1:
            insert_dict('HEADER_FILES', str(number) + ' line |', '3.2', last_line + line)

        if line.count(';') > 1 and line.find('for') == -1:
            insert_dict('FORMATTING', str(number) + ' line |', '1.1', last_line + line)

        if (is_func(line) or is_lambda(line)) and line.find('{') != -1 and line.find('}') != -1:
            insert_dict('FORMATTING', str(number) + ' line |', '1.2', last_line + line)

        if line[len(line) - 2] == ' ' or line[len(line) - 2] == '\t':
            insert_dict('FORMATTING', str(number) + ' line |', '1.3', last_line + line)

        if line.find('{') != -1 and line.find('{') != current_indent and \
                (not is_between(line, pos, '{') or (line.find('=') != -1 and line.find('=') < line.find('{'))):
            insert_dict('FORMATTING', str(number) + ' line |', '1.6', last_line + line)

        if len(line) > 140:
            insert_dict('FORMATTING', str(number) + ' line |', '1.7', last_line + line)

        if line.find('#define') != -1:
            lst = line.replace('(', ' ').split()
            if not lst[1].isupper():
                insert_dict('FORMATTING', str(number) + ' line |', '1.8', last_line + line)

        if current_indent != 0 and line[current_indent + 1] == '#':
            insert_dict('FORMATTING', str(number) + ' line |', '1.9', last_line + line)

        if count_empty_line > 1:
            insert_dict('FORMATTING', str(number) + ' line |', '1.10', last_line + line)

        for type in TYPES_:
            if re.search('\s?(' + type + ' const)\W?', line) and not in_string_or_comment(line, pos_string, pos_comment, 'const'):
                insert_dict('FORMATTING', str(number) + ' line |', '1.13', last_line + line)
                break

        if len(userType) != 0:
            lst = line.split()
            if not lst[1][0].isupper():
                insert_dict('FORMATTING', str(number) + ' line |', '1.15', last_line + line)

        if line.find('//') != -1 and line.find('//') != last_indent \
                and not pos_string.is_empty() and not is_between(line, pos_string , '//'):
            insert_dict('FORMATTING', str(number) + ' line |', '1.16', last_line + line)

        if line.find('//') != -1 and not pos_string.is_empty() and not is_between(line, pos_string , '//') and \
                last_line.find('//') != -1 and not pos_string.is_empty() and not is_between(last_line, pos_string , '//'):
            insert_dict('FORMATTING', str(number) + ' line |', '1.17', last_line + line)

        if len(hasOper) != 0 and not in_string_or_comment(line, pos_string, pos_comment, hasOper):
            splitLine = line.split('(', maxsplit = 1)[1]
            if hasOper == 'for':
                splitLine = splitLine.split(';')[0][len(hasOper):].split(',')
        else:
            splitLine = [line]

        for part in splitLine:
            if len(typeInLine) != 0 and not is_func(line) and not in_string_or_comment(line, pos_string, pos_comment, typeInLine) and \
                    ((line.find('(') != -1 and line.find('=') > line.find('(')) or line.find('(') == -1):
                for var in splitLine:
                    arr = var.split(' ')
                    for i in arr:
                        if (i and i[0] != '*' and i[0] != '&' and i[0].isupper()):
                            insert_dict('FORMATTING', str(number) + ' line |', '1.19', last_line + line)


        if line.find('.') != -1 and not in_string_or_comment(line, pos_string, pos_comment, '.'):
            positions = find_all(line, '.')
            for pos in positions:
                if line[pos + 1].isdigit() and not line[pos - 1].isdigit():
                    insert_dict('FORMATTING', str(number) + ' line |', '1.20', last_line + line)

        if re.search('\s?(main)\W?', line) != None and is_func(line) and file.name.find('.m') == -1:
            insert_dict('EXTENSION', 'extension |', '2.2', '')

        if len(typeInLine) != 0 and line[line.find(typeInLine) + len(typeInLine)].isspace() and \
                ((line[line.find(typeInLine) + len(typeInLine) + 1] == '*') or
                 (line[line.find(typeInLine) + len(typeInLine) + 1] == '&')) and \
                (not in_string_or_comment(line, pos_string, pos_comment, '*') or not in_string_or_comment(line, pos_string, pos_comment, '&')):
            insert_dict('VARIABLE_DECLARATION', str(number) + ' line |','5.5', last_line + line)

        if line.find('=') != -1 and not hasOper and \
                ((len(typeInLine) != 0 and line.find(typeInLine) > line.find('=')) or len(typeInLine) == 0):
            sep = line.split()
            variable = sep[0]
            if last_line.find(variable) != -1 and last_line.find(";") == last_line.find(variable) + len(variable):
                insert_dict('VARIABLE_DECLARATION', str(number) + ' line |', '5.6', last_line + line)

        if line.find('using namespace') != -1 and not in_string_or_comment(line, pos_string, pos_comment, 'using namespace'):
            insert_dict('NAMESPACE', str(number) + ' line |', '7.1', last_line + line)

        if line.find('inline namespace') != -1 and not in_string_or_comment(line, pos_string, pos_comment, 'inline namespace'):
            insert_dict('NAMESPACE', str(number) + ' line |', '7.2', last_line + line)

        if ((re.search('\s?(try)\W?',line) != None and not in_string_or_comment(line, pos_string, pos_comment, 'try')) or
                (re.search('\s?(throw)\W?', line) != None and not in_string_or_comment(line, pos_string, pos_comment, 'throw'))):
            insert_dict('EXCEPTIONS', str(number) + ' line |', '8.1', last_line + line)

        for type, c_type in C_TYPES_.items():
            if line.find(type) != -1 and not in_string_or_comment(line, pos_string, pos_comment, type):
                insert_dict('BASIC_DATA_TYPES', str(number)
                            + ' line |', '12.2 | ' + c_type + 'should be here ', last_line + line)

        if not is_empty_line(line):
            last_line = line
        last_indent = current_indent
        number += 1
	
	if lines[-1][-1] != '\n':
	    insert_dict('EXCEPTIONS', 'The file must end with an end-of-line character |', '1.4')
    if file.name.find('.h') != -1 and file.name.find('.hpp') == -1:
        insert_dict('EXTENSION', 'extension |', '2.1', '')


def find_valid_extension(name):
    for ext in EXTENSION_:
        if name.find(ext) != -1 and name.find('.md') == -1:
            return ext
    return '.'


def check_files(paths):
    is_empty_ = True
    for file in os.listdir(path=paths):
        if find_valid_extension(str(file)) != '.':
            f = open(str(paths + '/' + file), 'r', encoding='utf-8')
            text_formatting(f, paths)
            print("File checked: ", f.name)
            if not is_empty_errors(ERRORS_):
                is_empty_ = False
                print('In ' + file + ' errors:')
                print_errors(ERRORS_, f.name)
            clear_errors(ERRORS_)
            f.close()

    return is_empty_


def main(paths: str):
    is_empty_ = True
    for current in os.walk(paths):
        is_empty_ = check_files(current[0] + '/')

    if not is_empty_:
        return 1
    else:
        return 0


if __name__ == '__main__':
    main('/__w/fear-engine/fear-engine')
