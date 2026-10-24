from golemLLM.core.client import GolemCLIENThttp
from golemLLM.core.proposal import GolemPROPOSAL, GolemPROPOSALparser

print("Running tests...")

CLIENT = GolemCLIENThttp()
PARSER = GolemPROPOSALparser(CLIENT)

proposal = PARSER.parse(54599)