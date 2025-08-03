# repair_utils.py

def detect_common_error(traceback_text):
    if "ImportError" in traceback_text:
        return "import"
    elif "NameError" in traceback_text:
        return "undefined variable"
    elif "SyntaxError" in traceback_text:
        return "syntax"
    elif "KeyError" in traceback_text:
        return "missing dict key"
    return "unknown"

def adjust_prompt(prompt, error_type):
    if error_type == "import":
        return prompt + "\n⚠️ Ensure all imports are defined at the top."
    if error_type == "undefined variable":
        return prompt + "\n⚠️ Make sure all variables are declared before used."
    if error_type == "syntax":
        return prompt + "\n⚠️ Check indentation, colons, and parens."
    return prompt
