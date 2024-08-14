def generate_permutations():
    from itertools import permutations
    
    with open("wordlist.txt", "w") as file:
        for r in range(1, 11):  # Generate permutations from 1 to 10 values
            for perm in permutations(range(10), r):
                file.write("".join(map(str, perm)) + "\n")
        
        for r in range(1, 11):  # Generate permutations from 1 to 10 alphabets
            for perm in permutations("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", r):
                file.write("".join(perm) + "\n")
                
        for r in range(1, 11):  # Generate permutations from 1 to 10 special characters
            special_characters = "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?"
            for perm in permutations(special_characters, r):
                file.write("".join(perm) + "\n")

        for r in range(1, 11):  # Generate permutations from 1 to 10 signs
            signs = "~`"
            for perm in permutations(signs, r):
                file.write("".join(perm) + "\n")
                
        for r in range(1, 11):  # Generate permutations from 1 to 10 of all combined
            combined_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?0123456789~`"
            for perm in permutations(combined_characters, r):
                file.write("".join(perm) + "\n")

if __name__ == "__main__":
    generate_permutations()
