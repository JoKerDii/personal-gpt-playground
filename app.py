import gradio as gr
from loguru import logger
from MyGPT import MyGPT
from config import MODELS, DEFAULT_MODEL, MODEL_TO_MAX_TOKENS

mygpt = MyGPT()

def fn_prehandle_user_input(user_input, chat_history):
    # check input
    if not user_input:
        gr.Warning("Please enter your question")
        logger.warning("Please enter your question")
        return chat_history

    # show user's message in front end chat window
    chat_history.append([user_input, None])

    logger.info(f"\nUser Input: {user_input}, \n"
                f"History: {chat_history}")
    return chat_history


def fn_predict(
        user_input,
        chat_history,
        model,
        max_tokens,
        temperature,
        stream):

    # if user's input is null, return current chat history
    if not user_input:
        return chat_history

    # print out log, record input parameters
    logger.info(f"\nUser Input: {user_input}, \n"
                f"History: {chat_history}, \n"
                f"Model: {model}, \n"
                f"Max # of Tokens: {max_tokens}\n"
                f"Temperature: {temperature}\n"
                f"Stream Output: {stream}")

    # config messages parameters
    messages = user_input  # or [{"role": "user", "content": user_input}]
    if len(chat_history) > 1:
        messages = []
        for chat in chat_history:
            if chat[0] is not None:
                messages.append({"role": "user", "content": chat[0]})
            if chat[1] is not None:
                messages.append({"role": "assistant", "content": chat[1]})
    print(messages)

    # generate response
    bot_response = mygpt.get_response(
        messages, model, max_tokens, temperature, stream)

    if stream:
        # stream output
        chat_history[-1][1] = ""
        for character in bot_response:
            character_content = character.choices[0].delta.content
            if character_content is not None:
                chat_history[-1][1] += character_content
                yield chat_history
    else:
        # non stream output
        chat_history[-1][1] = bot_response
        logger.info(f"History: {chat_history}")
        yield chat_history


def fn_update_max_tokens(model, origin_set_tokens):
    """
    Update max number of tokens

    Args:
        model: model ID
        origin_set_tokens: original number of tokens in the slider

    Returns:
        the slider with the updated max number of tokens
    """
    # get model's max number of tokens or original number of tokens
    new_max_tokens = MODEL_TO_MAX_TOKENS.get(model)
    new_max_tokens = new_max_tokens if new_max_tokens else origin_set_tokens

    # if original number exceeds the updated max, reset it to default 1000
    new_set_tokens = origin_set_tokens if origin_set_tokens <= new_max_tokens else 1000

    # create slider with updated max token
    new_max_tokens_component = gr.Slider(
        minimum=0,
        maximum=new_max_tokens,
        value=new_set_tokens,
        step=1.0,
        label="max_tokens",
        interactive=True,
    )

    return new_max_tokens_component


with gr.Blocks() as demo:
    # title
    gr.Markdown("# <center> Personal GPT Playground </center>")
    with gr.Row(equal_height=True):
        # chat on the left
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="ChatBot")
            user_input_textbox = gr.Textbox(label="Input", value="Hello")
            with gr.Row():
                submit_btn = gr.Button("Submit")
                clear_btn = gr.Button("Clear", elem_id="btn")
        # tools on the right
        with gr.Column(scale=1):
            # create an option board for tuning parameters
            with gr.Tab(label="Parameter"):
                # choose a model
                model_dropdown = gr.Dropdown(
                    label="model",
                    choices=MODELS,
                    value=DEFAULT_MODEL,
                    multiselect=False,
                    interactive=True,
                )
                max_tokens_slider = gr.Slider(
                    minimum=0,
                    maximum=4096,
                    value=1000,
                    step=1.0,
                    label="max_tokens",
                    interactive=True
                )
                temperature_slider = gr.Slider(
                    minimum=0,
                    maximum=2,
                    value=0.7,
                    step=0.01,
                    label="temperature",
                    interactive=True
                )
                stream_radio = gr.Radio(
                    choices=[
                        True,
                        False],
                    label="stream",
                    value=True,
                    interactive=True
                )

        # ensure max_tokens_slider changes with the change of model type
        # https://www.gradio.app/docs/dropdown
        model_dropdown.change(
            fn=fn_update_max_tokens,
            inputs=[model_dropdown, max_tokens_slider],
            outputs=max_tokens_slider
        )

        # after clicking on the button for submission, check input first then execute the response
        # https://www.gradio.app/docs/textbox
        user_input_textbox.submit(
            fn=fn_prehandle_user_input,
            inputs=[
                user_input_textbox,
                chatbot],
            outputs=[chatbot]
        ).then(
            fn=fn_predict,
            inputs=[
                user_input_textbox,
                chatbot,
                model_dropdown,
                max_tokens_slider,
                temperature_slider,
                stream_radio],
            outputs=[chatbot]
        )

        # after clicking on the button
        # https://www.gradio.app/docs/button
        submit_btn.click(
            fn=fn_prehandle_user_input,
            inputs=[
                user_input_textbox,
                chatbot],
            outputs=[chatbot]
        ).then(
            fn=fn_predict,
            inputs=[
                user_input_textbox,
                chatbot,
                model_dropdown,
                max_tokens_slider,
                temperature_slider,
                stream_radio],
            outputs=[chatbot]
        )

        clear_btn.click(lambda: None, None, chatbot, queue=False)


demo.queue().launch() # share=True # server_name="0.0.0.0"
