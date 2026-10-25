from golemLLM.core.client import GolemCLIENThttp
from golemLLM.core.parsing import GolemSHOT
from golemLLM.core.proposal import GolemPROPOSAL, GolemPROPOSALparser

print("Running tests...")

CLIENT = GolemCLIENThttp(verbose=True)
PARSER = GolemPROPOSALparser(CLIENT)

from difflib import ndiff

for i in range(54500, 54599):
    print(f"Testing proposal {i}")
    shot = GolemSHOT(i, CLIENT)

    text1 = repr(shot.command_classical)
    text2 = repr(PARSER.parse(shot.command_classical).to_command())

    diff = ndiff(text1, text2);

    missing_chars = [delta[2:] for delta in diff if delta.startswith('- ')]

    missing_string = "".join(missing_chars)

    if missing_string:
        print(f"Shot {i} missing: {missing_string}")
    else:
        print(f"Shot {i}: No difference")
