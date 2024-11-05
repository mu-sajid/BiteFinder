import json
import math

class DataParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []
        self.dfs = {}
        self.idfs = {}
        self.doc_count = 0

    def load_data(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            for line in file:
                valid = False
                line = line.strip()
                if line:
                    try:
                        json_object = json.loads(line)
                        if 'attributes' in json_object and json_object['attributes'] is not None:
                            attributes = json_object['attributes']
                            restaurant_keywords = ['restaurantsgoodforgroups', 'restaurantstakeOut', 'restaurantsattire', 'restaurantstableservice', 'restaurantsdelivery']
                            for keyword in attributes.keys():
                                if(keyword in restaurant_keywords):
                                    valid = True
                    
                        if 'categories' in json_object and json_object['categories'] is not None and json_object['categories'] != "None":
                            categories_str = json_object['categories'].lower()
                            restaurant_keywords = ['restaurant', 'food', 'cafe', 'diner', 'eatery', 'bistro', 'grill', 'takeout', 'buffet', 'bar']
                            for keyword in restaurant_keywords:
                                if(keyword in categories_str):
                                    valid = True
                        
                        if(valid):
                            self.data.append(json_object)
                            self.doc_count += 1
                            self.update_dfs(json_object)
                    except json.JSONDecodeError:
                        continue
        self.update_idfs()
        return self.data

    def get_documents(self):
        documents = []
        for business in self.data:
            documents.append({
                "name": business.get("name", ""),
                "categories": business.get("categories", "")
            })
        return documents

    def update_dfs(self, json_data):
        if 'categories' in json_data and json_data['categories'] is not None and json_data['categories'] != "None":
            categories_str = json_data['categories'].lower().split(',')
            categories_set = set(categories_str)
            for category in categories_set:
                category = category.strip().lower() 
                result = self.dfs.get(category)
                if(result == None):
                    self.dfs[category] = 1
                else:
                    self.dfs[category] = self.dfs.get(category) + 1
        else:
            return

    def update_idfs(self):
        for category in self.dfs.keys():
            df = self.dfs.get(category)
            idf = math.log(self.doc_count / df)
            self.idfs[category] = idf

