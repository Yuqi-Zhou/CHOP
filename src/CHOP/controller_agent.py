import re
import os
import time
import shutil
import requests
from PIL import Image
from CHOP.prompt import get_opreation_sop_prompt_with_image, get_custome_opreation, get_memroy_prompt
from CHOP.controller import get_size, tap, type, slide, back, app_exit, get_screenshot_savedir, homeslide
from CHOP.chat import init_action_chat, init_memory_chat, add_response
from CHOP.api import inference_chat

class ActionController:
    def __init__(self, args):
        self.args = args
        self.api = args.api
        self.adb_path = args.adb_path
        self.grounding_api = "http://127.0.0.1:8001/generate_click_location/"
        self.temp_dir = f"screenshot/{self.args.test_data}/temp"
        self.x, self.y = get_size(args.adb_path)

    def click(self, action, image_path, x, y):
        error_flag = 0
        files = {
            'file': open(image_path, 'rb')}
        data={"data": action}
        response = requests.post(self.grounding_api, files=files, data=data)
        result = response.json()
        tap_coordinate = result.get("click_coordinates", None)
        tap(self.adb_path, tap_coordinate[0], tap_coordinate[1], x, y)
        return error_flag

    def typeText(self, action):
        error_flag = 0
        text = re.search(r"\((.*?)\)", action).group(1)
        type(self.adb_path, text)
        return error_flag


    def page(self, action, x, y):
        error_flag = 0
        slide(self.adb_path, action, x, y)
        return error_flag
    
    def back(self):
        error_flag = 0
        back(self.adb_path)
        return error_flag

    def exit(self):
        error_flag = 0
        x, y = get_size(self.adb_path)
        app_exit(self.adb_path)
        app_exit(self.adb_path)
        time.sleep(2)
        homeslide(self.adb_path, "right", x, y)
        return error_flag
    
    def makedirs(self):
        if not os.path.exists("screenshot"):
            os.mkdir("screenshot")
        if not os.path.exists("temp"):
            os.mkdir("temp")
        else:
            shutil.rmtree("temp")
            os.mkdir("temp")

    def action_split(self, plan, documentation, boundary_condition, plan_iter):
        iter = f"plan{plan_iter}_action0"
        save_dir = f"screenshot/{self.args.test_data}/{self.args.app_name}_{self.args.ins_cnt}"
        image, _ = get_screenshot_savedir(self.adb_path, save_dir, iter)

        operation_history = init_action_chat()
        opreation_prompt = get_opreation_sop_prompt_with_image(plan, documentation, boundary_condition)
        operation_history = add_response("user", opreation_prompt, operation_history, image)
        while True:
            response = inference_chat(operation_history, self.api)
            try:
                action_text = response.split("Actions:")[1].strip()
                actions = [action.split('.', 1)[1].strip() for action in action_text.split('\n') if action.strip()]
            except:
                print("Response not formatted, retry.")
            else:
                break
        return actions

    def get_image_size(self, image):
        iw, ih = Image.open(image).size
        if iw > ih:
            x, y = self.y, self.x
            iw, ih = ih, iw
        else:
            x, y = self.x, self.y
        return iw, ih, x, y

    def do_action(self, action, plan_iter, action_iter):
        iter = f"plan{plan_iter}_action{action_iter}"
        save_dir = f"screenshot/{self.args.test_data}/{self.args.app_name}_{self.args.ins_cnt}"
        image, _ = get_screenshot_savedir(self.adb_path, save_dir, iter)
        iw, ih, x, y = self.get_image_size(image)

        print(action)
        if "stop" in action:
            self.exit()
        elif "click" in action:
            self.click(action, image, x, y)
        elif "page" in action:
            self.page(action, x, y)
        elif "type" in action:
            self.typeText(action)
        elif "back" in action:
            self.back()
        elif "exit" in action:
            self.exit()

    def open_app(self, action):
        iter = f"plan0_action0"
        save_dir = f"screenshot/{self.args.test_data}/{self.args.app_name}_{self.args.ins_cnt}"
        image, _ = get_screenshot_savedir(self.adb_path, save_dir, iter)
        iw, ih, x, y = self.get_image_size(image)
        self.click(action, image, x, y)

    def do_actions(self, actions, plan_iter):
        for action_iter, action in enumerate(actions):
            self.do_action(action, plan_iter, action_iter)

    def do_custome(self, plan, plan_iter, documentation, boundary_condition, memories):
        action_iter = -1
        summs = []
        next_suggestion = ''
        actions = []
        while True:
            if action_iter >= 10:
                exit()
            action_iter += 1
            iter = f"plan{plan_iter}_action{action_iter}"
            save_dir = f"screenshot/{self.args.test_data}/{self.args.app_name}_{self.args.ins_cnt}"
            image, _ = get_screenshot_savedir(self.adb_path, save_dir, iter)
            _, _, x, y = self.get_image_size(image)

            operation_history = init_action_chat()
            opreation_prompt = get_custome_opreation(plan, memories, documentation, boundary_condition, summs, next_suggestion)
            operation_history = add_response("user", opreation_prompt, operation_history, image)

            while True:
                response = inference_chat(operation_history, self.api)
                try:
                    action = re.search(r"Action:(.*)\n", response).group(1).strip()
                    summarization = re.search(r"Summarization:(.*)", response, re.DOTALL).group(1).strip()
                    finish = re.search(r"Finish:(.*)", response, re.DOTALL).group(1).strip()
                except:
                    print("Response not formatted, retry.")
                else:
                    break
            summs.append(summarization)
            actions.append(action)

            if "stop" in action:
                self.exit()
            elif "click" in action:
                self.click(action, image, x, y)
            elif "page" in action:
                self.page(action, x, y)
            elif "type" in action:
                self.typeText(action)
            elif "back" in action:
                self.back()
            elif "exit" in action:
                self.exit()

            if "Yes" in finish:
                memory_history = init_memory_chat()
                memroy_prompt = get_memroy_prompt(plan, summs)
                operation_history = add_response("user", memroy_prompt, memory_history)
                memory = inference_chat(operation_history, self.api)
                return memory
            time.sleep(2)