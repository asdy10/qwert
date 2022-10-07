import threading

lock = threading.Lock()


def write_log(text):
    with lock:
        try:
            with open('logs.txt', 'a') as f:
                f.write(f'\n{text}')
        except:
            print('ERROR LOG')
