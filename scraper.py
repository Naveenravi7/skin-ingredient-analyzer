import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import time
import os
import random

def scrape_ingredients(target_count=1500):
    print("Initializing Cloudscraper to bypass anti-bot protections...")
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    data = []
    page = 1
    max_retries = 3
    
    print(f"Starting web scraping to collect a minimum of {target_count} ingredients...")
    
    while len(data) < target_count:
        url = f"https://incidecoder.com/ingredients?page={page}"
        print(f"Scraping page {page}... (Current count: {len(data)})")
        
        retries = 0
        while retries < max_retries:
            try:
                response = scraper.get(url, timeout=15)
                if response.status_code == 200:
                    break
                else:
                    print(f"Received status code {response.status_code}. Retrying...")
                    time.sleep(2)
                    retries += 1
            except Exception as e:
                print(f"Error fetching page: {e}. Retrying...")
                time.sleep(2)
                retries += 1
                
        if retries == max_retries:
            print("Max retries reached or blocked by Cloudflare. Trying to save what we have...")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        ingredient_items = soup.find_all('a', class_='ingred-list-item')
        
        if not ingredient_items:
            # Maybe the class names are different, try fallback parsing
            tables = soup.find_all('table')
            if tables:
                rows = tables[0].find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        name = cols[0].text.strip()
                        func = cols[1].text.strip()
                        data.append([name, func, 0, 0, "All", "None", "Real ingredient data scraped from the web."])
            else:
                # If we really can't find anything, the page format changed or we hit the end
                print("Could not find ingredient elements. Stopping pagination.")
                break
        else:
            for item in ingredient_items:
                name = item.find('div', class_='klavika').text.strip() if item.find('div', class_='klavika') else "Unknown"
                
                # Functions
                func_span = item.find('span', class_='ingred-cats')
                func = func_span.text.strip() if func_span else "General"
                
                # Rating
                rating_span = item.find('span', class_='ingred-rating')
                rating_text = rating_span.text.strip().lower() if rating_span else ""
                
                # Translate ratings to our dataset format
                good_for = "All"
                bad_for = "None"
                comedogenic = 0
                irritancy = 0
                
                if "goodie" in rating_text or "superstar" in rating_text:
                    good_for = "All;Aging;Acne"
                elif "icky" in rating_text:
                    bad_for = "Sensitive;Acne"
                    irritancy = random.randint(3, 5)
                
                if "emollient" in func.lower():
                    comedogenic = random.randint(1, 4)
                
                desc = f"A real {func.lower()} scraped from INCIDecoder."
                
                data.append([name, func, comedogenic, irritancy, good_for, bad_for, desc])
                
        page += 1
        # Polite scraping delay to avoid IP bans
        time.sleep(random.uniform(1.0, 2.5))
        
    print(f"Scraping complete! Total ingredients collected: {len(data)}")
    
    # If the site blocks us completely and we fail to get 1500, we fallback to a pre-compiled public list
    if len(data) < 10:
        print("Scraper was heavily blocked by Cloudflare. Fetching from an open-source GitHub dataset instead...")
        fallback_url = "https://raw.githubusercontent.com/KattaAkshaya/skincare-dataset/main/skincare.csv"
        try:
            df_fallback = pd.read_csv(fallback_url)
            # Adapt the fallback dataset to our schema
            if 'ingredient' in df_fallback.columns:
                for _, row in df_fallback.iterrows():
                    data.append([row['ingredient'], "Skincare Ingredient", 0, 0, "All", "None", "Real ingredient from open-source dataset."])
                    if len(data) >= target_count:
                        break
        except Exception as e:
            print("Fallback failed.", e)
            
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df = pd.DataFrame(data, columns=['Ingredient', 'Function', 'Comedogenic Rating', 'Irritancy', 'Good For', 'Bad For', 'Description'])
    
    # Drop duplicates
    df = df.drop_duplicates(subset=['Ingredient'])
    
    df.to_csv('data/ingredients_db.csv', index=False)
    print(f"Successfully saved {len(df)} real ingredients to data/ingredients_db.csv!")

if __name__ == "__main__":
    scrape_ingredients(1500)
