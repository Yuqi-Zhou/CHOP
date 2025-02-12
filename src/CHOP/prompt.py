def split_planning_prompt(user_instruction):
    tips = '''
        Tips:
        1. The first action of the task should find App (parameter).
        2. When switching from one app to another, you need to exit the current app, that is, return to the homepage.
        3. Please do not use any markdown strings, such as ** or ###, in the output.
    '''

    actions_rule = '''
        Then, you need to generate a sequence of base instruction to compelete the user instruction. You can perform the following base instructions:
        1. Find App (parameter). Locate and open the specified app on your device. The parameter is the name of the app (e.g., "Notes," "Calendar"). Output format is 'Find App (XXX)'.
        2. Search Item (parameter). Click on the search bar, type in the item name, and press enter. The parameter is the name of the item you want to search for. This action can be performed on any website with a search functionality. Output format is 'Search Item (XXX)'.
        3. Send Text Message (parameter). This action involves typing a specific message into a designated text input area. The parameter is the content of the message to be sent. Output format is 'Send Text Message (XXX)'.
        4. Send Text Message (parameter). This action involves typing a specific message into a designated text input area. The parameter is the content of the message to be sent. Output format is 'Send Text Message (XXX)'.
        5. Back Home. When a command needs to be executed from one app to another, it needs to be executed first to return to the homepage. Output format is 'Back Home'.
        6. Open Section (parameter): `Find and enter the specified section or feature in the application. The parameter is the name of the section, such as 'Hot List', 'Messages', 'Settings', etc.
        7. Interact (parameter1, parameter2): `Interact with the content in the application, such as 'Like' or 'Comment'. The parameter1 is the content to be interact with, such as 'Video' or 'Song'. The parameter2 is the action of interaction, such as 'Like content', 'Post a comment', etc.
        8. Manage Collections (parameter1, paramter2): `Manage personal collections or shopping carts, etc. The parameter1 include actions such as 'Add to Favorites', 'Delete', and parameter2 include items such as 'Product', 'Video', etc.
        9. Share Content (parameter1, paramter2): Share content from the application to other platforms or users. The parameter1 include the sharing platform and parameter2 include recipient, such as 'WeChat's 'Lucky'.
        10. Check Notifications (parameter): View notifications or messages in the application. The parameter is the section of the app, such as 'System Notifications', 'Private Messages', etc.
        11. Modify Settings (parameter1, paramter2): `Modify the settings in the application. The parameter1 include the setting item and parameter2 include its changes, such as 'Theme Skin', 'Notification Method', etc.
        12. Create or Edit Entry (parameter1, paramter2): Create or edit entries in the application. The parameters include the entry type and name, such as 'Playlist', 'Contact', etc.

        If certain instruction cannot be represented by the base instructions mentioned above, please create new base instructions on your own. Additionally, you need to provide the instruction's name, the parameters it contains, a description of each parameter, the steps to complete this new instruction and the conditions for completing this instruction. Follow the format of the four base instructions mentioned above. Then use these new base instructions in your output. The command name and the subsequent description are separated by "###".
    '''

    thought_rules = '''
    Next, you need to think about something.
    Thought: Next, you need to consider which base instructions this task can consist of. Furthermore, how to create a new base instruction if the instruction is missing. Finally, you need to consider whether these created instructions can fully complete the task with the basic instructions. Lastly, please make sure to consider whether the generated task list is complete.
    '''

    planning_prompt = f'''You are a helpful phone operating assistant. You need to break down user instructions into specific task steps. The decomposed tasks will be provided to another assistant for execution. Here is the user instruction: '{user_instruction}'. Give me the response as requested below.

    '{actions_rule}'

    '{thought_rules}'

    '{tips}'

    Finally, your output must follow the following format:
    Thinking: Generate as requested by Thought Rules.
    Instructions: If the base instruction requires parameters, use (parameter). The output format is 1. instruction1\n 2. instruction2 3. instruction3 ### The description of instruction3 4. instruction4 ... '''

    return planning_prompt

def get_opreation_sop_prompt_with_image(plan, tool_function, tool_judgement):

    introduction = f'''
        Please generate a sequence of actions to complete the upcoming tasks: '{plan}'. You need to refer to the document: {tool_function}. There are some boundary conditions that you can consider based on the screenshot: {tool_judgement}. This is the current screenshot. Give me the response as requested below.
    '''

    action_rule = '''
        Then, The action sequence you output can only contain the following five actions. Use the description of the elements in the screenshot provided by the user to perform the following actions:
        1. click (parameter). Parameter is the target you need to click on. Reference Observation for the description of click elements.
        2. page down, page up. These two commands don't need parameters, used for page turning.
        3. type (parameter). The parameter is what you want to type. Make sure you have clicked on the input box before typing.
        4. back. Back to the previous page.
        5. exit. Exit the app and go back to the homepage.
        '''

    thought_rule = '''
        First, you need to generate the Thought.
        Observation: You need to describe the current screenshot. Provide a detailed description of the task-related parts in screenshot. It is also necessary to describe the positions of different elements.
        Thought: Please consider how to generate action sequences for executing instructions based on document and boundary conditions, as well as how to replace parameters in action sequences. You also need to consider how to use the content of observations and instructions to generate action sequences and replace their parameters.
    '''

    tips = '''
        1. If the action requires parameters, use (parameter). The Actions output should be 1. Action1 \n 2. Action2 ...
        2. Please do not use any markdown strings, such as ** or ###, in the output.
    '''

    output_rules = '''
        Finally, your output must follow the following format:
        Observation: Generate as required by Observation
        Thought: Generate as required by Thought
        Actions: The output format should be 1. action1 \n 2. action2 \n ... 
        '''

    opreation_prompt = f'''
    {introduction}
    {action_rule}
    {thought_rule}
    {tips}
    {output_rules}
    '''
    return opreation_prompt

def get_memroy_prompt(plan, summs):
    summs = " ".join([f"{i+1}. {summary}" for i,summary in enumerate(summs)])
    prompt = f'''
        This is the user's instruction: {plan}. This is the specific execution results of each step: {summs}. The information that may be used in subsequent tasks should be reflected in the summary sentence.
    '''
    return prompt

def get_custome_opreation(plan, memories, tool_function, tool_judgement, actions, next_suggestion):

    introduction = f'''
        Please give me a suggestion about how to complete the upcoming task: '{plan}'. This is the execution information from the previous process, and your task will depend on the information within it: '{memories}'. Here are some additional suggestions that you need to refer to when executing: '{next_suggestion}'.  You can refer to the document: {tool_function}. There are some boundary conditions that you can consider based on the screenshot: {tool_judgement}. These are the actions you have taken before: {''.join(actions)}. You need to think about the next step based on the actions that have already been taken. This is the current screenshot. Give me the response as requested below.
    '''

    observation_thought_rules = '''
        First, you need to generate the Observation.
        Observation: Provide a detailed textual description of the key content in the screenshot, such as visible text in the saerch bar, buttons, or icons. Provide a detailed description of the components related to the task.
        Thought: You need to think about how to interact with the items on screen to further complete the task. Then, you need to consider whether the current instruction has been completed. If it has been completed, there is no need to generate the next action. In addition, you also need to consider the actions you have taken before as the basis for your next action, so as to make better decisions and avoid repetitive operations.
    '''
    
    summarization_rule = '''
        Summarization: Next, you also need to summarize the actions and provide the reason why this action was taken. The information that may be used in subsequent tasks should be reflected in the summary sentence. 
    '''

    tips = '''
        1. Please do not use any markdown strings, such as ** or ###, in the output.
        2. Please do not repeat the same action you have taken before.
    '''

    action_rule = '''
        Then, The action sequence you output can only contain the following five actions. Use the description of the elements in the screenshot provided by the user to perform the following actions:
        1. click (parameter). Parameter is the target you need to click on. The clicked object needs to be described in detail, such as the text it contains and its shape. 
        2. page down, page up. These two commands don't need parameters, used for page turning.
        3. type (parameter). The parameter is what you want to type. Make sure you have clicked on the input box before typing.
        4. back. Back to the previous page.
        5. exit. Exit the app and go back to the homepage.
        6. None. The action means doing nothing.
        '''

    output_rules = '''
        Finally, your output must follow the following format:
        Observation: Generate as required by Observation (based on the textual description provided).
        Thought: Generate as required by Thought (based on the textual description provided and Observation).
        Action: Generate as required by action rules. If the action requires parameters, use (parameter). Only one action can be output.
        Summarization: Generate as required by Summarization (based on the textual description).
        Finish: If you believe the task is finished or will be finished, output "Yes". Otherwise, output "No".
        '''

    opreation_prompt = f'''
    {introduction}
    {observation_thought_rules}
    {action_rule}
    {summarization_rule}
    {tips}
    {output_rules}
    '''
    return opreation_prompt
