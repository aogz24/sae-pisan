import csv

def read_csv(file_path):
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        data = [row for row in csv_reader]
    return header, data

if __name__ == "__main__":
    file_path = 'data_20241223_1000000.csv'
    header, data = read_csv(file_path)
    print("Header:", header)
    print("Data:", data)