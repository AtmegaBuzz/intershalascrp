import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep, time
import gspread
from IConfig import spreadsheet_url,job_list,total_results_want


while(True):
    today_date = datetime.datetime.today().date()
    with open("time.txt","r",encoding="utf8") as f:
        time_d = (f.read()).split("-")
        past_date = datetime.date(int(time_d[0]), int(time_d[1]), int(time_d[2]))
        day_difference = (today_date-past_date).days    
        
        if(not(day_difference>=7)):
            print("goin to sleep")
            continue
        
        

    gc = gspread.service_account(filename='cred.json')
    sh = gc.open_by_url(spreadsheet_url)
    worksheet = sh.sheet1


    url_data = worksheet.batch_get(("F2:F",))[0]

    url_store = []

    for url in url_data:
        url_store.append(url[0])

    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')
    options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            )
    options.add_argument('--no-sandbox')
    options.add_argument("window-size=1920,1080")
    options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--verbose")
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    for job_title in job_list:

        driver.get(f"https://internshala.com/internships/{job_title}-internship")
        driver.maximize_window()


        sleep(3)
        try:
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[20]/div/div[1]/i"))).click()
            sleep(2)
        except:
            pass
        sleep(3)
        number_of_pages = int(WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"total_pages"))).get_attribute("innerText"))
        print(number_of_pages)                                                             

        counter = 0
        flag = True


        for page in range(number_of_pages):
            
            try:
                number_of_posts = len(driver.find_elements(By.XPATH,"/html/body/div[1]/div[22]/div[2]/div/div[3]/div[2]/div[2]/div/div"))
                div_no = 22
                if(number_of_posts==0):
                    raise "switch xpath"
                                                                
            except Exception as e:
                print(e)
                div_no = 21
                number_of_posts = len(driver.find_elements(By.XPATH,"/html/body/div[1]/div[21]/div[2]/div/div[3]/div[2]/div[2]/div/div"))

                
            print("l",number_of_posts)                                                    
            for post in range(1,number_of_posts+1):
                sleep(1)
                job_url = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[{div_no}]/div[2]/div/div[3]/div[2]/div[2]/div/div[{post}]/div[2]/a"))).get_attribute("href")
                if(job_url in url_store):
                    print("skipping already present")
                    continue
            
                job_title = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[{div_no}]/div[2]/div/div[3]/div[2]/div[2]/div/div[{post}]/div[1]/div[1]/div[1]/div[1]/a"))).get_attribute("innerText")
                company_name = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[{div_no}]/div[2]/div/div[3]/div[2]/div[2]/div/div[{post}]/div[1]/div[1]/div[1]/div[2]/a"))).get_attribute("innerText")
                stipend = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[{div_no}]/div[2]/div/div[3]/div[2]/div[2]/div/div[{post}]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/span"))).get_attribute("innerText")
                duration = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[{div_no}]/div[2]/div/div[3]/div[2]/div[2]/div/div[{post}]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]"))).get_attribute("innerText")
                location = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[{div_no}]/div[2]/div/div[3]/div[2]/div[2]/div/div[{post}]/div[1]/div[2]/div[1]/span/a"))).get_attribute("innerText")

                worksheet.append_row([job_title,company_name,stipend,duration,location,job_url])
                print("Fetched",counter)
                if(counter>=total_results_want):
                    flag = False
                    break
                counter+=1
            if(flag==False):
                print("results fetched")
                break
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"next"))).click()

            sleep(3)
        sleep(5)
        print("all jobs scrapperd from title")

    driver.close()
    
    with open("time.txt","w",encoding="utf8") as f:
        f.write(f"{today_date}")
