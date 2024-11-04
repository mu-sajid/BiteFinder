import json

class DataParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []

    def load_data(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        self.data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return self.data

    def get_documents(self):
        documents = []
        for business in self.data:
            documents.append({
                "name": business.get("name", ""),
                "categories": business.get("categories", "")
            })
        return documents
