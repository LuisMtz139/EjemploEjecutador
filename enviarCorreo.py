import csv
import os
import shutil
import xml.etree.ElementTree as ET
import re

class EnviarCorreo:
    def otro(self, escenario_id):
        
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.path = root.find('RutaCarpetas').text
        try:
            with open("escenario_ids.csv", "r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row: 
                        escenario_id = row[0]  # Save the last escenario_id
    
            if escenario_id is not None:
                full_path = os.path.join(self.path, escenario_id, 'timbrado')
                print(full_path)
    
                # Print the contents of the directory
                print("Contents of the directory:")
                for filename in os.listdir(full_path):
                    print(filename)
    
                # Copy procesados.txt to procesados2.txt
                shutil.copy(os.path.join(full_path, 'procesados.txt'), os.path.join(full_path, 'procesados2.txt'))
    
                # Read and validate the contents of procesados2.txt
                with open(os.path.join(full_path, 'procesados2.txt'), 'r') as file:
                    for line in file:
                        if line.count('|') == 5:
                            # Check if the last field is an email address
                            last_field = line.split('|')[-1].strip()
                            if re.match(r"[^@]+@[^@]+\.[^@]+", last_field):
                                print("Correct line:", line)
                                # Separate the line into different data and assign a letter from the alphabet to each data
                                data = line.split('|')
                                alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                for i, item in enumerate(data):
                                    print(f"{alphabet[i]}: {item}")
                            else:
                                print("Incorrect line (invalid email):", line)
                        else:
                            print("Incorrect line (wrong number of pipes):", line)
            else:
                print("No escenario_id found.")
        except FileNotFoundError:
            print("El archivo no existe.")