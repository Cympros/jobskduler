# coding=utf-8

from schduler_controller import TaskSchdulerController

if __name__ == '__main__':
    tasks = ['exec_single_task', 'clear', 'check_env_dependence']
    while True:
        input_info = "------------------------执行任务列表-----------------------\n"
        for index, task_item in enumerate(tasks):
            input_info += str(index) + "：" + task_item + "\n"
        task_index_selected = input(input_info + "请选择需运行任务对应索引(索引下标越界触发程序退出)：")
        if task_index_selected.isdigit() is False:
            utils_logger.log("索引值非数字，请重新输入：", task_index_selected)
            continue
        task_index_selected = int(task_index_selected)
        if task_index_selected >= len(tasks) > 0:
            utils_logger.log("[" + str(task_index_selected) + "]任务索引不存在，退出程序...")
            break
        func_name = tasks[task_index_selected]
        controller = TaskSchdulerController()
        if hasattr(controller, func_name):
            func = getattr(controller, func_name)
            func()
