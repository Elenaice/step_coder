#!/usr/bin/env python3
import re
import sys

def load_reverse_dictionary(dict_path):
    reverse_mapping = {}
    with open(dict_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '\t' in line:
                orig, short = line.split('\t')
                reverse_mapping[short] = orig
    return reverse_mapping

def expand_number(match):
    num = match.group(0)
    if '@' in num:
        parts = num.split('@')
        if len(parts) == 2:
            number_part = parts[0]
            zeros_to_add = int(parts[1])
            if '.' in number_part:
                int_part, frac_part = number_part.split('.')
                new_frac = frac_part + ('0' * zeros_to_add)
                return f'{int_part}.{new_frac}'
            else:
                return f'{number_part}.{"0" * zeros_to_add}'
    return num

def expand_digit_runs(text):
    def expand_run(match):
        digit = match.group(1)
        count = int(match.group(2))
        return digit * count
    
    return re.sub(r'\{(\d)(\d+)\}', expand_run, text)

def expand_sequences(text):
    text = re.sub(r'\(#(\d+)-#(\d+)\)', lambda m: '(' + ','.join([f'#{i}' for i in range(int(m.group(1)), int(m.group(2)) + 1)]) + ')', text)
    text = re.sub(r'#(\d+)-#(\d+)', lambda m: ','.join([f'#{i}' for i in range(int(m.group(1)), int(m.group(2)) + 1)]), text)
    return text

def restore_format(text):
    lines = text.split(';')
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r'\(', '( ', line)
        line = re.sub(r'\)', ' )', line)
        line = re.sub(r',', ', ', line)
        line = re.sub(r'=', ' = ', line)
        line = re.sub(r'\s+', ' ', line)
        result.append(line + ';')
    return '\n'.join(result)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 decoder.py <input.sstep> <output.step>")
        sys.exit(1)
    
    reverse_mapping = load_reverse_dictionary('dictionary.txt')
    
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    
    decoded = content

    for short, orig in sorted(reverse_mapping.items(), key=lambda x: len(x[0]), reverse=True):
        decoded = decoded.replace(short, orig)
    
    decoded = expand_sequences(decoded)
    
    decoded = re.sub(r'-?\d+\.?\d*@\d+', expand_number, decoded)
    
    decoded = expand_digit_runs(decoded)
    
    decoded = restore_format(decoded)
    
    with open(sys.argv[2], 'w') as f:
        f.write(decoded)

if __name__ == "__main__":
    main()
