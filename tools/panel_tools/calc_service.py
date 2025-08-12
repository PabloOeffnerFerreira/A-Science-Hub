from tools.panel_tools.simple_calc import SafeEvaluator

_e = SafeEvaluator()

def evaluate(text: str):
    return _e.evaluate(text)

def variables():
    return dict(sorted(_e.get_variables().items(), key=lambda kv: kv[0]))

def set_var(name: str, value: float):
    _e.set_variable(name, value)

def delete_var(name: str):
    _e.delete_variable(name)

def reset_vars():
    _e.reset_variables()
