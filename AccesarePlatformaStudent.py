from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



USER_ASE = "nume_utilizator"
PAROLA_ASE = "parola"


driver = webdriver.Chrome()

try:

    driver.get("https://webstudent.ase.ro")
    time.sleep(2)



    input_user = driver.find_element(By.ID, "txtUtilizator")
    input_pass = driver.find_element(By.ID, "txtParola")

    input_user.send_keys("pricopealin24")
    input_pass.send_keys("alin1321alin")
    input_pass.send_keys(Keys.ENTER)


    time.sleep(5)


    link_note = driver.find_element(By.LINK_TEXT, "Note")
    link_note.click()
    time.sleep(2)


    butoane = driver.find_elements(By.XPATH, "//input[@value='Afiseaza note']")
    if butoane:
        butoane[0].click()
        print("Am apasat pe butonul de afisare note...")
        time.sleep(3)

    randuri = driver.find_elements(By.XPATH, "//table//tr[td]")

    print("-" * 30)
    print(f"{'MATERIE':<30} | {'NOTA':<5} | {'CREDITE'}")
    print("-" * 30)

    for r in randuri:
        celule = r.find_elements(By.TAG_NAME, "td")

        if len(celule) >= 6:
            materie = celule[1].text
            nota = celule[4].text
            credite = celule[5].text
            print(f"{materie[:30]:<30} | {nota:<5} | {credite}")

finally:

    time.sleep(10)
    driver.quit()