import os

file_path = 'C:/Users/Engr kester/Desktop/Work/WEB/ABRMS/static/png_files/cpics/img1.jpg'  # Replace with the actual file path
if os.path.isfile(file_path):
    print("Path is a file!")
    if os.path.exists(file_path):
        print("File exists!")
    else:
        print("File does not exist.")
else:
    print("Path is not a file or does not exist.")
