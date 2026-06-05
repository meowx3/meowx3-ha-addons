# antenna_diag.py

def evaluate(sats, snr):
    if sats < 4:
        return "Too few satellites - move antenna outside"

    if snr < 20:
        return "Low signal strength - reduce interference"

    if sats >= 8 and snr > 30:
        return "Excellent placement"

    return "Moderate performance"
