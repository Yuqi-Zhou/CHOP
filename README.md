<div align="center">
  <h1 style="display: inline-block; font-size: 32px;">CHOP: Mobile Operating Assistant with Constrained High-frequency Optimized Subtask Planning </\br></h1>
</div>


This repository introduces CHOP, a framework designed to optimize subtasks in mobile app automation. While current visual language models (VLMs) operate at the task, subtask, and action levels, subtasks often suffer from ineffectiveness or inefficiency. CHOP addresses this by introducing basis subtasks, which are common, human-executed sequences that ensure both effectiveness and efficiency. Evaluated across 60 tasks in 20 apps, our method significantly improves task completion, outperforming existing frameworks in both English and Chinese contexts.


<div align="center">
    <img src=assets/workflow.jpg width=100% />
</div>



## Dataset

### CHOP-En & CHOP-ZH

The data in CHOP-En and CHOP-ZH includes 10 applications. In CHOP-En, each application contains 3 instructions, while CHOP-ZH contains 10 instructions per application. You can find all the instructions used for testing in the papers in the `src/dataset` folder. The complete CHOP-ZH dataset will be released later due to company regulations.

### Basis Subtask

We collect 10 commonly used subtasks from AITZ and define them as **basis subtasks** as shown in the table below. The documentation for each basis subtask can be found in the files `src/dataset/documentation.json` and `src/dataset/boundary_conditions.json`.
 
 | Basis Subtask                                  | Explanation                                                                                                                                                                                                                                                |
|------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Search Item (parameter)                        | Click on the search bar, type in the item name, and press   enter. The parameter is the name of the item you want to search for. This   action can be performed on any website with a search functionality. Output   format is 'Search Item (XXX)'.        |
| Send Text Message (parameter)                  | This action involves typing a specific message into a   designated text input area. The parameter is the content of the message to be   sent. Output format is 'Send Text Message (XXX)'.                                                                  |
| Open Section (parameter)                       | Find and enter the specified section or feature in the   application. The parameter is the name of the section, such as 'Hot List',   'Messages', 'Settings', etc.                                                                                         |
| View Content (parameter)                       | View the specified content in the application. The parameter   describes the content to be viewed, such as 'Latest News', 'Posts', etc.                                                                                                                    |
| Interact (parameter1,   parameter2)            | Interact with the content in the application, such as 'Like'   or 'Comment'. The parameter1 is the content to be interact with, such as   'Video' or 'Song'. The parameter2 is the action of interaction, such as 'Like   content', 'Post a comment', etc. |
| Manage Collections   (parameter1, paramter2)   | Manage personal collections or shopping carts, etc. The   parameter1 include actions such as 'Add to Favorites', 'Delete', and   parameter2 include items such as 'Product', 'Video', etc.                                                                 |
| Share Content (parameter1,   paramter2)        | Share content from the application to other platforms or   users. The parameter1 include the sharing platform and parameter2 include   recipient, such as 'WeChat's 'Lucky'.                                                                               |
| Check Notifications   (parameter)              | View notifications or messages in the application. The   parameter is the section of the app, such as 'System Notifications', 'Private   Messages', etc.                                                                                                   |
| Modify Settings (parameter1,   paramter2)      | Modify the settings in the application. The parameter1 include   the setting item and parameter2 include its changes, such as 'Theme Skin',   'Notification Method', etc.                                                                                  |
| Create or Edit Entry   (parameter1, paramter2) | Create or edit entries in the application. The parameters   include the entry type and name, such as 'Playlist', 'Contact', etc.                                                                                                                           |

## CHOP demo usage

### 🔧Preparation

#### ADB Environment

❗At present, only **Android OS** and **Harmony OS** (version <= 4) support tool debugging.

1. Download the [Android Debug Bridge](https://developer.android.com/tools/releases/platform-tools?hl=en).
2. Turn on the ADB debugging switch on your Android phone, it needs to be turned on in the developer options first.
3. Connect your phone to the computer with a data cable and select "Transfer files".
4. Test your ADB environment as follow: ```/path/to/adb devices```. If the connected devices are displayed, the preparation is complete.
5. If you are using a MAC or Linux system, make sure to turn on adb permissions as follow: ```sudo chmod +x /path/to/adb```
6. If you are using Windows system, the path will be ```xx/xx/adb.exe``

#### UI grounding

You can go to https://huggingface.co/spaces/Aria-UI/Aria-UI to get the Aria-UI model.

### Run

Here we provide a demo code for anyone who wants to try the CHOP on GPT-4V.

Firstly, go to `src/CHOP/api.py` and add your own urls. Then, go to `src/run_Aria.py` to set your Aria-UI model path.

Secondly, run the folloiwng code in commad line to test CHOP framework:

```shell
cd src

python run_Aria.py

python run.py --app_name APP_FOR_TEST --ins_cnt DIFFICULTY --test_data CHOP-En/CHOP-ZH --adb_path YOUR_ADB_PATH --api YOUR_API_KEY
```
