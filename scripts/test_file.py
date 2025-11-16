# deepseek-code/test_file.py
#!/usr/bin/env python3
"""Test file for analysis"""

def calculate_fibonacci(n):
    """Calculate Fibonacci sequence"""
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    """Main function"""
    print("Fibonacci sequence:")
    for i in range(10):
        print(f"F({i}) = {calculate_fibonacci(i)}")

if __name__ == "__main__":
    main()