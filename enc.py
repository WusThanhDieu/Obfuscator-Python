import ast
import base64
import python_minifier
import random
import zlib
import os
import sys

class Obfuscator:
    def __init__(self):
        self._map = {}
        self._counter = 0

    def fake_name(self, style: int = 1) -> str:
        self._counter += 1
        if style == 1:
            return f'{"O0" * (self._counter % 5)}' + ''.join(random.choice(['O0', 'O']) for _ in range(10)).replace('O', 'O0')
        elif style == 2:
            return f'{"O0" * (self._counter % 10)}' + ''.join(random.choice(['O0', 'O']) for _ in range(100)).replace('O', 'O0')
        else:
            raise ValueError("Invalid style selected.")

    @staticmethod
    def str_compress(s: str) -> str:
        compressed = zlib.compress(s.encode())
        ba64_enc = base64.b64encode(compressed).decode()
        return f"(lambda s: zlib.decompress(base64.b64decode(s)).decode())('{ba64_enc}')"

    def obfuscate(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                new_name = self.fake_name(1)
                self._map[node.name] = new_name
                node.name = new_name

        for node in ast.walk(tree):
            if isinstance(node, ast.arg):
                new_name = self.fake_name(2)
                self._map[node.arg] = new_name
                node.arg = new_name

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in self._map:
                node.id = self._map[node.id]

    def replace_str(self, code: str) -> str:
        tree = ast.parse(code)
        new_code = code
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                compressed_string = self.str_compress(node.value)
                new_code = new_code.replace(repr(node.value), compressed_string)

        return new_code

    @staticmethod
    def ensure_imports(code: str) -> str:
        imports = []
        if "import zlib" not in code:
            imports.append("import zlib")
        if "import base64" not in code:
            imports.append("import base64")
        if imports:
            return "\n".join(imports) + "\n" + code
        return code

    def execute(self, code: str) -> str:
        tree = ast.parse(code)
        self.obfuscate(tree)
        code = ast.unparse(tree)
        code = self.replace_str(code)
        code = self.ensure_imports(code)
        return code


class WusTeamObfuscator:
    def __init__(self):
        self.obfuscator = Obfuscator()
    def run(self):
        input_obf = input('Your file: ')
        rename_identifiers = input('Rename global? yes/no: ').strip().lower() == 'yes'
        output_obf = input_obf.rsplit('.', 1)[0] + '-obf.py'
        try:
            with open(input_obf, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: The file '{input_obf}' does not exist.")
            return
        confus = python_minifier.minify(self.obfuscator.execute(code), rename_globals=rename_identifiers, convert_posargs_to_args=True, remove_annotations=True)
        with open(output_obf, 'w', encoding='utf-8') as f:
            f.write(confus)
        print(f'Obfuscated code saved to: {output_obf}')
        sys.exit()

if __name__ == "__main__":
    app = WusTeamObfuscator()
    app.run()
