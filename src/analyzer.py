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
        self._ensure_database_exists()
        
        try:
            self.db = pd.read_csv(self.db_path)
            self.ingredient_names = self.db['Ingredient'].tolist()
        except Exception as e:
            print(f"Error loading database: {e}")
            self.db = pd.DataFrame()
            self.ingredient_names = []

    def _ensure_database_exists(self):
        """Generates a 300-ingredient GoT-themed database if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Check if it exists and has enough rows
        if os.path.exists(self.db_path):
            try:
                df = pd.read_csv(self.db_path)
                if len(df) >= 300:
                    return
            except:
                pass
                
        print("Generating 300-ingredient database...")
        functions = ['Solvent', 'Humectant', 'Emollient', 'Antioxidant', 'Preservative', 'Surfactant', 'Thickener', 'Exfoliant', 'Soothing', 'Astringent']
        good_for_options = ['All', 'Dry', 'Oily', 'Acne', 'Sensitive', 'Aging']
        bad_for_options = ['None', 'Dry', 'Oily', 'Sensitive', 'Acne']
        
        base_ingredients = [
            ("Water (Tears of Lys)", "Solvent", 0, 0, "All", "None", "The base of most potions. Pure and untainted."),
            ("Glycerin (Essence of Highgarden)", "Humectant", 0, 0, "Dry", "None", "Draws moisture like a Tyrell sponge."),
            ("Niacinamide", "Antioxidant", 0, 0, "Acne", "None", "Fortifies the skin barrier like the Wall."),
            ("Salicylic Acid (Wildfire Extract)", "Exfoliant", 0, 1, "Oily;Acne", "Dry;Sensitive", "A potent BHA that burns away impurities in pores."),
            ("Fragrance (Perfume of Qarth)", "Perfume", 0, 4, "None", "Sensitive", "Provides scent, but treacherous to sensitive skin."),
            ("Dimethicone (Valyrian Resin)", "Emollient", 1, 0, "Dry", "None", "Forms a protective shield impervious to the elements."),
            ("Retinol (Blood of the Dragon)", "Antioxidant", 0, 3, "Aging", "Sensitive", "Powerful anti-aging elixir, handle with care."),
            ("Vitamin C (Sun of Dorne)", "Antioxidant", 0, 1, "All", "Sensitive", "Brightens and protects like the Dornish sun."),
            ("Hyaluronic Acid (Riverrun Tears)", "Humectant", 0, 0, "Dry", "None", "Holds immense amounts of water to flood the skin with hydration."),
            ("Alcohol Denat (Milk of the Poppy)", "Astringent", 0, 5, "Oily", "Dry;Sensitive", "Numbing and drying, use only when necessary.")
        ]
        
        prefixes = ['Sodium', 'Potassium', 'Cetearyl', 'Methyl', 'Propyl', 'Butyl', 'Ethyl', 'PEG-', 'PPG-', 'Hydrolyzed', 'Extract of', 'Essence of', 'Tears of', 'Oil of', 'Ash of', 'Dust of', 'Sap of', 'Resin of', 'Nectar of', 'Elixir of']
        roots = ['Hyaluronate', 'Paraben', 'Alcohol', 'Glycol', 'Acid', 'Sulfate', 'Chloride', 'Benzoate', 'Peptide', 'Ceramide', 'Rose', 'Lavender', 'Dragonbone', 'Weirwood', 'Iron', 'Gold', 'Valyrian Steel', 'Obsidian', 'Moonwood', 'Sunstone']
        
        data = [list(ing) for ing in base_ingredients]
        existing_names = set([ing[0] for ing in base_ingredients])
        
        while len(data) < 300:
            name = f"{random.choice(prefixes)} {random.choice(roots)}"
            if name in existing_names:
                continue
            existing_names.add(name)
            
            func = random.choice(functions)
            comedogenic = random.randint(0, 5)
            irritancy = random.randint(0, 5)
            
            if func in ['Emollient', 'Thickener']: comedogenic = random.randint(1, 5)
            if func in ['Preservative', 'Astringent', 'Exfoliant']: irritancy = random.randint(1, 5)
                
            good_for = random.choice(good_for_options)
            if random.random() > 0.7: good_for += f";{random.choice(good_for_options)}"
            bad_for = random.choice(bad_for_options)
            if random.random() > 0.8 and bad_for != 'None': bad_for += f";{random.choice(bad_for_options)}"
                
            desc = f"A Maester's {func.lower()} crafted in the Citadel for skincare incantations."
            data.append([name, func, comedogenic, irritancy, good_for, bad_for, desc])
            
        df = pd.DataFrame(data, columns=['Ingredient', 'Function', 'Comedogenic Rating', 'Irritancy', 'Good For', 'Bad For', 'Description'])
        df.to_csv(self.db_path, index=False)

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
