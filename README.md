# **AutoNavAI**

## **Overview**
This project leverages AI-powered web browsing automation, enabling a bot to interact with websites in real-time, execute tasks, and fetch data autonomously. The bot can navigate, click elements, scroll, fill forms, download files, and retrieve answers based on the content of the page using advanced machine learning models like Llama. It processes actions step-by-step, ensuring efficient interaction with complex websites.

## **Key Features**
- **AI-driven Web Automation**: The bot can simulate human-like behavior on websites—clicking buttons, typing text, scrolling, and more.
- **Real-time Task Completion**: It identifies actions needed to complete tasks on webpages, such as searching for information, submitting forms, and extracting data.
- **Seamless Web Integration**: Interacts with web elements dynamically by using bounding boxes, enhancing accuracy and speed in identifying elements.
- **Multi-Step Actions**: Capable of executing complex workflows across different web pages by analyzing screenshots and textual descriptions, making it adaptable to diverse use cases.
- **Autonomous Interaction**: Based on user queries, it autonomously navigates to websites (e.g., Google, Amazon) and completes tasks like price comparison, form filling, and file downloading.

## **How It Works**
1. **Query Interpretation**: Users input a task (e.g., "Get prices of iPhones on Amazon"), which is processed by the Llama3 AI model.
2. **Action Detection**: Based on the query, the system generates a list of actions to take (e.g., click a button, type text).
3. **Web Interaction**: Using Playwright, the bot interacts with the webpage—identifying elements by bounding boxes, clicking them, filling in forms, or extracting data.
4. **Data Extraction**: The bot then performs actions such as retrieving prices or extracting other relevant information and returning it to the user.

## **Prerequisites**
- Python 3.x
- Playwright for Python: `pip install playwright`
- Tesseract-OCR: `pip install pytesseract`
- Groq API: You need a valid API key for the Groq service.

## **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/priyaankk/AutoNavAI.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the Groq API key:
   - In the environment variable, set `GROQ_API_KEY` to your API key:
   ```bash
   export GROQ_API_KEY="your_api_key"
   ```

## **Usage**
1. In the `main.py` file, define your task query.
2. Run the script:
   ```bash
   python main.py
   ```
3. The bot will open a Chromium browser, navigate to the appropriate site, and execute the task step-by-step.
4. The final result (e.g., price, information) will be printed in the terminal.

## **Example**
Here’s an example of how the system interacts:
- **User Input**: "Get me prices of iPhones on Amazon."
- The bot navigates to Amazon, identifies price elements, and returns the price of the first iPhone listed.

## **Future Enhancements**
- **Support for More Complex Websites**: Extend compatibility to more complex, JavaScript-heavy websites.
- **Multiple Query Types**: Allow the bot to handle more varied queries and execute more diverse tasks.
- **Improved Error Handling**: Enhance the system's ability to handle unexpected errors and interactions.

## **Contributing**
If you would like to contribute to the project, feel free to fork the repository, submit pull requests, or open issues to suggest improvements.
