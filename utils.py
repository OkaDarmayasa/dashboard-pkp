def format_capaian(value):
    try:
        val = float(value)
        if 0 <= val <= 1:
            return f"{val * 100:.0f}%"
        else:
            return f"{val:.0f}" if val.is_integer() else str(val)
    except:
        return str(value)
