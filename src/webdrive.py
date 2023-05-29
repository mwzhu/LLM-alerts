from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import io
from PIL import ImageChops
import json
from utils import promptGPT
import re
# def promptGPT(systemprompt, userprompt, model=constants.model):
#     print("""Inputting {} tokens into {}.""".format(num_tokens_from_messages(systemprompt+userprompt), model))
#     response = openai.ChatCompletion.create(
#       model=model,
#       temperature=0,
#       messages=[
#         {"role": "system", "content": systemprompt},
#         {"role": "user", "content": userprompt}])
#     return response["choices"][0]["message"]["content"]


system_prompt = """
    As an AI, you have the capability to pull different types of blockchain information. A user will provide you with an address or ENS (Ethereum Name Service) and specify whether they want to see tokens, NFTs, or transaction history associated with that address or ENS. Based on this input, you will output a command in a structured JSON format to get a screenshot of the required information.

    For example, if a user says "Could you display the NFTs associated with the account @elonmusk.eth?", your output would be:
    { 
        "command": "screenshot",
        "address_or_ens": "elonmusk.eth",
        "twitter_handle": "elonmusk.eth",
        "type_of_screenshot": "nfts"
    }
  User: "Can you provide the transaction history for my ENS mywallet.eth?"
   AI Output:
   { 
     "command": "screenshot",
     "address_or_ens": "mywallet.eth",
     "twitter_handle": "N/A",
     "type_of_screenshot": "transaction history"
   }
"""

def webDriveLLM(user_input):

    llm_result = promptGPT(system_prompt, user_input)
    #parse the json in the response
    # res = json.loads(res)
    # Extract the JSON command
    command_match = re.search(r'{(.+?)}', llm_result, re.DOTALL)
    command_json_str = command_match.group(0)

    # Extract the comment
    comment = llm_result.replace(command_json_str, '').strip()

    # Parse the command JSON
    command_json = json.loads(command_json_str)
    #get the address or ens
    address_or_ens = command_json["address_or_ens"]
    #get the type of screenshot
    type_of_screenshot =  command_json["type_of_screenshot"]
    #get the twitter handle
    twitter_handle =  command_json["twitter_handle"]

    url = screenshot_of_zerion_page(address_or_ens)
    return url

# webDriveLLM("Can you provide the transaction history for my ENS vitalik.eth?")





#STICHES IMAGES TOGETHER
def stitch_images(image_filenames, output_filename):
    # Load images
    images = [Image.open(filename) for filename in image_filenames]

    # Determine total width and maximum height
    total_width = max(image.size[0] for image in images)
    max_height = sum(image.size[1] for image in images)

    # Create new image object for result
    stitched_image = Image.new('RGB', (total_width, max_height))

    # Paste images
    current_height = 0
    for image in images:
        stitched_image.paste(image, (0, current_height))
        current_height += image.size[1]

     
    left_crop = 500
    right_crop = total_width - 300
    stitched_image = stitched_image.crop((left_crop, 0, right_crop, max_height))


    # Save resulting image
    stitched_image.save(output_filename)
    print("Saved stitched image as: ", output_filename)
    return output_filename



#TAKES 2 SCREENSHOTS
def screenshot_full_page(driver, filename):
    temp_filenames = []
    # Calculate total height of the page
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    
    # Initial viewport height (by JavaScript)
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Store all screenshots in a list
    screenshots = []

    # Scroll and capture screenshots
    for offset in range(0, total_height, int(viewport_height * 0.99)):  # Update here
        driver.execute_script(f"window.scrollTo(0, {offset});")
        # Wait to load page
        time.sleep(2)
        
        # Take screenshot and append to list of screenshots
        screenshot_as_png = driver.get_screenshot_as_png()
        screenshot = Image.open(io.BytesIO(screenshot_as_png))
        temp_filename = (filename.replace(".png", "") + "SC_" + str(offset) + ".png")
        screenshot.save(temp_filename)
        temp_filenames.append(temp_filename)
        screenshots.append(screenshot)

    # Get total width from the first screenshot
    total_width = screenshots[0].size[0]

    # Create a new image object with the total height and width of all screenshots
    stitched_image = Image.new('RGB', (total_width, total_height))

    # Paste screenshots into new image object
    current_height = 0
    for screenshot in screenshots:
        # Here we'll use paste(), which pastes the image at specified location.
        stitched_image.paste(screenshot, (0, current_height))
        current_height += screenshot.size[1]


    # Save stitched imageaf
    # stitched_image.save(filename)
    # print("Saved screenshot as ", filename)
    
    return temp_filenames 
   


from PIL import Image

def screenshot_of_zerion_page(address):
    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--window-size=375x812")  # iPhone X dimensions   

    # Set the webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # Navigate to url
    url = f'https://app.zerion.io/{address}/overview'
    driver.get(url)

    # Let the page load
    time.sleep(5)

    try:
        # Wait for up to 10 seconds before throwing a TimeoutException
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept']"))
        )
        def hide_element(driver, xpath):
            script = f"""
            var element = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (element) element.style.display = 'none';
            """
            driver.execute_script(script)

        # Usage:
        hide_element(driver, '//*[@id="PageWrapper"]/div/div[2]/div[2]')
        button.click()
        print("Button clicked!")
        sidebar_element = driver.find_element(By.ID, "SidebarDesktop")
        driver.execute_script("arguments[0].remove()", sidebar_element)
        print("Sidebar removed!")

    except Exception as e:
        print(f"Button not found or not clickable. Exception: {str(e)}")

    # Screenshot and save
    screenshots_filenames = screenshot_full_page(driver, f'{address}_overview.png')
    screenshot_full_url = stitch_images(screenshots_filenames, f'{address}_overview.png')
    
    # Close the driver
    driver.close()
    driver.quit()
    return [screenshot_full_url, url]

# Test with an address

# screenshot_of_zerion_page("0xd8da6bf26964af9d7eed9e03e53415d37aa96045")