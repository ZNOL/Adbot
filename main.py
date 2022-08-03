import os
from config import *

base_path = os.path.abspath(os.path.dirname(__file__))


def write_pid_file(pid_nr):
    with open(os.path.join(base_path, 'main.pid'), 'w') as f:
        f.write(pid_nr)


def delete_pid_file():
    try:
        os.remove(os.path.join(base_path, 'main.pid'))
    except FileNotFoundError:
        pass


def check_parallel_process():
    file = os.path.join(base_path, 'main.pid')
    try:
        f = open(file)
    except Exception:
        return True
    else:
        with f:
            _pid = f.readline()
        try:
            os.kill(int(_pid), 0)
        except Exception:
            logging.warning("PID file was found but process with its PID not running. Removing PID file")
            delete_pid_file()
            return True
        else:
            logging.warning(f"A running parallel process with ID {_pid} is found. Exiting")
            exit(0)


check_parallel_process()


from source.handler.commands import *
from source.handler.messages import *
from source.base.googledocs import *
from source.base.backupbase import *
from aiogram import executor


async def func(x):
    asyncio.create_task(sync_func())
    asyncio.create_task(questions_sendler())
    asyncio.create_task(sync_backup_func())


if __name__ == '__main__':
    pid = os.getpid()
    write_pid_file(str(pid))
    logging.info(f'*** BOT was started. PID={pid}')

    print('Started')
    executor.start_polling(dp, on_startup=func)

    delete_pid_file()
    logging.info(f'*** BOT was stopped. PID={pid}')
