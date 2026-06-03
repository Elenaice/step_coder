import re
import sys
import chardet

def load_dictionary(dict_path):
    mapping = {}
    with open(dict_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '\t' in line:
                orig, short = line.split('\t')
                mapping[orig] = short
    return mapping

def compress_number(match):
    num = match.group(0)
    if '.' in num:
        compressed = num.rstrip('0').rstrip('.')
        if compressed.endswith('.'):
            compressed += '0'
        return compressed
    return num

def compress_digit_runs(text):
    def replace_run(match):
        digits = match.group(0)
        digit = digits[0]
        count = len(digits)
        if count >= 4:
            return f'{{{digit}{count}}}'
        return digits
    
    return re.sub(r'(\d)\1{3,}', replace_run, text)

def compress_sequences(text):
    def replace_sequence(match):
        numbers = re.findall(r'#(\d+)', match.group(0))
        if len(numbers) < 3:
            return match.group(0)
        int_nums = [int(n) for n in numbers]
        if all(int_nums[i+1] - int_nums[i] == 1 for i in range(len(int_nums)-1)):
            return f'#{numbers[0]}-#{numbers[-1]}'
        return match.group(0)
    
    text = re.sub(r'(?:#\d+,?\s*){3,}', replace_sequence, text)
    text = re.sub(r'\(\s*#(\d+)-#(\d+)\s*\)', r'(#\1-#\2)', text)
    return text

def remove_name_arguments(text):
    entities = [
        'CARTESIAN_POINT', 'DIRECTION', 'VECTOR', 'LINE', 'CIRCLE', 'ELLIPSE',
        'PLANE', 'CYLINDRICAL_SURFACE', 'CONICAL_SURFACE', 'SPHERICAL_SURFACE',
        'TOROIDAL_SURFACE', 'VERTEX_POINT', 'EDGE_CURVE', 'ORIENTED_EDGE',
        'EDGE_LOOP', 'FACE_BOUND', 'ADVANCED_FACE', 'CLOSED_SHELL', 'MANIFOLD_SOLID_BREP'
    ]
    
    for entity in entities:
        pattern = r'\b' + re.escape(entity) + r'\s*\(\s*\'[^\']*\'\s*,'
        text = re.sub(pattern, entity + "('',", text)
    
    return text

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 encoder.py <input.step> <output.sstep>")
        sys.exit(1)
    
    mapping = load_dictionary('dictionary.txt')
    
    with open(sys.argv[1], 'rb') as f:
        raw_data = f.read()
        detected = chardet.detect(raw_data)
        encoding = detected['encoding'] or 'utf-8'
        content = raw_data.decode(encoding)
    
    encoded = content
    
    encoded = remove_name_arguments(encoded)
    
    for orig, short in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(orig) + r'\b'
        encoded = re.sub(pattern, short.replace('\\', '\\\\'), encoded)

    encoded = encoded.replace("'NONE'", "''")
    
    encoded = re.sub(r'-?\d+\.\d+', compress_number, encoded)
    
    encoded = compress_digit_runs(encoded)
    
    encoded = re.sub(r'\s*\(\s*', '(', encoded)
    encoded = re.sub(r'\s*\)\s*', ')', encoded)
    encoded = re.sub(r'\s*,\s*', ',', encoded)
    encoded = re.sub(r'\s*=\s*', '=', encoded)
    encoded = re.sub(r'[ \t]+', ' ', encoded)
    
    encoded = compress_sequences(encoded)
    
    encoded = encoded.strip()
    
    with open(sys.argv[2], 'w') as f:
        f.write(encoded)
    
    original_chars = len(content)
    encoded_chars = len(encoded)
    
    print(f'Original: {original_chars} chars')
    print(f'Compressed: {encoded_chars} chars')
    print(f'Compression: {(1 - encoded_chars/original_chars) * 100:.1f}%')

if __name__ == "__main__":
    main()
