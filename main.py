import os
import io
import json
import dotenv
import base64
import difflib
import pyperclip
from openai import OpenAI
from tools.tools import tools
from tavily import TavilyClient
from prompts.prompts import base_system_prompt, automode_system_prompt
from PIL import Image
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.markdown import Markdown

# -------- Importing api keys -------- #
dotenv.load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# -------- Some configruations -------- #
console = Console()
client = OpenAI()
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Set up conversation memory.
conversation_history = []

# -------- Prompts part -------- #

base_sys_prompt = base_system_prompt
automode_prompt = automode_system_prompt


def update_system_prompt(current_iteration=None, max_iterations=None):
    global base_system_prompt, automode_system_prompt
    chain_of_thought_prompt = """
    Answer the user's request using relevant tools (if they are available). Before calling a tool, do some analysis within <thinking></thinking> tags. First, think about which of the provided tools is the relevant tool to answer the user's request. Second, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, close the thinking tag and proceed with the tool call. BUT, if one of the values for a required parameter is missing, DO NOT invoke the function (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters. DO NOT ask for more information on optional parameters if it is not provided.

    Do not reflect on the quality of the returned search results in your response.
    """
    return base_system_prompt + "\n\n" + chain_of_thought_prompt


# -------- Tools part -------- #


def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"


def create_file(path, content=""):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"File created successfully: {path}")
        return f"File created successfully: {path}"
    except Exception as e:
        error_message = f"Error creating file: {str(e)}"
        print(error_message)
        return error_message


def read_file(path):
    try:
        with open(path, "r") as f:
            content = f.read()
            return content
    except Exception as e:
        return f"Error reading the file: {str(e)}"


def list_files(path="."):
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"


def highlight_diff(diff_text):
    return Syntax(diff_text, "diff", theme="monokai", line_numbers=True)


def generate_and_apply_diff(original_content, new_content, path):
    diff = list(
        difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a\\{path}",
            tofile=f"b\\{path}",
            n=3,
        )
    )
    if not diff:
        return "No changes detected."
    try:
        with open(path, "w") as f:
            f.writelines(new_content)
        diff_text = "".join(diff)
        highlighted_diff = highlight_diff(diff_text)

        diff_panel = Panel(
            highlighted_diff,
            title=f"Changes in {path}",
            expand=False,
            border_style="cyan",
        )
        console.print(diff_panel)

        added_lines = sum(
            1 for line in diff if line.startswith("+") and not line.startswith("+++")
        )
        removed_lines = sum(
            1 for line in diff if line.startswith("-") and not line.startswith("---")
        )

        summary = f"Changes applied to {path}: \n"
        summary += f" Lines added: {added_lines}\n"
        summary += f" Lines removed: {removed_lines}\n"
    except Exception as e:
        error_panel = Panel(
            f"Error: {str(e)}", title="Error Applying Changes", style="bold red"
        )
        console.print(error_panel)
        return f"Error applying changes: {str(e)}"


def edit_and_apply(path, new_content):
    try:
        with open(path, "r") as file:
            original_content = file.read()
        if new_content != original_content:
            diff_result = generate_and_apply_diff(original_content, new_content, path)
            return f"Changes applied to {path}: \n{diff_result}"
        else:
            return f"No changes needed for {path}"
    except Exception as e:
        return f"Error editing/applying to file: {str(e)}"


def tavily_search(query):
    try:
        response = tavily.qna_search(query=query, search_depth="advanced")
        return response
    except Exception as e:
        return f"Error performing search: {str(e)}"


def get_clipboard_text():
    cliboard_content = pyperclip.paste()
    if isinstance(cliboard_content, str):
        return cliboard_content
    else:
        print("No clipboard text copied")
        return None


def encode_image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.DEFAULT_STRATEGY)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="JPEG")
            return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
    except Exception as e:
        return f"Error encoding image: {str(e)}"


# -------- AI Model part -------- #
def chat_with_gpt4(user_input, tools, image_path=None):
    global conversation_history

    current_conversation = []
    if image_path:
        console.print(
            Panel(
                f"Processing image at path: {image_path}",
                title_align="left",
                title="Image Processing",
                expand=False,
                style="yellow",
            )
        )
        image_base64 = encode_image_to_base64(image_path)

        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
                {"type": "text", "text": f"User input for image: {user_input}"},
            ],
        }
        current_conversation.append(image_message)
        console.print(
            Panel(
                "Image message added to conversation history",
                title_align="left",
                title="Image Added",
                style="green",
            )
        )
    else:
        current_conversation.append({"role": "user", "content": user_input})

    messages = conversation_history + current_conversation

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=300,
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "create_file": create_file,
            "create_folder": create_folder,
            "edit_and_apply": edit_and_apply,
            "list_files": list_files,
            "read_file": read_file,
            "tavily_search": tavily_search,
            "get_clipboard_text": get_clipboard_text,
        }

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            current_conversation.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "assistant",
                    "name": function_name,
                    "input": function_args,
                    "content": function_response,
                }
            )
            messages = conversation_history + current_conversation
        tools_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        response_with_tools = tools_response.choices[0].message.content
        current_conversation.append(
            {"role": "assistant", "content": response_with_tools}
        )
        conversation_history = messages + [
            {"role": "assistant", "content": response_with_tools}
        ]
        console.print(
            Panel(
                Markdown(response_with_tools),
                title="Assistant",
                title_align="left",
            )
        )
    else:
        final_response = response_message.content
        current_conversation.append({"role": "assistant", "content": final_response})
        conversation_history = messages + [
            {"role": "assistant", "content": final_response}
        ]
        console.print(
            Panel(
                Markdown(final_response),
                title="Assistant",
                title_align="left",
            )
        )
        return final_response


def main():
    console.print(
        Panel(
            "Welcome to the OpenAI Engineer Chat with Image Support!",
            title="Welcome",
            style="bold green",
        )
    )
    while True:
        user_input = console.input("[bold cyan]User:[/bold cyan] ")

        if user_input.lower() == "exit":
            console.print(
                Panel(
                    "Thank you for chatting. Goodbye!",
                    title_align="left",
                    title="Goodbye",
                    style="bold green",
                )
            )
            break
        elif user_input.lower() == "image":
            image_path = (
                console.input(
                    "[bold cyan]Drag and drop your image here, then press enter:[/bold cyan] "
                )
                .strip()
                .replace("'", "")
            )

            if os.path.isfile(image_path):
                user_input = console.input(
                    "[bold cyan]You (prompt for image):[/bold cyan] "
                )
                chat_with_gpt4(user_input, tools, image_path)

            else:
                console.print(
                    Panel(
                        "Invalid image path. Please try again.",
                        title="Error",
                        style="bold red",
                    )
                )
        else:
            chat_with_gpt4(user_input, tools)


if __name__ == "__main__":
    main()
