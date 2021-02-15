import os

USER_TYPES_ = [
    'typedef',
    'class',
    'struct',
    'union',
    'enum'
]

C_TYPES_ = [
    'uint8_t',
    'int8_t',
    'uint16_t',
    'int16_t',
    'uint32_t',
    'int32_t',
    'uint64_t',
    'int64_t'
]

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

def insert_dict(dic: dict, pos, elem, lines):
        dic[pos] = {elem: lines}


def print_errors(dic: dict, file):
    file_name = file.replace('//', '/')
    if file.find('./src/') != -1:
        file_name = file.replace('./src/', '')+ ' |'

    for title, value in dic.items():
        for line, errors in value.items():
            print('\n============================================================')
            print(file_name, line, end=' ')
            for error, lines in errors.items():
                print(error, '('+ title.lower() + ')', '\n' ,lines)


def clear_errors(dic: dict):
    for key, value in dic.items():
        value.clear()


def is_func(line):
    flag = False
    for type in TYPES_:
        split_l = str(line).partition(' ')
        if split_l[0] == type:
            flag = True
            break
    if flag:
        if str(line).find('(') != -1 and str(line).find(')') != -1:
            return True
    return False


def in_string(line: str, symbol : str):
    if line.find('"') != -1:
        pos_string = line.find('"')
        if line.find(symbol) != -1 and \
                line.find(symbol) > pos_string and \
                line.find(symbol) < line.find('"', pos_string+1):
            return True
    return False


def is_empty_line(line: str):
    for char in line:
        if not char.isspace():
            return False
    return True


def make_header_guard(file, path):
    newPath = path.replace('//', '/')
    name = file.name.split('/')[-1]
    return str('ENGINE' + newPath.replace('/', '_').replace('.', '').upper() + '_' + name.split('.')[0].upper()
               + '_' + name.split('.')[1].upper() + '_')


def text_formatting(file, path):
    number = 1
    indent = 0
    last_indent = 0
    last_line = ''
    guard = ''
    count_empty_line = 0

    if file.name.find('.hpp') != -1:
        guard = make_header_guard(file, path)

    for line in file:
        hasOper = ''
        current_indent = 0
        typeInLine = ''
        userType = ''

        if is_empty_line(line):
            count_empty_line += 1

        if line.find('{') != -1 and line.find('namespace') == -1 and last_line.find('namespace') == -1:
            indent += 1
        elif line.find('}') != -1:
            indent -= 1

        for type in TYPES_:
            if line.find(type) != -1:
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
                insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.11', last_line + line)
                break
            else:
                break

        if current_indent != indent and line.find('{') == -1 and not is_empty_line(line):
            if current_indent > indent:
                insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |',
                            'Not enough whitespace',  last_line + line)
            else:
                insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |',
                            'Too many whitespace', last_line + line)

        if line.find('#ifndef') != -1 and file.name.find('.hpp') != -1 and line.split()[1] != guard and number == 1:
            insert_dict(ERRORS_.get('HEADER_FILES'), str(number) + ' line |', '3.2', last_line + line)

        if line.count(';') > 1 and line.find('for') == -1:
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.1', last_line + line)

        if is_func(line) and line.find('{') != -1 and line.find('}') != -1:
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.2', last_line + line)

        if line[len(line) - 2] == ' ' or line[len(line) - 2] == '\t':
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.3', last_line + line)

        if line.find('{') != -1 and line.find('{') != current_indent:
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.6', last_line + line)

        if len(line) > 140:
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.7', last_line + line)

        if line.find('#define') != -1:
            lst = line.replace('(', ' ').split()
            if not lst[1].isupper():
                insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.8', last_line + line)

        if current_indent != 0 and line[current_indent + 1] == '#':
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.9', last_line + line)

        if count_empty_line > 1:
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.10', last_line + line)
            count_empty_line = 0

        if line.find('const') != -1 and (line.find(typeInLine) < line.find('const')):
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.13', last_line + line)

        if len(userType) != 0:
            lst = line.split()
            if not lst[1][0].isupper():
                insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.15', last_line + line)

        if line.find('//') != -1 and line.find('//') != last_indent and not in_string(line, '//'):
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.16', last_line + line)

        if line.find('//') != -1 and not in_string(line, '//') and \
                last_line.find('//') != -1 and not in_string(last_line, '//'):
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.17', last_line + line)

        if len(hasOper) != 0:
            newLine = line.split('(')[1]
            if newLine.find(')'):
                newLine = newLine.replace(')', '')
            if hasOper == 'for':
                newLine = newLine.split(';')[0]
        else:
            newLine = line

        if str(typeInLine) != 0 and not is_func(newLine) and \
            newLine[newLine.find(typeInLine) + len(typeInLine)] == ' ' and \
            newLine[newLine.find(typeInLine) + len(typeInLine) + 1].isupper():
                insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.19', last_line + line)

        if line.find('.') != -1 and line[line.find('.') + 1].isdigit() and not line[line.find('.') - 1].isdigit():
            insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line |', '1.20', last_line + line)

        if line.find('main') != -1 and is_func(line) and file.name.find('.m') == -1:
            insert_dict(ERRORS_.get('EXTENSION'), 'extension |', '2.2', '')

        if len(typeInLine) != 0 and line[line.find(typeInLine) + len(typeInLine)] == ' ' and \
                ((line[line.find(typeInLine) + len(typeInLine) + 1] == '*') or
                 (line[line.find(typeInLine) + len(typeInLine) + 1] == '&')):
            insert_dict(ERRORS_.get('VARIABLE_DECLARATION'), str(number) + ' line |','5.5', last_line + line)

        if line.find('=') != -1 and not hasOper and \
                ((len(typeInLine) != 0 and line.find(typeInLine) > line.find('=')) or len(typeInLine) == 0):
            sep = line.split()
            variable = sep[0]
            if last_line.find(variable) != -1:
                insert_dict(ERRORS_.get('VARIABLE_DECLARATION'), str(number) + ' line |', '5.6', last_line + line)

        if line.find('using namespace') != -1:
            insert_dict(ERRORS_.get('NAMESPACE'), str(number) + ' line |', '7.1', last_line + line)

        if line.find('inline namespace') != -1:
            insert_dict(ERRORS_.get('NAMESPACE'), str(number) + ' line |', '7.2', last_line + line)

        if line.find('try') != -1 or line.find('throw') != -1:
            insert_dict(ERRORS_.get('EXCEPTIONS'), str(number) + ' line |', '8.1', last_line + line)

        if line.find('unsigned int') != -1:
            insert_dict(ERRORS_.get('BASIC_DATA_TYPES'), str(number) + ' line |', '12.1', last_line + line)

        for c_type in C_TYPES_:
            if line.find(c_type) != -1:
                insert_dict(ERRORS_.get('BASIC_DATA_TYPES'), str(number) + ' line |', '12.2', last_line + line)
        if not is_empty_line(line):
            last_line = line
        last_indent = current_indent
        number += 1

    if file.name.find('.h') != -1 and file.name.find('.hpp') == -1:
        insert_dict(ERRORS_.get('EXTENSION'), 'extension |', '2.1', '')


def find_valid_extension(name):
    for ext in EXTENSION_:
        if name.find(ext) != -1 and name.find("README") == -1:
            return ext
    return '.'


def check_files(paths, flag: bool):
    dir = os.listdir(path=paths)
    for file in dir:
        ext = find_valid_extension(str(file))
        if ext != '.':
            f = open(str(paths + '/' + file), 'r', encoding='utf-8')
            text_formatting(f, paths)
            f.close()


            if ERRORS_:
                flag = True
            if ERRORS_.get('EXTENSION') or ERRORS_.get('FORMATTING') :
                print('In ' + file + ' errors:')
                print_errors(ERRORS_, f.name)
            clear_errors(ERRORS_)


def main(paths: str):
    flag = False
    dir = os.walk(paths)
    for current in dir:
        paths = current[0]
        if paths.find('./.') != 0:
            for folder in range(1, len(current) - 1):
                for file in current[folder]:
                    check_files(current[0] + '/' + file, flag)

    if not flag:
        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    main('./')
