import argparse
import json
import re
import time
from CHOP.prompt import split_planning_prompt
from CHOP.api import inference_chat
from CHOP.controller_agent import ActionController 
from CHOP.controller import get_size, app_exit
from CHOP.chat import init_split_instruction


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instruction", type=str, default="")
    parser.add_argument("--app_name", type=str)
    parser.add_argument("--ins_cnt", type=int)
    parser.add_argument("--adb_path", type=str)
    parser.add_argument("--api", type=str)
    parser.add_argument("--test_data", type=str)
    args = parser.parse_args()
    return args

def run(args):
    instruction = args.instruction
    action_controller = ActionController(args)
    split_prompt = split_planning_prompt(instruction)
    split_instruction = init_split_instruction(split_prompt)
    response = inference_chat(split_instruction, args.api)
    response = response.split("Instructions:")[-1]

    plannings = []
    matches = re.findall(r'(\d+)\.\s*(.*?)(?=\n\d+\.|\Z)', response, re.DOTALL)
    for match in matches:
        _, step_content = match
        plannings.append(step_content)

    memories = []

    with open(f'dataset/documentation.json', 'r', encoding='utf-8') as f:
        documentations = json.load(f)
    with open(f'dataset/boundary_conditions.json', 'r', encoding='utf-8') as f:
        boundary_conditions = json.load(f)
    documentation, boundary_condition = "", ""

    one_step_plans = ['Search Item']
    multi_steps_plans = list(boundary_conditions.keys())

    plan_iter=-1
    x, y = get_size(args.adb_path)

    while(len(plannings) > 0):
        plan = plannings.pop(0)
        plan_iter += 1
        one_step_flag = False

        if 'find app' in plan.lower():
            action_controller.open_app(f'Open app {args.app_name}')
            time.sleep(5)
            continue

        for plan_type in one_step_plans:
            if plan_type.lower() == plan.lower()[:len(plan_type.lower())]:
                documentation, boundary_condition = documentations[plan_type], boundary_conditions.get(plan_type, '')
                actions = action_controller.action_split(plan, documentation, boundary_condition, plan_iter)
                action_controller.do_actions(actions, plan_iter)
                one_step_flag = True
                time.sleep(6)

        if one_step_flag:
            continue

        for plan_type in multi_steps_plans:
            if plan_type.lower() == plan.lower()[:len(plan_type.lower())]:
                documentation, boundary_condition = documentations[plan_type], boundary_conditions.get(plan_type, '')

        if "back home" in plan.lower():
            app_exit(args.adb_path)
        else:
            memory = action_controller.do_custome(plan, plan_iter, documentation, boundary_condition, memories)
            memories.append(memory)
        time.sleep(3)

    app_exit(args.adb_path)

if __name__ == "__main__":
    args = get_args()
    with open(f'dataset/{args.test_data}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    instruction = data[args.app_name]
    instruction = instruction[args.ins_cnt]
    args.instruction = instruction
    run(args)