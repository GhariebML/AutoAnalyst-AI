import re
import json

def clean_llm_json(text: str) -> str:
    text = text.strip()
    
    # Remove markdown code block fences if present
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
            
    # Escape raw control characters inside string literals
    cleaned = []
    in_string = False
    escape = False
    for char in text:
        if char == '"' and not escape:
            in_string = not in_string
            cleaned.append(char)
        elif char == '\\' and in_string:
            escape = not escape
            cleaned.append(char)
        else:
            if escape:
                escape = False
            if in_string:
                if char == '\n':
                    cleaned.append('\\n')
                elif char == '\r':
                    cleaned.append('\\r')
                elif char == '\t':
                    cleaned.append('\\t')
                else:
                    cleaned.append(char)
            else:
                cleaned.append(char)
                
    text = "".join(cleaned)
    
    # Remove trailing commas before closing braces/brackets
    text = re.sub(r',(\s*[\]\}])', r'\1', text)
    
    return text

# Test cases
test_cases = [
    # Trailing commas
    ('{"name": "test",}', '{"name": "test"}'),
    # Raw newlines in string
    ('{"desc": "hello\nworld"}', '{"desc": "hello\\nworld"}'),
    # Complex case with escaped quotes and trailing comma
    ('{"desc": "hello \\"world\\"\\nand more", "list": [1, 2, ],}', '{"desc": "hello \\"world\\"\\nand more", "list": [1, 2]}')
]

for i, (inp, expected) in enumerate(test_cases):
    cleaned = clean_llm_json(inp)
    try:
        parsed = json.loads(cleaned)
        print(f"Test {i} PASSED: parsed successfully as {parsed}")
    except Exception as e:
        print(f"Test {i} FAILED: {e}\nInput: {inp}\nCleaned: {cleaned}")
