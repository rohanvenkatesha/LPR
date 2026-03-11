import re

STATES = ["AN","AP","AR","AS","BR","CH","DN","DD","DL","GA","GJ","HR",
          "HP","JK","KA","KL","LD","MP","MH","MN","ML","MZ","NL","OR",
          "PY","PN","RJ","SK","TN","TR","UP","WR"]

SPECIAL_CHARACTERS = ['.','!','#','$','%','&','@','[',']','_',' ']

def clean_plate_text(raw_texts, min_conf=0.5):
    cleaned = []
    for txt, conf in raw_texts:
        txt_upper = txt.upper()
        if "IND" not in txt_upper and conf > min_conf:
            for ch in SPECIAL_CHARACTERS:
                txt_upper = txt_upper.replace(ch, '')
            cleaned.append(txt_upper)
    return cleaned

def validate_indian_plate(plate):
    if any(plate.startswith(st) for st in STATES):
        pattern = r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$"
        return bool(re.match(pattern, plate)) and len(plate) >= 7
    return False