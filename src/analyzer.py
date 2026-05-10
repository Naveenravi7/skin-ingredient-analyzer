import pandas as pd
from thefuzz import process
import re
import os
import random
try:
    from PIL import Image
    import pytesseract
    import cv2
    import numpy as np
except ImportError:
    pass

class IngredientAnalyzer:
    def __init__(self, db_path='data/ingredients_db.csv'):
        self.db_path = db_path
        
        try:
            self.db = pd.read_csv(self.db_path)
            self.ingredient_names = self.db['Ingredient'].tolist()
        except Exception as e:
            print(f"Error loading database: {e}")
            self.db = pd.DataFrame()
            self.ingredient_names = []



    def extract_text_from_image(self, image_file):
        """Uses OCR to extract text from an uploaded image."""
        try:
            # Convert uploaded file to OpenCV format
            file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            
            # Preprocessing for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Use Tesseract to get text
            text = pytesseract.image_to_string(thresh)
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
            
    def clean_ingredient_list(self, raw_text):
        """Cleans and splits the raw string into a list of ingredients."""
        # Replace common OCR errors like newlines with commas
        raw_text = raw_text.replace('\n', ',')
        raw_list = re.split(r'[,\n]', raw_text)
        cleaned_list = [item.strip().title() for item in raw_list if len(item.strip()) > 2]
        return cleaned_list
        
    def match_ingredients(self, input_ingredients, threshold=70):
        """Matches input ingredients to the database using fuzzy string matching."""
        matched_results = []
        unmatched = []
        
        for ing in input_ingredients:
            if not self.ingredient_names:
                unmatched.append(ing)
                continue
                
            match = process.extractOne(ing, self.ingredient_names)
            
            if match and match[1] >= threshold:
                matched_name = match[0]
                score = match[1]
                record = self.db[self.db['Ingredient'] == matched_name].iloc[0].to_dict()
                record['Match Score'] = score
                record['Original Input'] = ing
                matched_results.append(record)
            else:
                unmatched.append(ing)
                
        return pd.DataFrame(matched_results), unmatched
        
    def analyze_for_skin_type(self, matched_df, skin_type):
        """Analyzes the matched ingredients for a specific skin type."""
        if matched_df.empty:
            return {'good': [], 'bad': [], 'comedogenic': [], 'irritants': []}
            
        analysis = {'good': [], 'bad': [], 'comedogenic': [], 'irritants': []}
        
        for _, row in matched_df.iterrows():
            if pd.notna(row.get('Good For')):
                good_for = [s.strip().lower() for s in str(row['Good For']).split(';')]
                if skin_type.lower() in good_for or 'all' in good_for:
                    analysis['good'].append(row)
                    
            if pd.notna(row.get('Bad For')):
                bad_for = [s.strip().lower() for s in str(row['Bad For']).split(';')]
                if skin_type.lower() in bad_for:
                    analysis['bad'].append(row)
                    
            if pd.notna(row.get('Comedogenic Rating')) and float(row['Comedogenic Rating']) > 2:
                analysis['comedogenic'].append(row)
                
            if pd.notna(row.get('Irritancy')) and float(row['Irritancy']) > 2:
                analysis['irritants'].append(row)
                
        return analysis
