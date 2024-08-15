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

# assistants = client.beta.assistants.list()
# print(assistants)
# exit()

# removed after uploading files 
# assistant = client.beta.assistants.create(
#     name="Study Helper",
#     model="gpt-3.5-turbo",
#     instructions="You are a study partner for students who are new to technology.  When you answer prompts, do so with simple language suitable for someone learning fundamental concepts.",
#     tools=[{"type": "file_search"}],
# )

# removed after creating and uploading files
# create a vector store called "curriculum"
# vector_store = client.beta.vector_stores.create(name="curriculum")

# removed after completing
# Ready the files for upload to OpenAI
# file_paths = ["knowledge/CurriculumLessons4-7.pdf", "knowledge/OpenAIChatCompletionsAPICheatsheet.pdf"]
# file_streams = [open(path, "rb") for path in file_paths]

# removed after uploading
# use the upload and poll sdk helpr to upload the files, add them to the vector store, 
# and poll the status of the file batch for completion
# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#   vector_store_id=vector_store.id, files=file_streams
# )

# removed after chekcing the status
# print the status and the file counts of the batch to see the results of this operation
# print(file_batch.status)
# print(file_batch.file_counts)
# exit()

assistant = client.beta.assistants.update(
    assistant_id="asst_XdYTmnWKrnciClxxeCx9nGFI",
    tool_resources={"file_search": {"vector_store_ids": ["vs_eEtThd1XVzhYoVEFPdkh0HpG"]}}
)

# print(assistant)
# exit()

thread = client.beta.threads.create()

user_input = ""

while True:
    if (user_input == ""):
        # greet user with a print(), asking for their name and teling them how to end the session.
        print("Assistant: Hello there! Just so you know, you can type exit to end our chat. What's your name? ")
        # prompt user for their name and assign it to a variable called name.
        name = input("You: ")
        # greet the user with another print(), referencing their name.
        print("Assistant: Hey, " + name + "! How can I help you?")
        # prompt the user for their question and assign that to user_input. this is the first request the assistant processes
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
   
    # moderation threshold
    # hate_threshold = 0.01
    self_harm_threshold = .01

    # Create/Use a while loop to check if the category score is more than the threshold set or is flagged
    while moderation_result.results[0].category_scores.self_harm > self_harm_threshold or moderation_result.results[0].flagged == True:
        print("Assistant: Sorry, your message violated our community guidelines.  Please try a different prompt.")
        # moderate a new prompt
        user_input = input("You: ")
        # added code to exit in the loop
        if user_input.lower() == "exit":
            print("Goodbye!")
            exit()
        moderation_result = client.moderations.create(
            input = user_input
        )

    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = "user",
        content = user_input
    )

    run = process_run(thread.id, assistant.id)

    log_run(run.status)

    message = get_message(run.status)

    print("\nAssistant: " + message + "\n")