def odd(n):
    if n == 0:
        return False
    return even(n-1)

def even(n):
    if n==0:
        return True
    return odd(n-1)

print(even(15))