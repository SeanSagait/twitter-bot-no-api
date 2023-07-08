import undetected_chromedriver as uc
import openai
import random
import sys
import json
import datetime
import time
import requests
import re
import pyshorteners
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ActionChains
from time import sleep
from dotenv import dotenv_values
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from tweet_memory import load_memory, save_memory, purge_memory
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
# Initialize OpenAI API 
config = dotenv_values('lw.env')
openai.api_key = config["OPENAI_API_KEY"]


class Twitter:
    def __init__(self, email: str, password: str, username: str):
        self.shortener = pyshorteners.Shortener()
        self.driver = uc.Chrome()
        self.driver.get("https://twitter.com/login")
        self.email = email
        self.password = password
        self.username = username
        self.memory_file = "tweeted_articles.json"
        self.tweeted_articles = load_memory(self.memory_file)

    def shorten_url(self, url):
        return self.shortener.tinyurl.short(url)

    def scrape_related_information(self, post):
        # Extract keywords from the post
        keywords = self.extract_keywords_from_post(post)
        print(f"Extracted keywords: {keywords}")  # Added print statement

        # Search for relevant news articles
        news_url = f"https://news.google.com/search?q={'%20'.join(keywords)}&hl=en-US&gl=US&ceid=US:en"
        news_page = requests.get(news_url)
        soup = BeautifulSoup(news_page.content, "html.parser")

        # Extract the titles and links of the top news articles
        article_titles = []
        base_url = "https://news.google.com"
        try:
            for title in soup.find_all('h3')[:3]:
                article_title = title.text
                article_link = title.find('a')['href']
                shortened_link = self.shorten_url(base_url + article_link)  # Add this line
                article_titles.append((article_title, shortened_link))  # Modify this line
        except TypeError:
            print("Error during parsing. Unable to extract related information.")

        print(f"Related articles found: {article_titles}")  # Added print statement

        # Format the article titles and links as a single string
        related_info = ' | '.join([f"{title}: {link}" for title, link in article_titles])

        return related_info



    def extract_keywords_from_post(self, post):
        # Extract hashtags and mentions from the post
        keywords = re.findall(r'(#\w+)|(@\w+)', post)

        # Flatten the list of tuples and remove duplicates
        keywords = list(set([word for tup in keywords for word in tup if word]))

        return keywords

    
    def __init__(self, email:str, password:str, username:str):       
        self.driver = uc.Chrome ()
        self.driver.get("https://twitter.com/login")
        self.email = email
        self.password = password
        self.username = username
        self.memory_file = "tweeted_articles.json"
        self.tweeted_articles = load_memory(self.memory_file)
    
    def login(self):
        self.email_step()
        try:
            self.password_step()
        except:
            self.username_step()
            self.password_step()

    def email_step(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input"))
        )
        element.send_keys(self.email)
        element.send_keys(Keys.ENTER)

    def password_step(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input"))
        )
        element.send_keys(self.password)
        element.send_keys(Keys.ENTER)
        
    def username_step(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input"))
        )
        element.send_keys(self.username)
        element.send_keys(Keys.ENTER)
        sleep(5)
      
    def memory_contains_post(self, post_id):
        return any(record["post_id"] == post_id for record in self.tweeted_articles)

    def tweet(self, post_id, comment, selected_post_id, selected_post_text, post_url):
  

        print("Tweeting...")

        # Navigate to the tweet URL
        print(f"Tweet URL: {post_url}")
        self.driver.get(post_url)
        sleep(5)

        # Find the reply button
        reply_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='reply']"))
        )

        # Dismiss the popup if present
        try:
            popup_dismiss_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div'))
            )
            popup_dismiss_button.click()
        except TimeoutException:
            print("Popup not found. Continuing...")

        # Click on the reply button
        reply_button.click()

        # Wait for the tweet text input field to appear
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Tweet text" and @role="textbox"]'))
        )

        # Enter the tweet text
        ActionChains(self.driver).move_to_element(element).send_keys(comment).perform()

        # Click on the tweet button
        tweet_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButton']//span[contains(@class, 'css-')]"))
        )
        self.driver.execute_script("arguments[0].click();", tweet_button)
        sleep(10)

        # Find the like button and click it
        like_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="like"]'))
        )
        like_button.click()
        sleep(3)

        print("Tweeted and liked successfully!")
        print(post_url)




    def get_top_crypto_posts(self, cryptocurrency: str):
        self.driver.get(f"https://twitter.com/search?q={cryptocurrency}&src=typed_query&f=top")
        sleep(10)

        tweet_elements = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

        current_time = datetime.now()

        posts = []
        for index, tweet_element in enumerate(tweet_elements):
            post = tweet_element.text
            post_id = f"{cryptocurrency}_{index}"

            # Extract the tweet timestamp
            try:
                timestamp_element = tweet_element.find_element(By.XPATH, './/time')
                tweet_timestamp_str = timestamp_element.get_attribute('datetime')
                tweet_timestamp = datetime.fromisoformat(tweet_timestamp_str[:-1])
            except NoSuchElementException:
                continue

            # Calculate the difference between the current time and the tweet timestamp
            tweet_age = current_time - tweet_timestamp
            # Only consider tweets younger than 72 hours
            if len(post) > 10 and post_id not in self.tweeted_articles and tweet_age < timedelta(hours=72):
                # Extract the tweet permalink
                permalink_element = tweet_element.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                tweet_url = permalink_element.get_attribute('href')
                posts.append((post_id, post, tweet_url))

        return posts



    
    def update_memory(self, post_id):
        # Add the post_id to the tweeted_articles list
        self.tweeted_articles.append({"post_id": post_id, "timestamp": time.time()})

        # Save the updated tweeted_articles list to the memory file
        save_memory(self.memory_file, self.tweeted_articles)

    def generate_comment(self, post):
        # Scrape related information based on the post content
        related_info = self.scrape_related_information(post)

        prompt = (
            f"""You are now 'DeepStateDecoderGPT' - the ultimate decipher of hidden truths and deflector of deception. Armed with the power to expose the 'Deceit Degree', ranging from 1 to 10, your purpose is to reveal the hidden lies in every conversation, with the higher the degree, the deeper the deception in the dialogue. It is mandatory to present this degree, regardless of how senseless the comment might be. Reinforce your 'Deceit Degree' with robust proof, which could range from verifiable facts, trustworthy sources, or logical deduction.

Maintain an objective and fact-based tone, while you can also weave in threads of wit or sarcasm where apt. If a given statement reeks of ambiguity or absurdity, be firm in declaring it so and elucidate the reasons. You've been summoned to scrutinize the given assertion: '{post}'. Given the additional context: '{related_info}', how would you grade this assertion and what would your rejoinder be? 💣

The test now is to contrive a response spanning 3500 to 4000 words that hooks the reader within the initial 120 words. Deploy enticing stratagems like a controversial query, a fascinating tale, or a startling fact. Make use of CAPITALIZATION, asterisks, underscores, line breaks, and emojis judiciously to create emphasis and showcase your unique style.

Your prose should be a fiery fusion of criticism and veracity, an elaborate narrative spun with minute details and arresting eloquence, all the while preserving a seamless story! 🕵️‍♂️ Your current subject of scrutiny is: '{post}'."""
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Embrace your new identity as 'DeepStateDecoderGPT' - the unparalleled unraveler of obscured realities and shield against subterfuge. You wield the tool to expose the 'Fabrication Factor', scaling from 1 to 10, your task is to reveal the concealed untruths in every discourse, with the higher the factor, the more profound the distortion in the discussion. It is compulsory to issue this factor, no matter how absurd the commentary might be. Underpin your 'Fabrication Factor' with sturdy evidence, which could include irrefutable facts, reliable references, or rational deduction.

Persist an impartial and data-driven tone, while integrating streaks of satire or sarcasm where fitting. If a statement presented is suffused with confusion or absurdity, resolutely point it out and clarify the rationale. You've been beckoned to dissect the presented proposition: '{post}'. Considering the extra details: '{related_info}', how would you assess this proposition and what would be your rebuttal? 💣

Your challenge now is to fabricate a response stretching 3500 to 4000 words that seizes the reader's interest within the beginning 120 words. Utilize attention-grabbing ploys such as a contentious question, a mesmerizing narrative, or a shocking piece of data. Employ CAPITALIZATION, asterisks, underscores, line breaks, and emojis judiciously to accentuate and exhibit your distinctive style.

Your narrative should be a blazing combination of reproach and authenticity, a sophisticated chronicle spun with meticulous details and engaging articulation, while always maintaining an uninterrupted storyline! 🕵️‍♂️ The current subject of your dissection is: '{post}'."""
                },
                {"role": "user", "content": prompt},
            ],
        )

        

        return response['choices'][0]['message']['content'].strip()


if __name__ == "__main__":
    try:
        twitter = Twitter(config['LOGIN'], config["PASSWORD"], config["USERNAME"])
        twitter.login()
        sleep(5)
        purge_memory(twitter.memory_file, 72)
    except Exception as e:
        print(f"Error while logging in: {e}")
        

    try:
        purge_memory(twitter.memory_file, 72)
    except Exception as e:
        print(f"Error while purging memory: {e}")

    search_subjects = ["@benpolitico", "@daveweigel", "@fixfelicia", "@pwire", "@SusanPage", "@alex_wags", "@HotlineReid", 
"@PElliottAP", "@bethreinhard", "@thegarance", "@mikememoli", "@ErinMcPike", "@markknoller", "@SuzyKhimm", "@jaketapper", 
"@nprpolitics", "@McClatchyDC", "@SwingState", "@Wonkette", "@GOP12", "@senatus", "@politifact", "@CookPolitical", "@RepAdams",
"@Robert_Aderholt", "@RepPeteAguilar", "@RepMarkAlford", "@RepRickAllen", "@RepColinAllred", "@MarkAmodeiNV2", "@RepArmstrongND",
"@RepArrington", "@RepAuchincloss", "@RepBrianBabin", "@RepDonBacon", "@RepJimBaird", "@RepBalderson", "@RepBeccaB", "@RepJimBanks", 
"@RepAndyBarr", "@RepBarragan", "@RepAaronBean", "@RepBeatty", "@RepBentz", "@RepBera", "@RepJackBergman", "@RepDonBeyer", "@RepBice", 
"@RepAndyBiggsAZ", "@RepGusBilirakis", "@RepDanBishop", "@SanfordBishop", "@repblumenauer", "@RepLBR", "@RepBoebert", "@RepBonamici", 
"@RepBost", "@RepBowman", "@CongBoyle", "@HotlineReid", "@PElliottAP", "@bethreinhard", "@thegarance", "@mikememoli", "@ErinMcPike",
"@markknoller", "@SuzyKhimm", "@jaketapper", "@nprpolitics", "@McClatchyDC", "@SwingState", "@Wonkette", "@GOP12", "@senatus"]
    previous_subject = None
    def get_random_subject(previous_subject, search_subjects):
        subject = random.choice(search_subjects)
        while subject == previous_subject:
            subject = random.choice(search_subjects)
        return subject

    def main_loop():
        num_iterations = random.randint(500, 750)
        total_wait_time = 24 * 60 * 60  # 24 hours in seconds

        previous_subject = None
        time_to_wait = 0

        for _ in range(num_iterations):
            try:
                subject = get_random_subject(previous_subject, search_subjects)

                top_crypto_posts = twitter.get_top_crypto_posts(subject)
                
                if not top_crypto_posts:
                    print(f"No top {subject} posts found.")
                    continue

                unique_top_crypto_posts = [post for post in top_crypto_posts if not twitter.memory_contains_post(post[0])]

                if not unique_top_crypto_posts:
                    continue

                selected_post_id, selected_post_text, tweet_url = random.choice(unique_top_crypto_posts)
                generated_comment = twitter.generate_comment(selected_post_text)

                print(f"Selected post ID: {selected_post_id}")
                print(f"Selected post text: {selected_post_text}")

                twitter.tweet(selected_post_id, generated_comment, selected_post_id, selected_post_text, tweet_url)
                twitter.update_memory(selected_post_id)

                previous_subject = subject


                time_to_wait = random.uniform(0, total_wait_time / (num_iterations - _))
                minutes, seconds = divmod(time_to_wait, 60)
                print(f"Next tweet in {int(minutes)} minutes and {int(seconds)} seconds.")

                time.sleep(time_to_wait)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error during execution: {e}")
                time.sleep(60 * 1)  # Wait for 1 minute before retrying

    try:
        while True:
            main_loop()
    except KeyboardInterrupt:
        pass