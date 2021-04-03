import sys
import os
from splinter import Browser
import re
import binascii
import subprocess

MSVC_VCVARS32_PATH = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Auxiliary\\Build\\vcvars32.bat'

if len(sys.argv) < 2:
    print('Must provide the .cpp filepath | Exiting...')
    exit(-1)

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''

def read_string_offsets(content):
    result = {}

    for line in content:
        if line.startswith('$'):
            offset_id = line.split()[0]

            quote_start = line.find('\'') + 1
            quote_end = line.rfind('\'')

            string_value = line[quote_start:quote_end]
            result[offset_id] = string_value

    return result

def read_segments(content):
    segments = []

    while True:
        segment = find_between(content, '_TEXT	SEGMENT', '_TEXT	ENDS')
        if len(segment) == 0:
            break

        segments.append(segment)
        content = content.replace(segment, '', 1)
        content = content.replace('_TEXT	SEGMENT', '', 1)
        content = content.replace('_TEXT	ENDS', '', 1)

    return segments

def find_main_segment(segments):
    for segment in segments:
        if segment.find('PROC	; ShellcodeMain') != -1:
            return segment

    return ''

def sanitize_segment_code(segment):
    lines = segment.splitlines()
    sanitized_lines = []

    for line in lines:
        if line.find(';') != -1:
            line = line[:line.find(';')]

        if line.find('PROC') != -1 or line.find('ENDP') != -1:
            line = ''

        sanitized_lines.append((line.lstrip() + '\n'))

    return ''.join(sanitized_lines)

def replace_string_offsets(segment, string_offsets):
    # find a "mov DWORD PTR" instruction
    for line in segment.split('\n'):
        if len(line.split()) < 3:
            continue 

        line_contents = line.split()
        if line_contents[0] == 'mov' and line_contents[1] == 'DWORD' and line_contents[2] == 'PTR':
            # find all offset identifiers until the 'call DWORD PTR' instruction
            offsets_to_replace = []

            for shadow_line in segment[segment.find(line):].split('\n'):
                shadow_line_contents = shadow_line.split()
                if len(shadow_line_contents) < 3:
                    continue 

                if shadow_line_contents[0] == 'call' and shadow_line_contents[1] == 'DWORD' and shadow_line_contents[2] == 'PTR':
                    break

                if shadow_line_contents[0] == 'push' and shadow_line_contents[1] == 'OFFSET':
                    offset_id = shadow_line_contents[2]
                    offsets_to_replace.append(offset_id)

            available_registers = ['esi', 'ebx', 'ecx', 'edx']
            used_registers = []

            inserted_code = ''
            for offset in offsets_to_replace:
                inserted_code += 'push\t0x0\n' # null terminator
                string_value = string_offsets[offset]
                string_partitions = re.findall('....?', string_value)

                for part in string_partitions:
                    idx = string_partitions.index(part)
                    string_partitions[idx] = part[::-1]

                for part in reversed(string_partitions):
                    hexval = '0x' + binascii.hexlify(part.encode('utf-8')).decode('utf-8')
                    inserted_code += 'push\t' + hexval + '\n'

                available_register = ''
                for reg in available_registers:
                    if reg not in used_registers:
                        available_register = reg
                        used_registers.append(reg)
                        break

                inserted_code += 'mov\t' + available_register + ', esp\n\n'

                segment = segment.replace('push\tOFFSET ' + offset, 'push\t' + available_register)

            segment = segment.replace(line, line + '\n' + inserted_code)

    # return the corrected segment code
    return segment

filename = sys.argv[1][:-4]
compile_cmd = '\"{0}\" && cl /O0 /Od /FA \"{1}.cpp\"'.format(MSVC_VCVARS32_PATH, filename)

subprocess.call((compile_cmd))

content = []

with open('{}.asm'.format(filename)) as f:
    content = f.readlines()

string_offsets = read_string_offsets(content)
content = ''.join(content)
segments = read_segments(content)
main_segment = find_main_segment(segments)

if len(main_segment) == 0:
    print('Could not find the segment for ShellcodeMain function | Exiting...')
    exit(-2)

sanitized_segment = sanitize_segment_code(main_segment)
sanitized_segment = replace_string_offsets(sanitized_segment, string_offsets)

with open('{}.asm'.format(filename) , 'w') as f:
    f.write(sanitized_segment)

url = 'https://defuse.ca/online-x86-assembler.htm#disassembly'

executable_path = {'executable_path': 'chromedriver.exe'}
resulting_shellcode = ''

sanitized_segment = re.sub(r'[\t]', ' ', sanitized_segment)

with Browser('chrome', executable_path) as browser:
    browser.visit(url)

    input_field = browser.find_by_name('instructions')
    assemble_button = browser.find_by_value('Assemble')

    input_field.fill(sanitized_segment)
    assemble_button.click()
    resulting_shellcode = browser.find_by_xpath('/html/body/div[1]/div[3]/div[2]/div[2]/p[4]').text

final_output = 'const char shellcode[] = ' + resulting_shellcode + ';'
with open("shellcode.txt", "w") as output_file:
    output_file.write(final_output)

os.remove('{}.exe'.format(filename))
os.remove('{}.obj'.format(filename))

if len(sys.argv) < 3:
    os.remove('{}.asm'.format(filename))
