# Conversion functions

def celsius_to_fahrenheit(c):
    return round((c * 9/5) + 32, 2)

def fahrenheit_to_kelvin(f):
    return round(((f - 32) * 5/9) + 273.15, 2)

def kelvin_to_celsius(k):
    return round(k - 273.15, 2)

# Main program demonstrating usage
def main():
    # Sample conversions
    c = 0
    f = 32
    k = 300

    f_result = celsius_to_fahrenheit(c)
    k_result = fahrenheit_to_kelvin(f)
    c_result = kelvin_to_celsius(k)

    # Function output format
    print(f"celsius_to_fahrenheit({c}) ➝ {f_result}")
    print(f"fahrenheit_to_kelvin({f}) ➝ {k_result}")
    print(f"kelvin_to_celsius({k}) ➝ {c_result}")
    
    print()  # for spacing

    # Human-readable temperature equivalents
    print(f"{c}°C = {f_result}°F")
    print(f"{f}°F = {k_result}K")
    print(f"{k}K = {c_result}°C")

# Run the main function
main()