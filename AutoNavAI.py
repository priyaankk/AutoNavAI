import os

from groq import Groq

import platform
import aiofiles
api_key=''
import os
os.environ['GROQ_API_KEY'] = 'INSERT_API_KEY_HERE'


import asyncio
from playwright.async_api import async_playwright

import playwright
import pytesseract
from PIL import Image
import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
import asyncio
from playwright.async_api import async_playwright


import base64

import json

smart_prompt = '''I will provide you with a search query. Your task is to analyze the query and improve it for better results in a Google search. 
Focus on making the query more specific, clear, and relevant to what the user is likely seeking. Avoid unnecessary words and include terms or phrases that target the desired information accurately. 
Give me a query for better search'''

prompt='''Imagine you are a robot browsing the web, just like humans. Now you need to complete a task. In each iteration,
you will receive an Observation that includes a screenshot of a webpage and some texts. 
Carefully analyze the bounding box information and the web page contents to identify the Numerical Label corresponding 
to the Web Element that requires interaction, then follow
the guidelines and choose one of the following actions:

1. Click a Web Element.
2. Delete existing content in a textbox and then type content.
3. Scroll up or down.
4. Wait 
5. Go back
7. Return to google to start over.
8. Download the file
9. Respond with the final answer

Correspondingly, Action should STRICTLY follow the format:

- Click [Numerical_Label] 
- Type [Numerical_Label]; [Content] 
- Scroll [Numerical_Label or WINDOW]; [up or down] 
- Wait 
- GoBack
- Bing
- Download
- ANSWER; [content]

Key Guidelines You MUST follow:

* Action guidelines *
1) Execute only one action per iteration.
2) Always click close on the popups.
3) When clicking or typing, ensure to select the correct bounding box.
4) Numeric labels lie in the top-left corner of their corresponding bounding boxes and are colored the same.
5) If the desired target is to do something like taking a action, you need to answer with ANSWER; FINISHED. For exmaple if i ask to write something or play a video

* Web Browsing Guidelines *
1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages
2) Select strategically to minimize time wasted.

Your reply should strictly follow the format:

Thought: {{Your brief thoughts (briefly summarize the info that will help ANSWER)}}
Action: {{One Action format you choose}}
Then the User will provide:
Observation: {{A labeled bounding boxes and contents given by User}}'''

import os


import nest_asyncio

# This is just required for running async playwright in a Jupyter notebook
nest_asyncio.apply()


import re

def parse_commands(text):
    # Define patterns for each command
    command_patterns = {
        'Click': r'Click \[?(\d+)\]?',
        'Type': r'Type \[?(\d+)\]?; (.*)',
        'Scroll': r'Scroll \[?(\d+|WINDOW)\]?; \[?(up|down)\]?',
        'Scroll1': r'Scroll \[?(up|down)\]?; \[?(\d+|WINDOW)\]?',
        'Wait': r'Wait',
        'GoBack': r'GoBack',
        'Bing': r'Bing',
        'Google': r'Google',
        'Download': r'Download; \[?(.*)\]?; \[?(.*)\]?',
        'ANSWER': r'ANSWER; (.*)',
        'FINISHED': r'FINISHED'
    }
    
    print("***************", text)
    # Dictionary to hold the parsed commands
    parsed_commands = []
    
    # Search for each command in the text
    for command, pattern in command_patterns.items():
        for match in re.finditer(pattern, text):
            if command in ['Click', 'Type', 'Scroll', 'Scroll1', 'ANSWER', 'Download']:
                # Commands with parameters
                if command == 'Scroll1':
                    command = 'Scroll'
                    parsed_commands.append({command: match.groups()[::-1]})
                else:
                    parsed_commands.append({command: match.groups()})
            else:
                # Commands without specific parameters
                parsed_commands.append(command)
    
    return parsed_commands

# Example text input
# text = '''Thought: The screenshot shows a search result for iPhones on Amazon.in.
# The price of an iPhone is visible in the search results, specifically for an iPhone 13 (128GB) - Blue.\n\nAction: ANSWER; ₹51,990'''

# # Parse the example text
# parsed_commands = parse_commands(text)
# parsed_commands


async def type_command(query, location):
    import platform
    await annot_elements[location].click()
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(query)
    await page.keyboard.press("Enter")
    

def llama3_agent(q):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": q,
            }
        ],
        model="llama3-70b-8192",
    )

    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

# parsed_commands = parse_commands('Action: {{Scroll WINDOW; down}}')
# parsed_commands

import asyncio
import base64

from langchain_core.runnables import chain as chain_decorator

# Some javascript we will run on each step
# to take a screenshot of the page, select the
# elements to annotate, and add bounding boxes
with open("mark_page.js") as f:
    mark_page_script = f.read()



async def mark_page(page):
    with open("mark_page.js") as f:
        mark_page_script = f.read()
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except:
            # May be loading...
            asyncio.sleep(3)
    screenshot = await page.screenshot(path='annotated_screenshot_with_numbers.png')
    # Ensure the bboxes don't follow us around
    await page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }

def format_descriptions(state):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return {**state, "bbox_descriptions": bbox_descriptions}

async def click_on_labeled_element(page, label_number, labeled_elements):
    """
    Clicks on an element identified by its label number from the labeled bounding boxes.
    
    Args:
        page: The Playwright page instance.
        label_number: The numerical label of the element to click (e.g., 5).
        labeled_elements: The list of labeled elements returned by `markPage`.
    """
    try:
        # Find the element with the specified label
        element = labeled_elements[label_number]
        x, y = element["x"], element["y"]

        # Perform the click action
        await page.mouse.click(x, y)
        print(f"Clicked on element with label {label_number}: {element.get('text', 'No text')}")
    except IndexError:
        print(f"Label {label_number} does not exist in the labeled elements.")
    except Exception as e:
        print(f"Error clicking on element with label {label_number}: {e}")


async def click(page, state, query, location):
    # - Click [Numerical_Label]
    
    bbox_id = location
    bbox_id = int(bbox_id)
    try:
        bbox = state["bboxes"][bbox_id]
    except:
        return f"Error: no bbox for : {bbox_id}"
    x, y = bbox["x"], bbox["y"]
    res = await page.mouse.click(x, y)
    # TODO: In the paper, they automatically parse any downloaded PDFs
    # We could add something similar here as well and generally
    # improve response format.
    return  res

async def type_text(page, location,text_content, state):
    bbox_id = location
    bbox_id = int(bbox_id)
    bbox = state["bboxes"][bbox_id]
    x, y = bbox["x"], bbox["y"]
    await page.mouse.click(x, y)
    # Check if MacOS
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(text_content)
    page = await page.keyboard.press("Enter")
    return page

async def scroll(page, state, scroll_args):
    if scroll_args is None or len(scroll_args) != 2:
        return "Failed to scroll due to incorrect arguments."

    target, direction = scroll_args

    if target.upper() == "WINDOW":
        # Not sure the best value for this:
        scroll_amount = 500
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.evaluate(f"window.scrollBy(0, {scroll_direction})")
    else:
        # Scrolling within a specific element
        scroll_amount = 200
        target_id = int(target)
        bbox = state["bboxes"][target_id]
        x, y = bbox["x"], bbox["y"]
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.mouse.move(x, y)
        await page.mouse.wheel(0, scroll_direction)

    return f"Scrolled {direction} in {'window' if target.upper() == 'WINDOW' else 'element'}"

async def wait():
    sleep_time = 5
    await asyncio.sleep(sleep_time)
    return f"Waited for {sleep_time}s."


async def go_back(page):
    await page.go_back()
    return f"Navigated back a page to {page.url}."


async def to_google(page):
    await page.goto("https://www.google.com/")
    return "Navigated to google.com."

async def download_pdf(page, pdf_link_selector, save_path = ""):
    """
    Downloads a PDF file by clicking a link and saving the response.
    
    Args:
        page: Playwright page object.
        pdf_link_selector (str): The selector for the link that opens the PDF.
        save_path (str): The file path where the PDF should be saved.

    Returns:
        str: A confirmation message after the PDF is downloaded.
    """
    print("Goes to download function!!!!!")
    # Wait for a response that includes '.pdf' in the URL
    async with page.expect_response(lambda response: response.url.endswith(".pdf")) as response_info:
        await page.click(pdf_link_selector)  # Click on the link to trigger the PDF response

    response = await response_info.value  # Get the response object
    pdf_content = await response.body()   # Get the binary content of the PDF

    # Save the PDF locally
    async with aiofiles.open(save_path, 'wb') as file:
        await file.write(pdf_content)

    return f"PDF downloaded and saved at {save_path}."


def get_prompt(text, question):
    return f'''
        Given the following information 
        Content:
        {text}
        and a task
        Question:
        {question}
        Reply with answer if it is not an action and answer is available in the text.
        Reply with NO If you do not know the answer
        Reply with NO If your response is a set of actions to be taken
        Reply  with NO If the question involves an action 
        
        example:
        Question:
        Play X on youtube
        Answer: NO
        Dont add any preamble
        Answer:
    '''

async def get_information1(query,page):
    

    prev_image = ''
    answer = ''
    while True:
        
        try:
            obj = await mark_page(page)
        except Exception as e:
            # print(e)
            await wait()
            continue
        obj = format_descriptions(obj)
    
        text = await page.inner_text('body')
        if 'google' not in page.url:
        
            p = get_prompt(text, query)
            # print("prompt is",p)
            p = llama3_agent(p)
            if p != 'NO':
                return p

        new_query =  prompt + "\n Valid Bounding boxes: " + obj['bbox_descriptions']  \
        + '\nQuestion:'+query
        resp = llama3_agent(new_query)
        smartt_prompt = smart_prompt + query
        print("p********************", resp)
        parsed_commands =parse_commands(resp)[0]
        
        print(parsed_commands)
        if 'Type' in parsed_commands:
            location = int(parsed_commands['Type'][0])
            await type_text(page, location, parsed_commands['Type'][1], obj)
        elif 'Click' in parsed_commands:
            location = int(parsed_commands['Click'][0])
            await click(page, obj, query, location)
        elif 'Bing' in parsed_commands:
            await page.goto('https://www.bing.com/')
            
        elif 'Scroll' in parsed_commands:
            await scroll(page, obj, parsed_commands['Scroll'])
            
        elif 'Wait' in parsed_commands:
            await wait()
        elif 'GoBack' in parsed_commands:
            await go_back(page)
        elif 'Google' in parsed_commands:
            await to_google(page)
            location = int(parsed_commands['Type'][0])
            type_smartt_prompt = llama3_agent(smartt_prompt)
            await type_text(page, location, type_smartt_prompt, obj)
        elif 'Download' in parsed_commands:
            print("might download!!!")
            pdf_selector = parsed_commands['Download'][0] if 'Download' in parsed_commands else None
            await download_pdf(page, pdf_selector, "/downloads/attentions.ai/")
        elif 'ANSWER' in parsed_commands:
            answer = parsed_commands['ANSWER'][0]
            print(answer)
            break
        elif 'FINISHED' in parsed_commands:
            break
    #await browser.close()
    print("returning answer")
    return answer



async def main():
    # Start Playwright
    async with async_playwright() as playwright:
        # Launch Chromium browser
        browser = await playwright.chromium.launch(headless=False)

        # Open a new page
        page = await browser.new_page()
        # Navigate to a website (example: Google)
        await page.goto('https://www.google.in')

        await get_information1('get me prices of iphones on amazon',page)
        # Close the browser
        await browser.close()

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
