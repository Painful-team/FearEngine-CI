import sys
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
  'EXTENSION': {}
}


FOLDERS_ = []


FLAG_ = False


def insert_dict(dic: dict, pos, elem):
  if len(dic) != 0 and pos in dic:
    dic[pos].insert(0, elem)
  else:
    dic[pos] = [elem]


def print_errors(dic: dict):
  print('============================')
  for key1, value1 in dic.items():
    print(key1)
    for key2, value2 in value1.items():
      print(key2, value2)
  print('============================')


def clear_errors(dic: dict):
  for key, value in dic.items():
    value.clear()


def is_func(line):
  for type in TYPES_:
    split_l = str(line).partition(' ')
    if split_l[0] == type:
      break
  if str(line).find('(') != -1 and str(line).find(')'):
    return True
  return False


def make_header_guard(file, path):
  if path.count('/') > 1:
    path[path.find('/')].replace('/', '')
  name = file.name.split('/')[-1]
  return str('ENGINE' + path.replace('/', '_').replace('.', '').upper() + '_' + name.split('.')[0].upper()
             + '_' + name.split('.')[1].upper() + '_')


def text_formatting(file, path):
  guard = ''

  if file.name.find('.h') != -1:
    guard = make_header_guard(file, path)

  number = 1
  last_line = str()
  space = 0

  for line in file:

    if line.find('#ifndef') != -1 and file.name.find('.h') != -1 and line.split().pop() != guard:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '3.2')

    if line.count(';') > 1 and line.find('for') == -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.1')

    if is_func(line) and line.find('{') != -1 and line.find('}') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.2')

    if line[len(line)-2] == ' ' or line[len(line)-2] == '\t':
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.3')

    if line.find('{') != -1 and line.find('{') != space:
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.6')

    if len(line) > 140:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.7')

    if line.find('#define') != -1:
      lst = line.replace('(', ' ').split()
      if not lst[1].isupper():
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.8')

    if line.find('#') != 0 and line.find('#') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.9')

    if line.isspace() and last_line.isspace():
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.10')

    for char in line:
      if char == ' ':
        space += 1
      elif char == '\t':
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.11')
      else:
        break

    for type in TYPES_:
      if line.find(type) < line.find('const') and line.find('const') != -1:
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.13')
        break

    for type in USER_TYPES_:
      if line.find(type) != -1:
        lst = line.split()
        if not lst[1][0].isupper():
          insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.15')
          break

    if line.find('//') == 0:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.16')

    if line.find('//') != -1 and last_line.find('//') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.17')

    for type in TYPES_:
      if line.find(type) != -1 and line.find('(') == -1:
        lst = line.split()
        if lst[1][0].isupper():
          insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.19')
          break

    if line.find('Float') != -1 and line.find('='):
      digit = line.find('.') - 1
      if not line[digit].isdigit():
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '1.20')

    if line.find('main') != -1 and is_func(line) and file.name.find('.m') == -1:
      insert_dict(ERRORS_.get('EXTENSION'), 'extension', '2.2')

    for type in TYPES_:
      if line.find(type) != -1 and (line.find('*') != -1 or line.find('&') != -1):
        if line[line.find(type) + len(type)] != '*':
          insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '5.5')
          break

    for type in TYPES_:
      if line.find(type) != -1 and not is_func(line) and line.find('=') == -1:
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '5.6')
        break

    if line.find('using namespace') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '7.1')

    if line.find('inline namespace') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '7.2')

    if line.find('try') != -1 or line.find('throw') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '8.1')

    if line.find('unsigned int') != -1:
      insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '12.1')

    for c_type in C_TYPES_:
      if line.find(c_type) != -1:
        insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '12.2')
        break

    if line.find('sizeof(') != -1:
      pos = line.find('sizeof(') + len('sizeof(')
      for type in TYPES_:
        if line.find(type) == pos:
          insert_dict(ERRORS_.get('FORMATTING'), str(number) + ' line', '15.1')
          break


    last_line = line
    number += 1
    space = 0

  if file.name.find('.h') != -1:
    insert_dict(ERRORS_.get('EXTENSION'), 'extension', '2.1')


def check_extension(name):
  for ext in EXTENSION_:
    if name.find(ext) != -1 and name.find("README") == -1:
      return ext
  return '.'


def check_files(paths):
  dir = os.listdir(path=paths)
  for file in dir:
    ext = check_extension(str(file))
    if ext != '.':
      f = open(str(paths + '/' + file), 'r', encoding='utf-8')
      text_formatting(f, paths)
      f.close()
      print('In ' + file + ' errors:')

      if ERRORS_:
        FLAG_ = True

      print_errors(ERRORS_)
      clear_errors(ERRORS_)


def main(paths: str):
    dir = os.walk(paths)
    for current in dir:
      paths = current[0]
      if paths.find('./.') != 0:
        for file in current[1]:
          check_files(current[0] + '/' + file)

    if FLAG_ == False:
      exit(1)
    else:
      exit(0)


if __name__ == '__main__':
    main('./')
