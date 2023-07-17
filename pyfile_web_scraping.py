
import time
import io
import pandas as pd
import numpy as np
import csv
import sys
import os  
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions


def scrapfyt(url):


  option = webdriver.ChromeOptions()
  option.binary_location = os.environ.get("GOOGLE_CHROME_BIN") 
  option.add_argument('--headless')
  option.add_argument('-no-sandbox')
  option.add_argument("--mute-audio")
  option.add_argument("--disable-extensions")#adds
  option.add_argument('-disable-dev-shm-usage')#shared memory

  driver = webdriver.Chrome(service=Service("C:/chrome extension/chromedriver.exe"), options=option) 

 

  driver.set_window_size(960, 800)    
  time.sleep(1)
  driver.get(url)
  time.sleep(2)


  pause = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ytp-play-button')))

  pause.click()
  time.sleep(0.2)
  pause.click()
  time.sleep(4)

 
  driver.execute_script("window.scrollBy(0,500)","")
    
  last_height = driver.execute_script("return document.documentElement.scrollHeight")

  while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    time.sleep(4)
  
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
      break
    last_height = new_height
    
  driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
  video_title = driver.find_element(By.NAME, 'title').get_attribute('content')

  video_owner1 = driver.find_elements(By.XPATH, '//*[@id="text"]/a')
  video_owner = []
  for owner in video_owner1:
    video_owner.append(owner.text)
  video_owner = video_owner[0]

  video_comment_with_replies = driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]').text + ' Comments'

  users = driver.find_elements(By.XPATH, '//*[@id="author-text"]/span')
  comments = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

  with io.open('comments.csv', 'w', newline='', encoding="utf-16") as file:
      writer = csv.writer(file, delimiter =",", quoting=csv.QUOTE_ALL)
      writer.writerow(["Username", "Comment"])
      for username, comment in zip(users, comments):
          writer.writerow([username.text, comment.text])
    
  commentsfile = pd.read_csv("comments.csv", encoding ="utf-16") 

  all_comments = commentsfile.replace(np.nan, '-', regex = True)
  all_comments = all_comments.to_csv("Full Comments.csv", index = False)
  video_comment_without_replies = str(len(commentsfile.axes[0])) + ' Comments'


  driver.close()

  return all_comments, video_title, video_owner, video_comment_with_replies, video_comment_without_replies
