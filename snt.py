import os
import random

from colorama import init
from colorama import Fore, Back, Style
from datetime import datetime
from ast import literal_eval
init()

def get_time():
    time = datetime.now()
    hour = str(time.hour)
    minute = str(time.minute)
    if len(minute) == 1:
        minute = '0' + minute
    return hour + ':' + minute

def log(text):
    print(f'{Style.DIM}{Fore.CYAN}[{get_time()}]{Fore.RESET}{Style.RESET_ALL} {text}')

def success(text):
    print(f'{Style.DIM}{Fore.LIGHTGREEN_EX}[{get_time()}]{Fore.RESET}{Style.RESET_ALL} {text}')

def error(text):
    print(f'{Style.DIM}{Fore.LIGHTRED_EX}[{get_time()}]{Fore.RESET}{Style.RESET_ALL} {text}')

def normalizeType(text):
    if text.startswith('"') and text.endswith('"') or text.startswith("'") and text.endswith("'"):
        if text.startswith('"') and text.endswith('"'):
            return text.strip('"')
        elif text.startswith("'") and text.endswith("'"):
            return text.strip("'")
    else:
        try:
            return int(text)
        except:
            return f'%{text}%'

def setType(text):
    if text.startswith('%') and text.endswith('%'):
        return text.strip('%')
    elif isinstance(text, str):
        return '"' + text + '"'
    else:
        return str(text)

class SNT:
    def __init__(self, path:str = '', indent:str = 'none'):
        self.__indent = indent
        self.__file_found = True
        if path.endswith('/') or path == '':
            self.__path = path + 'database.snt'
        elif path.endswith('.snt'):
            self.__path = path

        path = self.__path.split('/')

        for word in path:
            if word.endswith('.snt'):
                self.name = word.strip('.snt').upper()

        for word in path:
            if word.endswith('.snt'):
                self.file = word

        if not os.path.exists(self.__path):
            self.__file_found = False
        
        if self.__file_found:
            success(f'Database «{self.name}» connected')
        else:
            error(f'File «{self.file}» not found')
        
        data = self.__read()
        if self.__file_found:
            self.__data = data[0]
            if indent == 'none':
                self.__indent = data[1]
            else:
                self.__indent = indent
        else:
            self.__data = {}

    @property
    def path(self):
        return self.__path

    @property
    def print_path(self):
        log(self.__path)
    
    def __get_data(self, data):
        data = str(data)
        for variable, value in self.__data.items():
            if variable.startswith('%variable') and variable.endswith('%'):
                data = data.replace(f'%{value[0]}%', value[1])
        data = literal_eval(data)
        for element in self.__data:
            if element.startswith('%variable') and element.endswith('%'):
                data.pop(element)
        return data

    @property
    def data(self):
        return self.__get_data(self.__data)

    def help(self):
        log('create')

    def __read(self):
        if self.__file_found:
            with open(self.__path, 'r') as file:
                text = file.read()
                return self.to_dict(text)

    def set(self, object):
        if self.__file_found:
            for element, value in object.items():
                self.__data[element] = value
                log(f'«{element}» seted')

    def update(self, object):
        if self.__file_found:
            if 'class' in object['names'] and object['names']['class'] in self.__data:
                element = object['names']['class']
                if 'object' in object['names'] and object['names']['object'] in self.__data[object['names']['class']]:
                    objectt = object['names']['object']
                    if 'item' in object['names'] and object['names']['item'] in self.__data[object['names']['class']][object['names']['object']]:
                        self.__data[object['names']['class']][object['names']['object']][object['names']['item']] = object['update']
                        item = object['names']['item']
                        log(f'«{element}~>{objectt}~>{item}» has been updated')
                        return True
                    self.__data[object['names']['class']][object['names']['object']] = object['update']
                    log(f'«{element}~>{objectt}» has been updated')
                    return True
                self.__data[object['names']['class']] = object['update']
                log(f'«{element}» has been updated')
                return True
    
    def add(self, object):
        if self.__file_found:
            if 'class' in object['names'] and object['names']['class'] in self.__data:
                el = object['names']['class']
                if 'object' in object['names'] and object['names']['object'] in self.__data[object['names']['class']]:
                    obj = object['names']['object']
                    for element, value in object['adding'].items():
                        self.__data[object['names']['class']][object['names']['object']][element] = value
                        log(f'«{element}» added to «{el}~>{obj}»')
                    return True
                for element, value in object['adding'].items():
                    self.__data[object['names']['class']][element] = value
                    log(f'«{element}» added to «{el}»')
                return True
    
    def remove(self, object):
        if self.__file_found:
            if 'class' in object['names'] and object['names']['class'] in self.__data:
                el = object['names']['class']
                if 'object' in object['names'] and object['names']['object'] in self.__data[object['names']['class']]:
                    obj = object['names']['object']
                    if 'item' in object['names'] and object['names']['item'] in self.__data[object['names']['class']][object['names']['object']]:
                        item = object['names']['item']
                        del self.__data[object['names']['class']][object['names']['object']][object['names']['item']]
                        log(f'«{el}~>{obj}~>{item}» removed')
                        return True
                    del self.__data[object['names']['class']][object['names']['object']]
                    log(f'«{el}~>{obj}» removed')
                    return True
                del self.__data[object['names']['class']]
                log(f'«{el}» removed')
                return True

    def save(self):
        if self.__file_found:
            with open(self.__path, 'w') as file:
                file.write(self.stringify(self.__data, self.__indent))
            log('SNT saved')

    def stringify(self, object, indent:str = ' '):
        tokens = {
            'class': {},
            'object': {},
            'item': {}
        }
        result = f'property indent: "{indent}"\n\n'
        for element, value in object.items():
            if element.startswith('%variable') and element.endswith('%'):
                result += f'variable {value[0]}: {setType(value[1])}\n'
            else:
                result += element + ':\n'
                if not element.startswith('%variable') and not element.endswith('%'):
                    for object, value in value.items():
                        result += indent + object + ':\n'
                        for item, value in value.items():
                            result += indent + indent + item + ': ' + setType(value) + '\n'
                        result += indent + indent + 'end\n'
                result += indent + 'end\n'

        return result

    def to_dict(self, snt):
        snt = snt.split('\n')
        tokens = {}
        is_first = True
        indent = ' '
        temp = ['', '', '']
        for index, line in enumerate(snt):
            if not line.endswith(':') and line.startswith('property'):
                line = line.split(' ', 2)
                property = line[1].rstrip(':')
                if property == 'indent':
                    indent = line[2].strip('"').strip("'")
            elif not line.endswith(':') and line.startswith('variable'):
                line = line.split(' ', 2)
                tokens[f'%variable{random.randint(1, 1000000)}%'] = [line[1].rstrip(':'), normalizeType(line[2])]
            elif line == temp[2] + 'end':
                temp[2] = temp[2].split(indent, 1)[1]
            elif line.endswith(':') and not line.startswith(indent):
                temp[2] += indent
                tokens[line.rstrip(':')] = {}
                temp[0] = line.rstrip(':')
            elif line.endswith(':') and line.startswith(temp[2]):
                temp[1] = line.rstrip(':').lstrip(temp[2])
                tokens[temp[0]][line.rstrip(':').lstrip(temp[2])] = {}
                temp[2] += indent
            elif line and not line.isspace():
                try:
                    line = line.lstrip(temp[2])
                    line = line.split(':', 1)
                    tokens[temp[0]][temp[1]][line[0]] = normalizeType(line[1].strip())
                except IndexError as e:
                    error('SyntaxError: Invalid component or indent specified')
                    return [{}, ' ', {}]
        return [tokens, indent]