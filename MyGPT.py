from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv, find_dotenv

# load env (.env file in the directory with OPENAI_API_KEY)
load_dotenv(find_dotenv())

class MyGPT:
    def __init__(self):
        self.client = OpenAI()

    def get_response(
            self,
            messages,
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.7,
            stream=False,
    ):
        """
        Get response for an input. (ChatGPT API：https://platform.openai.com/docs/api-reference/chat)

        Args:
            messages: a list messages in the conversation
            model: model ID
            max_tokens: max number of tokens by the end of the conversation
            temperature: temperature parameter ranging between 0 and 2
                Higher value = higher randomness and creativity. Lower value = higher centainty and restriction.
            stream: whether streaming output or not

        Returns:
            if stream, return streaming version of response
            else, return response content.
        """
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif not isinstance(messages, list):
            return "Invalid messages type. It should be a string or a list."

        completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            stream=stream,
            temperature=temperature,
        )

        if stream:
            # stream version of response
            return completion

        # non stream version of response
        logger.debug(completion.choices[0].message.content)
        logger.info(f"Total # of tokens: {completion.usage.total_tokens}")
        return completion.choices[0].message.content

if __name__ == "__main__":
    # test
    mygpt = MyGPT()

    # prompt
    prompt = 'Hello'
    response = mygpt.get_response(prompt, temperature=1)
    print(response)
    #
    # # messages
    # messages = [
    #     {'role': 'user', 'content': 'what is LLM?'},
    # ]
    # response = mygpt.get_completion(messages, temperature=1)
    # print(response)