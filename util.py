'''
Utilities file for Benford's law validator webapp
'''
from detect_delimiter import detect

# Detect and return delimiter
def getDelim(decoded):
    line = decoded.decode("utf-8").partition("\n")[0]
    delim = detect(line)
    return delim

# Verbalize conformity based on value
def getConformity(mad):
    conformity_boundaries = {
        "close conformity": [0.000, 0.006],
        "acceptable conformity": [0.006, 0.012],
        "marginal conformity": [0.012, 0.015],
        "non-conformity": [0.015, 1],
    }
    for bound in conformity_boundaries:
        if (
            mad >= conformity_boundaries[bound][0]
            and mad <= conformity_boundaries[bound][1]
        ):
            conformity=bound
    return conformity

# Expected values for Bedford's law
expected = [
    0.301030,
    0.176091,
    0.124939,
    0.096910,
    0.079181,
    0.066947,
    0.057992,
    0.051153,
    0.045757,
]
