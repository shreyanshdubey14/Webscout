#########################################
# Code Generated by o3-mini-high
#########################################
import asyncio
import json
import os
import random
import re
import string
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Union, Optional

import httpx
from httpx import AsyncClient, HTTPStatusError

# For image models using validation. Adjust based on organization internal pydantic.
from pydantic import BaseModel, validator

# Rich is retained for logging within image methods.
from rich.console import Console
from rich.markdown import Markdown

console = Console()

#########################################
# New Enums and functions for endpoints,
# headers, models, file upload and images.
#########################################

class Endpoint(Enum):
    INIT = "https://gemini.google.com/app"
    GENERATE = "https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate"
    ROTATE_COOKIES = "https://accounts.google.com/RotateCookies"
    UPLOAD = "https://content-push.googleapis.com/upload"

class Headers(Enum):
    GEMINI = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Host": "gemini.google.com",
        "Origin": "https://gemini.google.com",
        "Referer": "https://gemini.google.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Same-Domain": "1",
    }
    ROTATE_COOKIES = {
        "Content-Type": "application/json",
    }
    UPLOAD = {
        "Push-ID": "feeds/mcudyrk2a4khkz",
    }

class Model(Enum):
    UNSPECIFIED = ("unspecified", {}, False)
    G_2_0_FLASH = (
        "gemini-2.0-flash",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"f299729663a2343f"]'},
        False,
    )
    G_2_0_FLASH_EXP = (
        "gemini-2.0-flash-exp",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"f299729663a2343f"]'},
        False,
    )  # Deprecated, should be removed in the future
    G_2_0_FLASH_THINKING = (
        "gemini-2.0-flash-thinking",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"9c17b1863f581b8a"]'},
        False,
    )
    G_2_0_FLASH_THINKING_WITH_APPS = (
        "gemini-2.0-flash-thinking-with-apps",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"f8f8f5ea629f5d37"]'},
        False,
    )
    G_2_0_EXP_ADVANCED = (
        "gemini-2.0-exp-advanced",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"b1e46a6037e6aa9f"]'},
        True,
    )
    G_1_5_FLASH = (
        "gemini-1.5-flash",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"418ab5ea040b5c43"]'},
        False,
    )
    G_1_5_PRO = (
        "gemini-1.5-pro",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"9d60dfae93c9ff1f"]'},
        True,
    )
    G_1_5_PRO_RESEARCH = (
        "gemini-1.5-pro-research",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"e5a44cb1dae2b489"]'},
        True,
    )

    def __init__(self, name: str, header: dict, advanced_only: bool):
        self.model_name = name
        self.model_header = header
        self.advanced_only = advanced_only

    @classmethod
    def from_name(cls, name: str) -> "Model":
        for model in cls:
            if model.model_name == name:
                return model
        raise ValueError(
            f"Unknown model name: {name}. Available models: {', '.join([m.model_name for m in cls])}"
        )

async def upload_file(file: Union[bytes, str, Path], proxy: Optional[str] = None) -> str:
    """
    Upload a file to Google's server and return its identifier.

    Parameters:
        file: bytes | str | Path
            File data in bytes, or path to the file to be uploaded.
        proxy: str, optional
            Proxy URL.

    Returns:
        str: Identifier of the uploaded file.
    Raises:
        httpx.HTTPStatusError: If the upload request failed.
    """
    if not isinstance(file, bytes):
        with open(file, "rb") as f:
            file = f.read()

    async with AsyncClient(http2=True, proxies=proxy) as client:
        response = await client.post(
            url=Endpoint.UPLOAD.value,
            headers=Headers.UPLOAD.value,
            files={"file": file},
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.text

#########################################
# Cookie loading and Chatbot classes
#########################################

def load_cookies(cookie_path: str) -> Tuple[str, str]:
    """Loads cookies from the provided JSON file."""
    try:
        with open(cookie_path, 'r') as file:
            cookies = json.load(file)
        session_auth1 = next(item['value'] for item in cookies if item['name'] == '__Secure-1PSID')
        session_auth2 = next(item['value'] for item in cookies if item['name'] == '__Secure-1PSIDTS')
        return session_auth1, session_auth2
    except FileNotFoundError:
        raise Exception(f"Cookie file not found at path: {cookie_path}")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON format in the cookie file.")
    except StopIteration:
        raise Exception("Required cookies not found in the cookie file.")

class Chatbot:
    """
    Synchronous wrapper for the AsyncChatbot class.
    """
    def __init__(
        self,
        cookie_path: str,
        proxy: dict = None,
        timeout: int = 20,
        model: Model = Model.UNSPECIFIED
    ):
        self.loop = asyncio.get_event_loop()
        self.secure_1psid, self.secure_1psidts = load_cookies(cookie_path)
        self.async_chatbot = self.loop.run_until_complete(
            AsyncChatbot.create(self.secure_1psid, self.secure_1psidts, proxy, timeout, model)
        )

    def save_conversation(self, file_path: str, conversation_name: str):
        return self.loop.run_until_complete(
            self.async_chatbot.save_conversation(file_path, conversation_name)
        )

    def load_conversations(self, file_path: str) -> List[Dict]:
        return self.loop.run_until_complete(
            self.async_chatbot.load_conversations(file_path)
        )

    def load_conversation(self, file_path: str, conversation_name: str) -> bool:
        return self.loop.run_until_complete(
            self.async_chatbot.load_conversation(file_path, conversation_name)
        )

    def ask(self, message: str) -> dict:
        return self.loop.run_until_complete(self.async_chatbot.ask(message))

class AsyncChatbot:
    """
    A class to interact with Google Gemini.
    Parameters:
        secure_1psid: str
            The __Secure-1PSID cookie.
        secure_1psidts: str
            The __Secure-1PSIDTS cookie.
        proxy: dict
            Http request proxy.
        timeout: int
            Request timeout in seconds.
        model: Model
            Selected model for the session.
    """
    __slots__ = [
        "headers",
        "_reqid",
        "SNlM0e",
        "conversation_id",
        "response_id",
        "choice_id",
        "proxy",
        "secure_1psidts",
        "secure_1psid",
        "session",
        "timeout",
        "model",
    ]

    def __init__(
        self,
        secure_1psid: str,
        secure_1psidts: str,
        proxy: dict = None,
        timeout: int = 20,
        model: Model = Model.UNSPECIFIED,
    ):
        headers = Headers.GEMINI.value.copy()
        if model != Model.UNSPECIFIED:
            headers.update(model.model_header)
        self._reqid = int("".join(random.choices(string.digits, k=4)))
        self.proxy = proxy
        self.conversation_id = ""
        self.response_id = ""
        self.choice_id = ""
        self.secure_1psid = secure_1psid
        self.secure_1psidts = secure_1psidts
        self.session = httpx.AsyncClient(proxies=self.proxy)
        self.session.headers = headers
        self.session.cookies.set("__Secure-1PSID", secure_1psid)
        self.session.cookies.set("__Secure-1PSIDTS", secure_1psidts)
        self.timeout = timeout
        self.model = model

    @classmethod
    async def create(
        cls,
        secure_1psid: str,
        secure_1psidts: str,
        proxy: dict = None,
        timeout: int = 20,
        model: Model = Model.UNSPECIFIED,
    ) -> "AsyncChatbot":
        instance = cls(secure_1psid, secure_1psidts, proxy, timeout, model)
        instance.SNlM0e = await instance.__get_snlm0e()
        return instance

    async def save_conversation(self, file_path: str, conversation_name: str) -> None:
        conversations = await self.load_conversations(file_path)
        conversation_exists = False
        for conversation in conversations:
            if conversation["conversation_name"] == conversation_name:
                conversation["conversation_name"] = conversation_name
                conversation["_reqid"] = self._reqid
                conversation["conversation_id"] = self.conversation_id
                conversation["response_id"] = self.response_id
                conversation["choice_id"] = self.choice_id
                conversation["SNlM0e"] = self.SNlM0e
                conversation_exists = True
        if not conversation_exists:
            conversation = {
                "conversation_name": conversation_name,
                "_reqid": self._reqid,
                "conversation_id": self.conversation_id,
                "response_id": self.response_id,
                "choice_id": self.choice_id,
                "SNlM0e": self.SNlM0e,
            }
            conversations.append(conversation)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversations, f, indent=4)

    async def load_conversations(self, file_path: str) -> List[Dict]:
        if not os.path.isfile(file_path):
            return []
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    async def load_conversation(self, file_path: str, conversation_name: str) -> bool:
        conversations = await self.load_conversations(file_path)
        for conversation in conversations:
            if conversation["conversation_name"] == conversation_name:
                self._reqid = conversation["_reqid"]
                self.conversation_id = conversation["conversation_id"]
                self.response_id = conversation["response_id"]
                self.choice_id = conversation["choice_id"]
                self.SNlM0e = conversation["SNlM0e"]
                return True
        return False

    async def __get_snlm0e(self):
        if not (self.secure_1psid and self.secure_1psidts) or self.secure_1psid[:2] != "g.":
            raise Exception("Enter correct __Secure_1PSID and __Secure_1PSIDTS value. __Secure_1PSID value must start with a g.")
        resp = await self.session.get(Endpoint.INIT.value, timeout=10, follow_redirects=True)
        if resp.status_code != 200:
            raise Exception(f"Response code not 200. Response Status is {resp.status_code}")
        snlm0e_match = re.search(r'"SNlM0e":"(.*?)"', resp.text)
        if not snlm0e_match:
            raise Exception("SNlM0e value not found in response. Check __Secure_1PSID value."
                            "\nNOTE: The cookies expire after a short period; ensure you update them frequently."
                            f" Failed with status {resp.status_code} - {resp.reason_phrase}")
        return snlm0e_match.group(1)

    async def ask(self, message: str) -> dict:
        params = {
            "bl": "boq_assistant-bard-web-server_20230713.13_p0",
            "_reqid": str(self._reqid),
            "rt": "c",
        }
        message_struct = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        data = {
            "f.req": json.dumps([None, json.dumps(message_struct)]),
            "at": self.SNlM0e,
        }
        resp = await self.session.post(
            Endpoint.GENERATE.value,
            params=params,
            data=data,
            timeout=self.timeout,
        )
        try:
            chat_data_line = resp.content.splitlines()[3]
            chat_data = json.loads(chat_data_line)[0][2]
        except (IndexError, json.JSONDecodeError):
            return {"content": f"Gemini encountered an error: {resp.content}."}
        if not chat_data:
            return {"content": f"Gemini returned empty response: {resp.content}."}
        json_chat_data = json.loads(chat_data)
        images = []
        if len(json_chat_data) >= 3:
            if len(json_chat_data[4][0]) >= 4 and json_chat_data[4][0][4]:
                for img in json_chat_data[4][0][4]:
                    images.append(img[0][0][0])
        results = {
            "content": json_chat_data[4][0][1][0],
            "conversation_id": json_chat_data[1][0],
            "response_id": json_chat_data[1][1],
            "factualityQueries": json_chat_data[3],
            "textQuery": json_chat_data[2][0] if json_chat_data[2] is not None else "",
            "choices": [{"id": i[0], "content": i[1]} for i in json_chat_data[4]],
            "images": images,
        }
        self.conversation_id = results["conversation_id"]
        self.response_id = results["response_id"]
        self.choice_id = results["choices"][0]["id"]
        self._reqid += 100000
        return results

#########################################
# New Image classes
#########################################

class Image(BaseModel):
    """
    A single image object returned from Gemini.
    Parameters:
        url: str
            URL of the image.
        title: str, optional
            Title of the image (default: "[Image]").
        alt: str, optional
            Optional description.
        proxy: str, optional
            Proxy used when saving the image.
    """
    url: str
    title: str = "[Image]"
    alt: str = ""
    proxy: Optional[str] = None

    def __str__(self):
        return f"{self.title}({self.url}) - {self.alt}"

    def __repr__(self):
        short_url = self.url if len(self.url) <= 20 else self.url[:8] + "..." + self.url[-12:]
        return f"Image(title='{self.title}', url='{short_url}', alt='{self.alt}')"

    async def save(
        self,
        path: str = "temp",
        filename: Optional[str] = None,
        cookies: Optional[dict] = None,
        verbose: bool = False,
        skip_invalid_filename: bool = False,
    ) -> Optional[str]:
        """
        Save the image to disk.
        Parameters:
            path: str, optional
                Directory to save the image (default "./temp").
            filename: str, optional
                Filename to use; if not provided, inferred from URL.
            cookies: dict, optional
                Cookies used for the image request.
            verbose: bool, optional
                If True, outputs status messages (default False).
            skip_invalid_filename: bool, optional
                If True, skips saving if the filename is invalid.
        Returns:
            Absolute path of the saved image if successful; None if skipped.
        Raises:
            httpx.HTTPError if the network request fails.
        """
        filename = filename or self.url.split("/")[-1].split("?")[0]
        try:
            filename = re.search(r"^(.*\.\w+)", filename).group()
        except AttributeError:
            if verbose:
                console.log(f"Invalid filename: {filename}")
            if skip_invalid_filename:
                return None
        async with AsyncClient(http2=True, follow_redirects=True, cookies=cookies, proxies=self.proxy) as client:
            response = await client.get(self.url)
            if response.status_code == 200:
                content_type = response.headers.get("content-type")
                if content_type and "image" not in content_type:
                    console.log(f"Warning: Content type of {filename} is {content_type}, not an image.")
                dest_path = Path(path)
                dest_path.mkdir(parents=True, exist_ok=True)
                dest = dest_path / filename
                dest.write_bytes(response.content)
                if verbose:
                    console.log(f"Image saved as {dest.resolve()}")
                return str(dest.resolve())
            else:
                raise HTTPStatusError(
                    f"Error downloading image: {response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response,
                )

class WebImage(Image):
    """
    Image retrieved from web.
    Returned when asking Gemini to "SEND an image of [something]".
    """
    pass

class GeneratedImage(Image):
    """
    Image generated by ImageFX (Google's AI image generator).
    Parameters:
        cookies: dict[str, str]
            Cookies used from the GeminiClient.
    """
    cookies: Dict[str, str]

    @validator("cookies")
    def validate_cookies(cls, v):
        if not v:
            raise ValueError("GeneratedImage requires cookies from GeminiClient.")
        return v

    async def save(self, **kwargs) -> Optional[str]:
        """
        Save the generated image to disk.
        Parameters:
            filename: str, optional
                Filename to use; generated images are in .png format.
            Additional arguments are passed to Image.save.
        Returns:
            Absolute path of the saved image if successful.
        """
        filename = kwargs.pop("filename", None) or f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.url[-10:]}.png"
        return await super().save(filename=filename, cookies=self.cookies, **kwargs)

#########################################
# Main usage demonstration
#########################################

if __name__ == "__main__":
    """
    Usage demonstration:
    - Reads cookies from 'cookies.json'
    - Initializes the synchronous Chatbot wrapper.
    - Performs a text query.
    - Performs an image generation query and downloads the generated image.
    - Demonstrates saving a conversation.
    """
    # Define the path to cookies file
    cookies_file = r"C:\Users\hp\Desktop\Webscout\cookies.json"
    
    # Create Chatbot instance with a chosen model
    try:
        bot = Chatbot(cookie_path=cookies_file, model=Model.G_2_0_FLASH_THINKING_WITH_APPS)
    except Exception as e:
        console.log(f"[red]Error initializing Chatbot: {e}[/red]")
        exit(1)

    # Sample text query
    text_message = "How many r's in word strawberry?"
    console.log("[green]Sending text query to Gemini...[/green]")
    try:
        response_text = bot.ask(text_message)
        console.log("[blue]Text Response:[/blue]")
        console.print(Markdown(response_text.get("content", "No content received.")))
    except Exception as e:
        console.log(f"[red]Error sending text query: {e}[/red]")

    # Image generation query
    image_message = "Generate an image of a scenic view."
    console.log("[green]Requesting image generation from Gemini...[/green]")
    try:
        response_image = bot.ask(image_message)
        # Check if any image URL is returned in the response
        image_urls = response_image.get("images", [])
        if not image_urls:
            console.log("[red]No image URLs returned in response.[/red]")
        else:
            image_url = image_urls[0]
            console.log(f"[blue]Image URL received: {image_url}[/blue]")
            # Use GeneratedImage class to download the generated image
            generated_img = GeneratedImage(
                url=image_url,
                cookies={"__Secure-1PSID": bot.secure_1psid, "__Secure-1PSIDTS": bot.secure_1psidts}
            )
            saved_path = asyncio.run(generated_img.save(path="downloaded_images", verbose=True))
            console.log(f"[blue]Generated image saved at: {saved_path}[/blue]")
    except Exception as e:
        console.log(f"[red]Error processing image generation: {e}[/red]")
    
    # Demonstrate saving a conversation
    conversation_file = "conversations.json"
    conversation_name = "Sample Conversation"
    try:
        bot.save_conversation(conversation_file, conversation_name)
        console.log(f"[green]Conversation saved to {conversation_file} under the name '{conversation_name}'.[/green]")
    except Exception as e:
        console.log(f"[red]Error saving conversation: {e}[/red]")
