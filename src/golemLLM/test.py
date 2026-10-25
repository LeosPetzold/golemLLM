from golemLLM.core.client import GolemCLIENThttp
from golemLLM.core.parsing import GolemSHOT
from golemLLM.core.proposal import GolemPROPOSAL, GolemPROPOSALparser

print("Running tests...")

CLIENT = GolemCLIENThttp(verbose=False)
PARSER = GolemPROPOSALparser(CLIENT)

for i in range(35880, 35880+15):
    #import time; time.sleep(5)  # GOLEM.fjfi.cvut.cz is a public resource and should be treated with care; honor operators' will to give out valuable data to the public.
    print(f"Testing proposal {i}")
    
    shot = GolemSHOT(i, CLIENT)

    text1 = repr(shot.command_classical)
    
    try: 
        text2 = repr(PARSER.parse(shot.command_classical).to_command())
    except Exception as e:
        print(f"Error parsing proposal {i}: {e}")
        text2 = "Error"

    with open(f"../tests/test_{i}.txt", "w") as f:
        f.write(text1 + "\n\n" + text2)
