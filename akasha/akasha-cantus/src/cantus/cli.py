
import sys
from cantus.vm import CantusVM
from cantus.dsl import parse
from cantus.compiler import compile

def main():
    if len(sys.argv)<2:
        print("Usage: python -m cantus.cli program.cantus")
        return

    with open(sys.argv[1]) as f:
        source=f.read()

    tokens=parse(source)
    vm=CantusVM()
    result=vm.execute(tokens)

    print("Final Stack:",result)
    print("Bytecode:",compile(tokens))

if __name__=="__main__":
    main()
