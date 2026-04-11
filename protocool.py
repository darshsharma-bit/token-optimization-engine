from pydantic import BaseModel

# Defining the minimal ATP Header
class ATPHeader(BaseModel):
    s: str  # Sender ID (e.g., 'agent_coder')
    r: str  # Receiver ID (e.g., 'agent_tester')
    i: int  # Intent Code (1 = Task Request, 2 = Task Result, 3 = Error)

# Defining the full ATP Packet
class ATPPacket(BaseModel):
    h: ATPHeader
    p: str  # The heavily compressed semantic payload (Gibberish to humans, understood by LLMs)