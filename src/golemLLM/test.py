from golemLLM.core.client import GolemCLIENThttp
from golemLLM.core.parsing import GolemSHOT
from golemLLM.core.proposal import GolemPROPOSAL, GolemPROPOSALparser

print("Running tests...")

CLIENT = GolemCLIENThttp(verbose=True)
PARSER = GolemPROPOSALparser(CLIENT)

from difflib import unified_diff

for i in range(54500, 54599):
    print(f"Testing proposal {i}")
    shot = GolemSHOT(i, CLIENT)

    dif1 = repr(shot.command_classical)
    dif2 = repr(PARSER.parse(shot.command_classical).to_command())

    diff = list(unified_diff(
        dif1.splitlines(), 
        dif2.splitlines(), 
        fromfile='classical', 
        tofile='parsed', 
        lineterm=''
    ))

    if diff:
        print(f"Shot {i} difference:\n" + "\n".join(diff))
    else:
        print(f"Shot {i}: No difference")
