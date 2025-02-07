import csv

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def preprocess_data(data):
    return [(row['captions'].lower() if row['captions'] else '', row) for row in data]

def search_objects(preprocessed_data, keyword):
    keyword = keyword.lower()
    matching_rows = [row for captions, row in preprocessed_data if keyword in captions]
    print(f"Found {len(matching_rows)} matching rows for keyword '{keyword}'.")
    for row in matching_rows:
        print(row)
    return matching_rows

if __name__ == "__main__":
    file_path = 'datasets/ObjaverseXL_sketchfab/metadata.csv'
    data = load_data(file_path)  # Load file once into memory
    preprocessed_data = preprocess_data(data)  # Precompute lowercase captions for faster searches
    
    while True:
        keyword = input("Enter a keyword to search (or type 'exit' to quit): ").strip()
        if keyword.lower() == 'exit':
            print("Exiting...")
            break
        search_objects(preprocessed_data, keyword)
