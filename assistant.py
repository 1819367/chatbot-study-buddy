import time
import random
from openai import OpenAI
import logging
import datetime
import re #python module for regular expressions, added to remove annotations made by the assistant

log = logging.getLogger("assistant")

logging.basicConfig(filename = "assistant.log", level = logging.INFO)

client = OpenAI()

def process_run(thread_id, assistant_id):
    new_run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id
    )

    phrases = ["Thinking", "Pondering", "Dotting the i's", "Achieving world peace"]

    while True:
        time.sleep(1)
        print(random.choice(phrases) + "...")
        run_check = client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = new_run.id
        )
        if run_check.status in ["cancelled", "failed", "completed", "expired"]:
            return run_check

def log_run(run_status):
    if run_status in ["cancelled", "failed", "expired"]:
        log.error(str(datetime.datetime.now()) + " Run " + run_status + "\n")

def get_message(run_status):
    if run_status == "completed":
        thread_messages = client.beta.threads.messages.list(
            thread_id = thread.id
        )
        message = thread_messages.data[0].content[0].text.value
        
        # check the message thread for annotations, and remove any
        if thread_messages.data[0].content[0].text.annotations:
            # regular expression pattern being searched for
            pattern = r'【\d+†source】'
            # search the message content for this expression
            message = re.sub(pattern, '', message)


    if run_status in ["cancelled", "failed", "expired"]:
        message = "An error has occurred, please try again."
    
    return message

# function to check if category value is greater than threshold
def check_category_scores(categories, threshold):
    for key, value in categories:
        if value > threshold:
            return True
        else:
            return False  

assistant = client.beta.assistants.update(
    assistant_id="asst_XdYTmnWKrnciClxxeCx9nGFI",
    tool_resources={"file_search": {"vector_store_ids": ["vs_eEtThd1XVzhYoVEFPdkh0HpG"]}}
)

thread = client.beta.threads.create()

user_input = ""

while True:
    if (user_input == ""):
        print("Assistant: Hello there! Just so you know, you can type exit to end our chat. What's your name? ")
        name = input("You: ")
        print("Assistant: Hey, " + name + "! How can I help you?")
        user_input = input("You: ")
    else:
        user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        exit()

    # moderate the user's input before the assistant creates a message
    moderation_result = client.moderations.create(
        input = user_input
    )
   
#   initiate a loop as long as the category scores exceed a threshold of .7 or the content is flagged
    while check_category_scores(moderation_result.results[0].category_scores, 0.7) or moderation_result.results[0].flagged == True:
        print("Assistant: Sorry, your message violated our community guidelines. Please try a different prompt.")
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            exit()
        moderation_result = client.moderations.create(
            input = user_input
        )

    # for checking single category, removed 
    # set the threshold for single category
    # self_harm_threshold = .01

    # while loop to check if a single category score is more than the threshold set or is flagged
    # while moderation_result.results[0].category_scores.self_harm > self_harm_threshold or moderation_result.results[0].flagged == True:
    #     print("Assistant: Sorry, your message violated our community guidelines.  Please try a different prompt.")
    #     # moderate a new prompt
    #     user_input = input("You: ")
    #     # added code to exit in the loop
    #     if user_input.lower() == "exit":
    #         print("Goodbye!")
    #         exit()
    #     moderation_result = client.moderations.create(
    #         input = user_input
    #     )

    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = "user",
        content = user_input
    )

    run = process_run(thread.id, assistant.id)

    log_run(run.status)

    message = get_message(run.status)

    print("\nAssistant: " + message + "\n")