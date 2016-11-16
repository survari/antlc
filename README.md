# antlc - AntLang Compiler

The AntLang Virtual Machine (AVM) takes ANT.ASM files as input and runs them.

This python script takes several ANT files and produces the corresponding ANT.ASM files.

Running ANT.ASM files is not the purpose of this module.

## Install

```sh
git clone https://github.com/antlang-software/antlc.git
```

## Run

### Command Line

```sh
python3 antlc.py some.ant
```

### Python 3

```python
import antlc
tokens = antlc.lexer('2+2')
ir = antlc.parser(tokens)
ant_asm = antlc.generate(ir)
```
