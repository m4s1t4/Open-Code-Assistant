# Open Code Assistant

This project is an open source wizard that uses various tools and APIs to assist in software development. The wizard can perform tasks such as creating and editing files, reading file contents, listing files in a directory, performing web searches, taking screenshots, and more.

## Project description

The wizard is designed to interact with the user through the console, allowing them to execute commands and receive responses in real time. It uses the OpenAI API to generate responses and the Tavily API to perform advanced internet searches. Additionally, it can process images and handle clipboard content.

## Instalation

1. Clone this repositori:
    ```sh
    git clone https://github.com/JoseMRodriguezM/Open-Code-Assistant.git
    cd Open-Code-Assistant
    ```

2. Now create a virtual enviroment:
    ```sh
    python -m venv venv
    source venv/bin/activate  #On windows`venv\Scripts\activate`
    ```

3. Install the dependecies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project root and add your API keys:
    ```env
    OPENAI_API_KEY=YOUR_API_KEY
    TAVILY_API_KEY=YOUR_API_KEY
    ```

## Use

To start the assistant, simply run the `app.py` file:
```sh
python app.py
```

### Available Commands

- **`exit`**: Exit the assistant.
- **`image`**: Process an image. You will be prompted to drag and drop the image into the console.
- **`take screenshot`**: Take a screenshot and save it in the `img` directory.

### Example of Use

1. Start the assistant:
 ```sh
 python app.py
 ```

2. Enter a command:
 ```sh
 User: create a new file called snake.py and store the snake game code made in python
 ```

3. Follow the assistant's instructions to complete the task.
