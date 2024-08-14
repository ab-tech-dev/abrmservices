import itertools
import multiprocessing

# Global variables
digits = "0123456789"
alphabets = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
characters = "!@#$%^&*()-_=+[]{}|;:',.<>?`~"
all_characters = digits + alphabets + characters
target_password = ""
attempts = multiprocessing.Value('i', 0)
found = multiprocessing.Value('b', False)

def brute_force_worker(length, start_idx, end_idx, charset):
    global attempts, found
    for guess in itertools.product(charset, repeat=length):
        if found.value:
            return
        guess_str = ''.join(guess)
        print(f"Trying: {guess_str}")
        with attempts.get_lock():
            attempts.value += 1
        if guess_str == target_password:
            with found.get_lock():
                found.value = True
            print(f"Password cracked! It is: {guess_str}")
            print(f"Number of attempts: {attempts.value}")
            return
        if attempts.value >= end_idx:
            return

def brute_force_password():
    """
    Brute force approach to match a password using multiprocessing.
    """
    total_combinations = sum(len(chars) ** length for length in range(1, 11) for chars in [digits, alphabets, characters]) + len(all_characters) ** 10
    chunk_size = total_combinations // multiprocessing.cpu_count()
    processes = []

    for length in range(1, 11):  # Attempting groups of one to ten characters
        for chars in [digits, alphabets, characters, all_characters]:
            start_idx = chunk_size * (length - 1)
            end_idx = chunk_size * length
            process = multiprocessing.Process(target=brute_force_worker, args=(length, start_idx, end_idx, chars))
            process.start()
            processes.append(process)

    for process in processes:
        process.join()

if __name__ == "__main__":
    target_password = input("Enter the target password: ")
    brute_force_password()
