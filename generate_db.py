import pandas as pd
import random
import os

def generate_database(num_ingredients=300):
    functions = ['Solvent', 'Humectant', 'Emollient', 'Antioxidant', 'Preservative', 'Surfactant', 'Thickener', 'Exfoliant', 'Soothing', 'Astringent']
    good_for_options = ['All', 'Dry', 'Oily', 'Acne', 'Sensitive', 'Aging']
    bad_for_options = ['None', 'Dry', 'Oily', 'Sensitive', 'Acne']
    
    # Base ingredients to ensure we have standard ones
    base_ingredients = [
        ("Water", "Solvent", 0, 0, "All", "None", "The base of life and most potions."),
        ("Glycerin", "Humectant", 0, 0, "Dry", "None", "Draws moisture like a sponge."),
        ("Niacinamide", "Antioxidant", 0, 0, "Acne", "None", "Brightens the skin and fortifies the barrier."),
        ("Salicylic Acid", "Exfoliant", 0, 1, "Oily;Acne", "Dry;Sensitive", "A potent BHA that clears pores."),
        ("Fragrance", "Perfume", 0, 4, "None", "Sensitive", "Provides scent, often irritating."),
        ("Dimethicone", "Emollient", 1, 0, "Dry", "None", "Forms a protective silicone barrier."),
        ("Retinol", "Antioxidant", 0, 3, "Aging", "Sensitive", "Powerful anti-aging elixir."),
        ("Vitamin C", "Antioxidant", 0, 1, "All", "Sensitive", "Brightens and protects."),
        ("Hyaluronic Acid", "Humectant", 0, 0, "Dry", "None", "Holds immense amounts of water."),
        ("Alcohol Denat", "Astringent", 0, 5, "Oily", "Dry;Sensitive", "Drying and potentially harsh.")
    ]
    
    prefixes = ['Sodium', 'Potassium', 'Cetearyl', 'Methyl', 'Propyl', 'Butyl', 'Ethyl', 'PEG-', 'PPG-', 'Hydrolyzed', 'Extract of', 'Essence of', 'Tears of', 'Oil of', 'Ash of', 'Dust of', 'Sap of', 'Resin of', 'Nectar of', 'Elixir of']
    roots = ['Hyaluronate', 'Paraben', 'Alcohol', 'Glycol', 'Acid', 'Sulfate', 'Chloride', 'Benzoate', 'Peptide', 'Ceramide', 'Rose', 'Lavender', 'Dragonbone', 'Weirwood', 'Iron', 'Gold', 'Valyrian Steel', 'Obsidian', 'Moonwood', 'Sunstone']
    
    data = []
    
    # Add base ingredients
    for ing in base_ingredients:
        data.append(list(ing))
        
    # Generate synthetic ingredients to reach the target count
    existing_names = set([ing[0] for ing in base_ingredients])
    
    while len(data) < num_ingredients:
        name = f"{random.choice(prefixes)} {random.choice(roots)}"
        if name in existing_names:
            continue
            
        existing_names.add(name)
        
        func = random.choice(functions)
        comedogenic = random.randint(0, 5)
        irritancy = random.randint(0, 5)
        
        # Adjust ratings based on function
        if func in ['Emollient', 'Thickener']:
            comedogenic = random.randint(1, 5)
        if func in ['Preservative', 'Astringent', 'Exfoliant']:
            irritancy = random.randint(1, 5)
            
        good_for = random.choice(good_for_options)
        if random.random() > 0.7:
            good_for += f";{random.choice(good_for_options)}"
            
        bad_for = random.choice(bad_for_options)
        if random.random() > 0.8 and bad_for != 'None':
            bad_for += f";{random.choice(bad_for_options)}"
            
        desc = f"A synthetic or natural {func.lower()} used in skincare formulations."
        
        data.append([name, func, comedogenic, irritancy, good_for, bad_for, desc])
        
    df = pd.DataFrame(data, columns=['Ingredient', 'Function', 'Comedogenic Rating', 'Irritancy', 'Good For', 'Bad For', 'Description'])
    
    # Ensure directory exists
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/ingredients_db.csv', index=False)
    print(f"Generated data/ingredients_db.csv with {len(df)} ingredients.")

if __name__ == "__main__":
    generate_database(300)
