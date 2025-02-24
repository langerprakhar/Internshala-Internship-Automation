import time
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set Gemini API Key
GEMINI_API_KEY = "your-free-gemini-api-key-here"
genai.configure(api_key=GEMINI_API_KEY)

# User Credentials
USERNAME = "Your Internshala-registered-email-id"
PASSWORD = "Your Internshala-Password"

# Function to check relevance using Gemini API
def check_relevance(title):
    prompt = f"""
    You are an AI assistant filtering internship listings. 
    The applicant is ONLY interested in roles **directly** related to (***Whatever you prefer***).

    If the title "{title}" is **STRICTLY or moderately** related to these fields, respond with only "YES".  
    If it is **even slightly unrelated**, respond with only "NO".  
    Do not provide explanations. Only answer "YES" or "NO".
    """

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        if response and hasattr(response, 'text'):
            answer = response.text.strip().upper()
            print(f"🔍 Checking relevance for '{title}' → Gemini says: {answer}")
            return answer == "YES"
        else:
            return False

    except Exception as e:
        print(f"⚠ Error checking relevance: {e}")
        return False


# Function to generate responses using Gemini API
def generate_response(question):
    prompt = f"""
    You are an applicant answering internship application questions.
    The applicant's resume details are as follows:

    ********The Info from your resume over here********

    Provide a **concise, professional answer** to the following internship application question:
    
    **Question:** {question}
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, 'text') else "I am excited about this opportunity and look forward to contributing my skills."
    except Exception as e:
        print(f"⚠ Error generating response: {e}")
        return "I am excited about this opportunity and look forward to contributing my skills."

# 🔹 Initialize WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

# 🔹 Open Internshala Login Page
driver.get("https://internshala.com/student/dashboard")
print("🔍 Opened Internshala login page.")

# 🔹 Login Process
try:
    email_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
    email_field.send_keys(USERNAME)

    password_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    password_field.send_keys(PASSWORD)

    print("⚠ Please manually click the 'Login' button now.")
    time.sleep(10)  # Wait for manual login

except Exception as e:
    print(f"⚠ Error during login: {e}")
    driver.quit()
    exit()

# 🔹 Navigate to AI and related internships
driver.get("https://internshala.com/internships/artificial-intelligence-ai,computer-science,computer-vision,machine-learning,python-django-internship/")
print("🔍 Navigated to AI and related internships page.")

# Locate all internship containers
internship_list = driver.find_elements(By.XPATH, "//div[contains(@class, 'individual_internship')]")

for internship in internship_list:
    try:
        # 🔹 Extract Title and Check Relevance
        title_element = internship.find_element(By.XPATH, ".//div[contains(@class, 'company')]//h3[contains(@class, 'job-internship-name')]")
        title = title_element.text.strip()
        print(f"🔍 Internship Title: {title}")

        if not check_relevance(title):
            print("⏭ Skipping - Not Relevant")
            continue

        # Find and click the internship title
        internship_meta = internship.find_element(By.XPATH, ".//div[contains(@class, 'internship_meta')]")
        heading_container = internship_meta.find_element(By.XPATH, ".//div[contains(@class, 'internship-heading-container')]")
        internship_logo = heading_container.find_element(By.XPATH, ".//div[contains(@class, 'internship_logo')]")

        driver.execute_script("arguments[0].click();", internship_logo)
        print("✅ Clicked on internship successfully!")
        time.sleep(3)

        # 🔹 Find and Click 'Apply Now' Button
        try:
            apply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn') and contains(@class, 'btn-large')]"))
            )
            driver.execute_script("arguments[0].click();", apply_button)
            print("✅ Clicked 'Apply Now' button successfully!")
            time.sleep(3)

        except Exception as e:
            print(f"❌ Error finding 'Apply Now' button: {e}")

        # 🔹 Handle Cover Letter (If Required)
        try:
            cover_letter_section = driver.find_elements(By.XPATH, "//h4[contains(@class, 'question-heading')]")
            if cover_letter_section:
                print("📝 Cover letter required. Adding now...")
                cover_letter_box = driver.find_element(By.XPATH, "//div[contains(@class, 'ql-editor')]")
                cover_letter_box.click()
                cover_letter_text = """I am excited about the opportunity to work with an organization that values innovation, collaboration, and growth. Throughout my academic and professional journey, I have worked on impactful projects that demonstrate my dedication to solving complex problems and driving meaningful results. I believe in teamwork and am eager to contribute to the success of the organization."""
                cover_letter_box.send_keys(cover_letter_text)
                time.sleep(2)
            else:
                print("✅ No cover letter required.")

        except Exception as e:
            print(f"⚠ Error handling cover letter: {e}")

        # 🔹 Handle Additional Questions (Use Gemini API)
        filled_count = 0

        try:
            questions = driver.find_elements(By.CLASS_NAME, "additional_question")
            for question in questions:
                try:
                    question_text = question.find_element(By.TAG_NAME, "label").text.strip()
                    print(f"🔹 Processing: {question_text}")

                    # Check if the question has an input box
                    answer_box = question.find_elements(By.XPATH, ".//div[contains(@id, 'auto_resize_height')]")  # Use find_elements to prevent errors
                    if answer_box:
                        answer_text = generate_response(question_text)
                        print(f"✨ Gemini Answer: {answer_text}")

                        driver.execute_script("arguments[0].scrollIntoView(true);", answer_box[0])
                        time.sleep(2)

                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(answer_box[0]))
                        driver.execute_script("arguments[0].click();", answer_box[0])
                        time.sleep(1)

                        # Ensure input field is cleared before entering new text
                        driver.execute_script("arguments[0].innerText = '';", answer_box[0])
                        time.sleep(1)

                        # Send the answer for the current question
                        driver.execute_script("arguments[0].innerText = arguments[1];", answer_box[0], answer_text)
                        time.sleep(2)

                        filled_count += 1
                    else:
                        print("⚠ No input box detected. Waiting for user input...")
                        time.sleep(10)  # Pause to allow manual input if needed

                except Exception as e:
                    print(f"⚠ Error processing question: {e}")

        except Exception as e:
            print(f"⚠ Error finding additional questions: {e}")


        time.sleep(15)  # Allow user to review

        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        print("⚠ Please click 'Submit' manually within the next 15 seconds.")
        time.sleep(3)  # Extra time for manual submission
        
    except Exception as e:
        print(f"⚠ Error during application process: {e}")

# 🔹 Close WebDriver
driver.quit()
print("🎯 Application process completed!")
