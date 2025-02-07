import csv

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_downloaded_sha256(downloaded_file_path):
    with open(downloaded_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['sha256'] for row in reader}

def preprocess_data(data, downloaded_sha256):
    return [(row['captions'].lower() if row['captions'] else '', row) for row in data if row['sha256'] in downloaded_sha256]

def search_objects(preprocessed_data, keyword):
    keyword = keyword.lower()
    matching_rows = [row for captions, row in preprocessed_data if keyword in captions]
    print(f"Found {len(matching_rows)} matching rows for keyword '{keyword}'.")
    for row in matching_rows:
        print(row)
    return matching_rows

if __name__ == "__main__":
    metadata_file_path = 'datasets/ObjaverseXL_sketchfab/metadata.csv'
    downloaded_file_path = 'datasets/ObjaverseXL_sketchfab/downloaded_0.csv'
    
    downloaded_sha256 = load_downloaded_sha256(downloaded_file_path)  # Load only downloaded objects
    data = load_data(metadata_file_path)  # Load metadata
    preprocessed_data = preprocess_data(data, downloaded_sha256)  # Filter metadata for downloaded objects
    
    while True:
        keyword = input("Enter a keyword to search (or type 'exit' to quit): ").strip()
        if keyword.lower() == 'exit':
            print("Exiting...")
            break
        search_objects(preprocessed_data, keyword)
