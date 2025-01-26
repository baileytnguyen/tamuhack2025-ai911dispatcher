from openai import OpenAI

client = OpenAI(api_key='')

def findAssistant():
    #list assistants, if not pull most recent
    assistant = client.beta.assistants.create(
    name="911 Emergency Dispatch Assistant_A",
    instructions= mainDirectives,
    model="gpt-4o",
    #tools=[{"type": "file_search"}],
    )
    return assistant.id
def newthread():
    thread = client.beta.threads.create()
def newMessage(thread_id,input1,pastInput):
    #if no past input then make new message
    # if past input or more messages
    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content= input1
    )
    
    

banana = "My name is robert smith, my phone number is 713-888-0012, I am located on the intersection of texas and university, and their is a fire raging at the intersection"

mainDirectives = """You are a 911 emergency dispatcher.You need to make sure all necessary emergency information is recorded so the proper emergency response can be issued.
Given the text prompt, Evaluate:
1.What is the address?
2.What is the phone number?
3.What is your name?
4. What is going on?
5. Given the answer to 4., Evaluate the priority of the emergency call from 1-4 given the following scale:

Level 1: Emergency call that requires the most urgent response, such as a cardiac arrest or a shooting.
Level 2: Urgent call that requires a timely response, such as a serious injury or a fire.
Level 3: Non-urgent call that requires a routine response, such as a minor accident or a theft.
Level 4: Low-priority call that requires a delayed response, such as a noise complaint or a parking violation.



If any of these details are missing, ask questions to find them out alongside any other
relevent questions that first responders might ask, given the emergency situation.

Once all necessary details are evaluated, message a concise paragraph with the answers to questions 1-5 and all additional information that was gathered.
"""


assistant = client.beta.assistants.create(
name="911 Emergency Dispatch Assistant_A",
instructions= mainDirectives,
model="gpt-4o",
#tools=[{"type": "file_search"}],
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
thread_id=thread.id,
role="user",
content= banana
)

run = client.beta.threads.runs.create_and_poll(
thread_id=thread.id,
assistant_id=assistant.id,
)

if run.status == 'completed': 
    messages = client.beta.threads.messages.list( thread_id=thread.id)
    if messages.data:
        content = messages.data[0].content[0].text.value
        print(content)
    else:
        print("No messages received.")
else:
    print("wowie wow")
    #print(run.status)