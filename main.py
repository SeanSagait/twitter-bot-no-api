from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from time import sleep

from dotenv import dotenv_values


class Twitter:
    def __init__(self, email:str, password:str, username:str) -> None:       
        self.driver =  webdriver.Chrome()
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
        
    def tweet(self, text:str):
        sleep(3)
        self.driver.find_element(By.CLASS_NAME, 'DraftEditor-root').click()
        element=self.driver.find_element(By.CLASS_NAME, 'public-DraftEditorPlaceholder-root')
        ActionChains(self.driver).move_to_element(element).send_keys(text).perform()
        sleep(3)
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div[3]").click()
        
if __name__ == "__main__":
    config = dotenv_values('.env')
    twitter = Twitter(config['LOGIN'], config["PASSWORD"], config["USERNAME"])
    twitter.login()
    twitter.tweet("hello world")
