from smolagents import CodeAgent, DuckDuckGoSearchTool, load_tool, tool
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from bs4 import BeautifulSoup
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from Gradio_UI import GradioUI
from dotenv import load_dotenv
import os

# Simple response object to match smolagents expectations
class ChatMessage:
    def __init__(self, content):
        self.content = content

# Custom Azure Model class for smolagents
class AzureModel:
    def __init__(self, endpoint, token, model_name, max_tokens=2096, temperature=0.5):
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def __call__(self, messages, **kwargs):
        # Convert smolagents message format to Azure format
        azure_messages = []
        
        if isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, dict):
                    # Extract role (convert enum to string if needed)
                    role = str(msg.get('role', 'user')).lower()
                    if 'system' in role:
                        role = 'system'
                    elif 'user' in role:
                        role = 'user'
                    elif 'assistant' in role:
                        role = 'assistant'
                    else:
                        role = 'user'  # default to user
                    
                    # Extract content - handle complex content structure
                    content = msg.get('content', '')
                    
                    # If content is a list (complex format from smolagents)
                    if isinstance(content, list):
                        # Extract text from the content list
                        text_content = ""
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_content += item.get('text', '')
                        content = text_content
                    
                    # Convert to string if not already
                    content = str(content) if content else ""
                    
                    # Create appropriate Azure message
                    if role == 'system':
                        azure_messages.append(SystemMessage(content))
                    else:
                        azure_messages.append(UserMessage(content))
                        
                elif isinstance(msg, str):
                    azure_messages.append(UserMessage(msg))
                else:
                    azure_messages.append(UserMessage(str(msg)))
        else:
            azure_messages.append(UserMessage(str(messages)))
        
        # Ensure we have at least one message
        if not azure_messages:
            azure_messages.append(UserMessage("Hello"))
        
        try:
            # Make the API call
            response = self.client.complete(
                messages=azure_messages,
                temperature=kwargs.get('temperature', self.temperature),
                top_p=kwargs.get('top_p', 1.0),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                model=self.model_name
            )
            
            return ChatMessage(response.choices[0].message.content)
        except Exception as e:
            print(f"Azure API Error: {e}")
            return ChatMessage(f"Error calling Azure API: {str(e)}")

# Azure API configuration
load_dotenv()  # Loads from .env by default

endpoint = os.getenv("AZURE_ENDPOINT")
model_name = os.getenv("AZURE_MODEL_NAME")
token = os.getenv("AZURE_TOKEN")

@tool
def summarize_webpage(url: str) -> str:
    """A tool that fetches and summarizes text content from a webpage.
    Args:
        url: A valid URL to a webpage.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text().strip() for p in paragraphs[:30] if p.get_text().strip())
        
        if not text:
            # Fallback to other text elements if no paragraphs found
            text = soup.get_text()[:2000]
            
        return f"Summary of content from {url}: {text[:700]}..."
    except requests.RequestException as e:
        return f"Failed to fetch the webpage {url}: Network error - {str(e)}"
    except Exception as e:
        return f"Failed to process the webpage {url}: {str(e)}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except pytz.exceptions.UnknownTimeZoneError:
        return f"Error: Unknown timezone '{timezone}'. Please provide a valid timezone."
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

@tool
def search_web(query: str) -> str:
    """A tool that searches the web using DuckDuckGo.
    Args:
        query: The search query string.
    """
    try:
        search_tool = DuckDuckGoSearchTool()
        results = search_tool(query)
        return f"Search results for '{query}': {results}"
    except Exception as e:
        return f"Error searching for '{query}': {str(e)}"

# Initialize final answer tool
final_answer = FinalAnswerTool()

# Create Azure model instance
model = AzureModel(
    endpoint=endpoint,
    token=token,
    model_name=model_name,
    max_tokens=2096,
    temperature=0.5
)

# Load prompt templates with error handling
try:
    with open("prompts.yaml", 'r') as stream:
        prompt_templates = yaml.safe_load(stream)
except FileNotFoundError:
    print("Warning: prompts.yaml not found. Using default prompts.")
    prompt_templates = None
except yaml.YAMLError as e:
    print(f"Warning: Error parsing prompts.yaml: {e}. Using default prompts.")
    prompt_templates = None

# Create agent with all tools
agent = CodeAgent(
    model=model,
    tools=[final_answer, summarize_webpage, get_current_time_in_timezone, search_web],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name="WebAgent",
    description="An AI agent that can search the web, summarize webpages, and get current time information."
)

# Launch the Gradio UI
if __name__ == "__main__":
    try:
        GradioUI(agent).launch()
    except Exception as e:
        print(f"Error launching Gradio UI: {e}")
        print("Make sure all dependencies are installed and the Gradio_UI module is available.")