from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class InstagramBot:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):

        print("1. Deschid pagina de login...")
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)

        print("2. Aștept încărcarea paginii.")
        time.sleep(2)

        try:
            print("3.Încerc să găsesc câmpul username după name.")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            print("   ✓ Am găsit câmpurile după NAME")
        except:
            # Încercare 2: După input-uri
            try:
                print("Nu am găsit după NAME")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if len(inputs) >= 2:
                    username_field = inputs[0]
                    password_field = inputs[1]
                    print(f" Am găsit {len(inputs)} câmpuri input")
            except:

                try:
                    print("  Încerc după placeholder..")
                    username_field = self.driver.find_element(By.XPATH,
                                                              "//input[@placeholder='Telefon, nume utilizator sau e-mail']")
                    password_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Parolă']")
                    print(" Am găsit după placeholder")
                except:

                    try:
                        print("   ✗ Încerc după aria-label...")
                        username_field = self.driver.find_element(By.XPATH,
                                                                  "//input[@aria-label='Număr de telefon, nume de utilizator sau e-mail']")
                        password_field = self.driver.find_element(By.XPATH, "//input[@aria-label='Parola']")
                        print("   ✓ Am găsit după aria-label")
                    except Exception as e:
                        print(f"   ✗ EROARE: {e}")
                        # Salvăm pagina pentru debugging
                        with open("pagina_eroare.html", "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                        print("   Pagina salvată în 'pagina_eroare.html'")
                        raise Exception("Nu s-au găsit câmpurile de login")


        print("4.Completez câmpurile.")
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(1)

        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)


        print("5.Caut butonul de login.")
        try:

            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            print("   ✓ Am găsit butonul după text")
        except:
            try:
                # Încercare 2: După type
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                print("   ✓ Am găsit butonul după type")
            except:
                try:
                    # Încercare 3: Orice buton din form
                    login_button = self.driver.find_element(By.XPATH, "//form//button")
                    print("Am găsit butonul în form")
                except Exception as e:
                    print(f" Eroare la găsire buton: {e}")
                    login_button = None

        if login_button:
            print("6.Apăs butonul de login.")
            login_button.click()
        else:
            print("6. Apăs ENTER pentru login...")
            password_field.send_keys(Keys.ENTER)

        print("7. Aștept să se încarce pagina principală...")
        time.sleep(7)

        try:

            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x1n2onr6')]")))
            print("Login REUȘIT! Am ajuns pe pagina principală.")
            return True
        except:

            try:
                error_msg = self.driver.find_element(By.XPATH, "//p[contains(text(), 'incorrect')]")
                print(f"✗ Login EȘUAT: {error_msg.text}")
            except:
                print("Login EȘUAT - nu s-a putut verifica")
            return False

    def find_followers(self, target_account):

        print(f"\nNavighez la {target_account}...")
        self.driver.get(f"https://www.instagram.com/{target_account}/")
        time.sleep(3)

        try:

            followers_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]"))
            )
            followers_link.click()
            print("Am deschis lista de followers")
            time.sleep(2)


            modal = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )


            print("Fac scroll în listă...")
            for i in range(3):
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                time.sleep(2)
                print(f"Scroll {i + 1} completat")

            return modal
        except Exception as e:
            print(f"Eroare la găsirea follower-ilor: {e}")
            return None

    def follow_users(self, max_follow=5):
        """Dă follow la primii utilizatori din listă"""
        print("\nÎncep să dau follow...")


        follow_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')]")


        valid_buttons = []
        for btn in follow_buttons:
            try:
                if btn.is_displayed() and btn.is_enabled():
                    valid_buttons.append(btn)
            except:
                pass

        print(f"Am găsit {len(valid_buttons)} butoane valide de Follow")

        followed = 0
        for i, button in enumerate(valid_buttons):
            if followed >= max_follow:
                break

            try:

                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)

                button.click()
                followed += 1
                print(f"✓ Follow {followed}: Am dat follow unui utilizator")
                time.sleep(2)  # Pauză între follow-uri

            except Exception as e:
                print(f"✗ Eroare la follow: {e}")

        print(f"Am dat follow la {followed} utilizatori")
        return followed

    def close(self):
        """Închide browserul"""
        input("\nApasă Enter pentru a închide browserul...")
        self.driver.quit()



if __name__ == "__main__":

    USERNAME = "verhovenbadr"
    PASSWORD = "aici contul acesta e facut de mine,trebuie inlocuit cu alt cont si sa fie data parola"

    TARGET_ACCOUNT = "chefsteps"

    bot = InstagramBot()

    try:
        if bot.login(USERNAME, PASSWORD):
            time.sleep(3)
            bot.find_followers(TARGET_ACCOUNT)
            time.sleep(2)
            bot.follow_users(max_follow=5)
        else:
            print("Nu s-a putut efectua login-ul. Verifică credentialele.")

    except Exception as e:
        print(f"Eroare generală: {e}")
        bot.driver.save_screenshot("eroare_generala.png")

    finally:
        bot.close()