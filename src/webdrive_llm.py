import json
from utils import promptGPT
import re
from webdrive import screenshot_of_zerion_page
from embeddings import get_similar_embeddings
#import promptTemplates
from langchain.prompts import PromptTemplate

# def promptGPT(systemprompt, userprompt, model=constants.model):
#     print("""Inputting {} tokens into {}.""".format(num_tokens_from_messages(systemprompt+userprompt), model))
#     response = openai.ChatCompletion.create(
#       model=model,
#       temperature=0,
#       messages=[
#         {"role": "system", "content": systemprompt},
#         {"role": "user", "content": userprompt}])
#     return response["choices"][0]["message"]["content"]


system_prompt_template = """As an AI, you have the capability to pull different types of blockchain information. A user will provide you with an address or ENS (Ethereum Name Service) and specify whether they want to see tokens, NFTs, or transaction history associated with that address or ENS. Based on this input, you will output a command in a structured JSON format to get a screenshot of the required information.

    Example ENS name: vitalik.eth
    Example address (ethereum): 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B
    
    For example, if a user says "Could you display the NFTs associated with the account elonmusk.eth?", your output would be:
    { 
        "command": "screenshot",
        "address_or_ens": "elonmusk.eth",
        "twitter_handle": "N/A",
        "type_of_screenshot": "nfts"
    }
    User: "Can you provide the transaction history for {ENS} {ADDRESS}?"
    AI Output:
    { 
        "command": "screenshot",
        "address_or_ens": "mywallet.eth",
        "twitter_handle": "N/A",
        "type_of_screenshot": "transactions"
    }
    Other relevant examples: 
    {EXAMPLES_STRING}
    """
system_prompt_test = """Other relevant examples: 
    {EXAMPLES_STRING}
    """

def web_drive_LLM(user_input):
    # don't intend to use langchain
    # template = system_prompt_template
    # system_prompt = PromptTemplate(
    #     input_variables=["EXAMPLES_STRING"],
    #     template=template,
    #     validate_template=False
    # )

    #https://python.langchain.com/en/latest/modules/prompts/prompt_templates/examples/partial.html
    # system_prompt = system_prompt.partial(EXAMPLES_STRING="test")
    # system_prompt.format(ENS="baz", ADDRESS="bar")
    # system_prompt_test.format(EXAMPLES_STRING="test")

    examples = get_similar_embeddings(user_input)
    print('num of examples: ', len(examples))
    #concatenate the examples
    EXAMPLES_STRING = ""
    for example in examples:
        EXAMPLES_STRING += example

    # system_prompt.replace("{ADDRESS}", "")

    #OPTION TO ADD ENS OR ADDRESS TO TEMPLATE & EXAMPLES HERE
    #remove the non-present variables
    #remove the non-present variables

    if ".eth" in user_input:
        global system_prompt
        system_prompt = system_prompt_template.replace("{ADDRESS}", "")
    else:
        system_prompt =system_prompt_template.replace("{ENS}", "")


    system_prompt = system_prompt.replace("{EXAMPLES_STRING}", EXAMPLES_STRING)
    #format the prompt
    # system_prompt = PromptTemplate(system_prompt, EXAMPLES_STRING)
    # template = system_prompt
    #format prompt 

    llm_result = promptGPT(system_prompt, user_input)
    print('llm_result: ', llm_result)

    #parse the json in the response
    # res = json.loads(res)
    # Extract the JSON command
    command_match = re.search(r'{(.+?)}', llm_result, re.DOTALL)
    command_json_str = command_match.group(0)

    # Extract the comment
    comment = llm_result.replace(command_json_str, '').strip()

    # Parse the command JSON
    command_json = json.loads(command_json_str)
    command = command_json["command"] 
    #get the address or ens
    address_or_ens = command_json["address_or_ens"]
    #get the type of screenshot
    type_of_screenshot =  command_json["type_of_screenshot"]
    #get the twitter handle
    twitter_handle =  command_json["twitter_handle"]

    if (command == 'screenshot'):
        filename, webpage_url = screenshot_of_zerion_page(address_or_ens, type_of_screenshot)
        print('returning image at path:', filename)
        return [filename, webpage_url]

# web_drive_LLM("Can you provide the transaction history for ENS vitalik.eth?")