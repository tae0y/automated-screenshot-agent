import json
import dspy
from ..config import OLLAMA_URL
from .schema import OutputJSON

class WebAuditSig(dspy.Signature):
    """Produce JSON per schema from screenshot+markdown."""
    md = dspy.InputField()
    schema = dspy.InputField()
    json_out = dspy.OutputField()

def make_program(model_name: str):
    lm = dspy.OllamaLocal(model=model_name, endpoint=f"{OLLAMA_URL}")
    dspy.configure(lm=lm, max_tokens=2048)
    return dspy.ChainOfThought(WebAuditSig)

def run_trial(program, md: str, schema: dict) -> OutputJSON:
    r = program(md=md, schema=json.dumps(schema))
    j = json.loads(r.json_out)
    return OutputJSON(**j)
