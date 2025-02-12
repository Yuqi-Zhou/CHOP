import os
import re
import time
import subprocess
from PIL import Image
import shlex

def get_size(adb_path):
    command = rf"{adb_path} shell wm size"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    print(result)
    resolution_line = result.stdout.strip().split('\n')[-1]
    width, height = map(int, resolution_line.split(' ')[-1].split('x'))
    return width, height


def homeslide(adb_path, action, x, y):
    if "down" in action:
        command = adb_path + f" shell input swipe {int(x/2)} {int(y/2)} {int(x/2)} {int(y/4)} 500"
    elif "up" in action:
        command = adb_path + f" shell input swipe {int(x/2)} {int(y/2)} {int(x/2)} {int(3*y/4)} 500"
    elif "left" in action:
        command = adb_path + f" shell input swipe {int(x/4)} {int(y/2)} {int(3*x/4)} {int(y/2)} 500"
    elif "right" in action:
        command = adb_path + f" shell input swipe {int(3*x/4)} {int(y/2)} {int(x/4)} {int(y/2)} 500"
    else:
        return
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)

def get_screenshot(adb_path):
    command = adb_path + " shell rm /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.5)
    command = adb_path + " shell screencap -p /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.5)
    command = adb_path + " pull /sdcard/screenshot.png ./screenshot"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    image_path = "./screenshot/screenshot.png"
    save_path = "./screenshot/screenshot.jpg"
    image = Image.open(image_path)
    original_width, original_height = image.size
    new_width = int(original_width * 0.5)
    new_height = int(original_height * 0.5)
    resized_image = image.resize((new_width, new_height))
    resized_image.convert("RGB").save(save_path, "JPEG")
    time.sleep(0.1)


def get_screenshot_savedir(adb_path, save_folder, step):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    command = adb_path + " shell rm /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)

    command = adb_path + " shell screencap -p /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)

    local_image_path = os.path.join(save_folder, f"screenshot{step}.png")
    command = adb_path + f" pull /sdcard/screenshot.png {local_image_path}"
    print(command)
    subprocess.run(command, capture_output=True, text=True, shell=True)

    image = Image.open(local_image_path)
    original_width, original_height = image.size

    new_width = int(original_width * 0.5)
    new_height = int(original_height * 0.5)
    resized_image = image.resize((new_width, new_height))

    local_ori_image_path = save_path = os.path.join(save_folder, f"screenshot{step}.jpg")  # 保存为JPEG的路径
    resized_image.convert("RGB").save(save_path, "JPEG")
    time.sleep(0.1)

    return local_ori_image_path, local_image_path


def tap(adb_path, x, y, px, py):
    w = px
    h = py
    ax = int(x/980*w)
    ay = int(y/980*h)
    print(f"tap: {x/980} {y/980}")
    command = adb_path + f" shell input tap {ax} {ay}"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)

def contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fa5]', text))

def type(adb_path, text):
    text = text.replace("\\n", "_").replace("\n", "_")

    if "ruc.edu.cn" in text:
        text1 = text.split('@')[0]
        text2 = text.split('@')[1]
        for char in text1:
            subprocess.run(["adb", "shell", "input", "text", char])
            time.sleep(0.1)
            subprocess.run(["adb", "shell", "input", "keyevent", "66"])
            time.sleep(0.1)
        subprocess.run(["adb", "shell", "input", "text", '@'+text2])
        subprocess.run(["adb", "shell", "input", "keyevent", "66"])

    else:
        if contains_chinese(text):
            for char in text:
                if char == ' ':
                    command = adb_path + f" shell input text %s"
                elif char == '_':
                    command = adb_path + f" shell input keyevent 66"

                elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char.isdigit():
                    command = adb_path + f" shell input text {char}"

                elif char in '-.,!?@\'°/:;()':
                    command = adb_path + f" shell input text \"{char}\"".replace('\'', "\\'")
                else:
                    command = adb_path + f" shell am broadcast -a ADB_INPUT_TEXT --es msg \"{char}\""
                result = subprocess.run(command, capture_output=True, text=True, shell=True)
                print(result)
                time.sleep(0.1)
        else:
            char = "\\'"
            text = text.replace("'", char)
            texts = text.split(char)
            for text in texts[:-1]:
                command = adb_path + f" shell input text {shlex.quote(text)}"
                print(command)
                subprocess.run(command, capture_output=True, text=True, shell=True)
                command = adb_path + f" shell input text \"{char}\""
                subprocess.run(command, capture_output=True, text=True, shell=True)
            command = adb_path + f" shell input text {shlex.quote(texts[-1])}"
            subprocess.run(command, capture_output=True, text=True, shell=True)


def slide(adb_path, action, x, y):
    if "down" in action:
        command = adb_path + f" shell input swipe {int(x/2)} {int(y/2)} {int(x/2)} {int(y/4)} 500"
    elif "up" in action:
        command = adb_path + f" shell input swipe {int(x/2)} {int(y/2)} {int(x/2)} {int(3*y/4)} 500"
    elif "left" in action:
        command = adb_path + f" shell input swipe {int(x/4)} {int(y/2)} {int(3*x/4)} {int(y/2)} 500"
    elif "right" in action:
        command = adb_path + f" shell input swipe {int(3*x/4)} {int(y/2)} {int(x/4)} {int(y/2)} 500"
    else:
        return
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)

def back(adb_path):
    command = adb_path + f" shell input keyevent 4"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)
    
    
def back_to_desktop(adb_path):
    command = adb_path + f" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.1)


def app_exit(adb_path):
    command_get_package = adb_path + " shell dumpsys window | findstr mCurrentFocus"
    result = subprocess.run(command_get_package, capture_output=True, text=True, shell=True)
    match = re.search(r"([a-zA-Z0-9\.]+?)/[a-zA-Z0-9\.]+", result.stdout)
    if match:
        package_name = match.group(1)

        command_force_stop = adb_path + f" shell am force-stop {package_name}"
        subprocess.run(command_force_stop, capture_output=True, text=True, shell=True)
        time.sleep(0.1)
