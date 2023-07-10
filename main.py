import undetected_chromedriver.v2 as uc
import openai
import random
import sys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from time import sleep
from dotenv import dotenv_values
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


# Initialize OpenAI API 
config = dotenv_values('.env')

openai.api_key = config["OPENAI_API_KEY"]

class Twitter:
    def __init__(self, email:str, password:str, username:str):       
        self.driver = uc.Chrome ()
        self.driver.get("https://twitter.com/login")
        self.email = email
        self.password = password
        self.username = username
        
    def login(self):
        self.email_step()
        try:
            self.password_step()
        except:
            self.username_step()
            self.password_step()
            
    def email_step(self):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input"))
        )
        element.send_keys(self.email)
        element.send_keys(Keys.ENTER)

    def password_step(self):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input"))
        )
        element.send_keys(self.password)
        element.send_keys(Keys.ENTER)
        
    def username_step(self):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input"))
        )
        element.send_keys(self.username)
        element.send_keys(Keys.ENTER)
        sleep(5)

    def tweet(self, text: str):
        print("Tweeting...")
        reply_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='reply']/parent::div"))
        )
        reply_button.click()

        print("Clicked on reply button.")
        sleep(4)
        element = self.driver.find_element(By.XPATH, '//div[@aria-label="Tweet text"]')
        print("Located the tweet text input field.")
        sleep(3)
        ActionChains(self.driver).move_to_element(element).send_keys(text).perform()
        print("Entered tweet text.")
        sleep(10)
        tweet_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButton']//span[contains(@class, 'css-')]"))
        )
        self.driver.execute_script("arguments[0].click();", tweet_button)
        sleep(30)
        print("Clicked on tweet button.")
        print("Tweeted successfully!")


    def get_top_crypto_posts(self, cryptocurrency:str):
    # Navigate to Twitter's search results page for the given cryptocurrency
        self.driver.get(f"https://twitter.com/search?q={cryptocurrency}&src=typed_query&f=top")
        sleep(10)

        # Extract the tweet elements from the page
        tweet_elements = self.driver.find_elements(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/section/div/div/div[2]')

        # Extract the text of each tweet and add it to the list of posts
        posts = []
        for tweet_element in tweet_elements:
            post = tweet_element.text
            posts.append(post)

        return posts

    def generate_comment(self, post):
        prompt = f"Generate a relevant and engaging comment about this top crypto post: '{post}'"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        
        return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    twitter = Twitter(config['LOGIN'], config["PASSWORD"], config["USERNAME"])
    twitter.login()
    sleep(5)
        
        # Scrape trending crypto posts
    top_crypto_posts = twitter.get_top_crypto_posts('crypto news')
    print(f"Top crypto posts: {top_crypto_posts}")

    if not top_crypto_posts:
        print("No top crypto posts found. Exiting.")
        input("Press Enter to close the browser window...")
        twitter.driver.quit()
        sys.exit(1)

    sleep(5)
    
    # Choose a random post from the list of trending posts
    selected_post = random.choice(top_crypto_posts)
    print(f"Selected post: {selected_post}")

    # Generate a comment using GPT-3.5 Turbo
    generated_comment = twitter.generate_comment(selected_post)
    print(f"Generated comment: {generated_comment}")

    # Tweet the generated comment
    twitter.tweet(generated_comment)

