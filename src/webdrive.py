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
from selenium.webdriver.common.by import By


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

    # Save resulting image
    stitched_image.save(output_filename)



def screenshot_full_page(driver, filename):
    temp_filenames = []
    # Calculate total height of the page
    total_height = driver.execute_script("return document.body.scrollHeight")
    #Remove the damn header
    menubar = driver.find_element(By.CLASS_NAME, "MobileVersion__TopBar-m4hzw4-0.igRbyj")
    menubar2 = driver.find_element(By.CLASS_NAME, "MobileVersion__SpaceBetween-m4hzw4-1.hIGhpK")
    element = driver.find_element(By.CLASS_NAME, "PageContentColumn-uudlam-0.gfHdoP")
    element2 = driver.find_element(By.CLASS_NAME, "shared__HStack-sc-1qg837v-1.iiBdOd")
    element3 = driver.find_element(By.CLASS_NAME, "Spacer__SpacerElement-sc-6ie5tt-0.eiiqPJ")
    driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", menubar)
    driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", menubar2)
    driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", element)
    driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", element2)
    driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", element3)
    #driver.execute_script("arguments[0].style.display = 'none';", element)
    # Initial viewport height (by JavaScript)
    #viewport_height = driver.execute_script("return window.innerHeight")
    viewport_height = 600
    driver.set_window_size(1024, 600)
    
    # Store all screenshots in a list
    screenshots = []
    height_deltas = []
    prev = 0
    # Scroll and capture screenshots
    for offset in range(0, total_height, viewport_height):
        print(offset)
        driver.execute_script(f"window.scrollTo(0, {offset});")
        # Wait to load page
        time.sleep(2)
        # Take screenshot and append to list of screenshots
        # Hide scrollbar
        driver.execute_script("document.body.style.overflow = 'hidden';")
        screenshot_as_png = driver.get_screenshot_as_png()
        driver.execute_script("document.body.style.overflow = 'auto';")
        screenshot = Image.open(io.BytesIO(screenshot_as_png))
        temp_filename = (filename.replace(".png", "") + "SC_" + str(offset) + ".png")
        screenshot.save(temp_filename)
        temp_filenames.append(temp_filename)
        screenshots.append(screenshot)
        height = driver.execute_script("return window.scrollY;")
        print(f'scroll height: {height}')
        height_deltas.append(height-prev)
        prev = height

    # Get total width from the first screenshot
    total_width = screenshots[0].size[0]

    # Create a new image object with the total height and width of all screenshots
    stitched_image = Image.new('RGB', (total_width, total_height))

    # Paste screenshots into new image object
    current_height = 0
    #numscrolls = total_height//viewport_height-1
    #remainder = total_height%viewport_height
    #scroll_lengths = []
    #if numscrolls > 0:
        #scroll_lengths.append(*[viewport_height]*numscrolls)
    ##scroll_lengths.append(remainder)
    #scroll_lengths.append(0)
    #print(scroll_lengths)
    height_deltas.pop(0)
    height_deltas.append(0)
    print(height_deltas)
    for (screenshot, height) in list(zip(screenshots,height_deltas)):
        # Here we'll use paste(), which pastes the image at specified location.
        stitched_image.paste(screenshot, (0, current_height))
        current_height += height#screenshot.size[1]

    # Save stitched image
    stitched_image.save(filename)
    print("Saved screenshot as ", filename)
    return 0#stitch_images(temp_filenames, "0x5a68c82e4355968db53177033ad3edcfd62accca_overview.png")
   


from PIL import Image




def screenshot_of_page(address):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--window-size=375x812")  # iPhone X dimensions   

    # Set the webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # Navigate to url
    url = f'https://app.zerion.io/{address}/overview'
    driver.get(url)

    # Let the page load
    time.sleep(2)

    try:
        # Wait for up to 10 seconds before throwing a TimeoutException
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept']"))
        )
        button.click()
        print("Button clicked!")
    except Exception as e:
        print(f"Button not found or not clickable. Exception: {str(e)}")

    # Screenshot and save
    screenshot_full_page(driver, f'{address}_overview.png')
    # Navigate to url
    driver.delete_all_cookies()  # Clear cookies
    driver.quit()  # Completely quit the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = f'https://app.zerion.io/{address}/nfts'
    driver.get(url)

    # Let the page load
    time.sleep(2)

    try:
        # Wait for up to 10 seconds before throwing a TimeoutException
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept']"))
        )
        button.click()
        print("Button clicked!")
    except Exception as e:
        print(f"Button not found or not clickable. Exception: {str(e)}")

    #Scroll down
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Screenshot and save
    driver.save_screenshot(f'{address}_nfts.png')
    screenshot_full_page(driver, f'{address}_nfts_fullpage.png')
    
    # Close the driver
    driver.close()
    driver.quit()

# Test with an address
screenshot_of_page("0xb6126af43b52ebd59afa0be472649035a0df6da7")
