import subprocess
import time

from ppadb.client import Client as AdbClient


class AndroidConnector:

    def __init__(self):

        client = AdbClient(host="127.0.0.1", port=5037)
        self.device = client.device("emulator-5554")
        self.queue = []
        self.busy = 0

    def add_queue(self, link, pin):
        self.queue.append([link, pin])

    def try_pay(self):
        check = 0
        while check == 0:
            if len(self.queue) > 0 and self.busy == 0:
                link, pin = self.queue.pop(0)
                self.busy = 1
                try:
                    self.script(link, pin)
                except:
                    pass
                self.busy = 0
                check = 1
            else:
                time.sleep(5)

    def click(self, x, y):
        self.device.shell(f'input tap {x} {y}')

    def send_text(self, text):
        self.device.shell(f'input text "{text}"')

    def send_rus(self):
        self.device.shell("am broadcast -a ADB_INPUT_TEXT --es msg 'asdf'")

    def go_home(self):
        self.device.shell('input keyevent 3')

    def open_browser(self):
        time.sleep(5)
        self.go_home()
        time.sleep(5)
        self.click(904, 333)

    def search(self, link):
        self.click(340, 145)
        time.sleep(2)
        self.send_text(link)
        time.sleep(2)
        self.device.shell('input keyevent 66')  # enter

    def sbp_open_in_app(self):
        # self.click(150, 830)
        # time.sleep(2)
        # self.send_text(app_name)
        time.sleep(2)
        # qiwi 237, 1100
        # sber 237, 1240
        # tin 237, 1372
        # vtb 237, 1506
        # alfa 237, 1641
        # raif 237, 1766
        self.click(237, 1100)
        time.sleep(2)

    def open_link_in_app(self):
        self.click(992, 158)
        time.sleep(5)
        self.click(534, 1233)
        time.sleep(5)
        self.click(658, 1360)

    def pay_in_app(self):

        self.click(528, 1802)
        time.sleep(7)
        self.click(974, 1797)
        time.sleep(7)

    def screenshot(self):
        self.device.shell('screencap -p /sdcard/image.png')
        self.device.pull('/sdcard/image.png', 'C:\\Users\\User\\PycharmProjects\\Wildberries — копия')

    def script(self, link, pin):
        self.unlock_app(pin)
        time.sleep(3)
        self.open_browser()
        time.sleep(7)
        self.search(link)
        time.sleep(7)
        self.open_link_in_app()
        time.sleep(7)
        self.pay_in_app()
        time.sleep(3)
        self.clear_apps()
        self.go_home()

    def unlock_app(self, pin):
        self.go_home()
        time.sleep(3)
        self.click(670, 346)
        time.sleep(7)
        codes = {'1': [233, 1047], '2': [540, 1047], '3': [846, 1047],
                 '4': [233, 1244], '5': [540, 1244], '6': [846, 1244],
                 '7': [233, 1426], '8': [540, 1426], '9': [846, 1426], '0': [534, 1621]}

        for i in pin:
            # print(i, codes[i][0])
            self.click(codes[i][0], codes[i][1])
            time.sleep(1)
        time.sleep(7)
        self.go_home()

    def clear_apps(self):
        self.device.input_keyevent('KEYCODE_APP_SWITCH')
        time.sleep(3)
        for i in range(3):
            self.device.input_swipe(502, 148, 502, 1725, 500)
            time.sleep(3)
        self.click(867, 169)


device = AndroidConnector()


def run_update_adb():
    while True:
        command = f"C:\\adb\\adb devices"
        r = subprocess.check_call(command)
        print(r)
        time.sleep(3600)

#
# def click_on_picture(image, x1, y1, x2, y2, t):
#     try:
#         while t > 0:
#             #screen = pag.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
#             screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
#             cv2_image = cv2.imread(image)
#             match = cv2.matchTemplate(cv2_image, screen, cv2.TM_SQDIFF_NORMED)
#             v, _, a, _ = cv2.minMaxLoc(match)
#             res_x, res_y = a
#             res_x += x1
#             res_y += y1
#             if (v < 0.1):
#                 return (res_x + 2, res_y + 2)
#                 break
#             else:
#                 time.sleep(0.5)
#                 t -= 0.5
#         else:
#             pass
#     except Exception as e:
#         print(e, "cant find picture")

if __name__ == '__main__':
    # command = f"C:\\adb\\adb devices"
    # r = subprocess.check_call(command)
    # print(r)
    # link = 'https://qr.nspk.ru/BD10002SS33UM3BS9LHR7LGJ62M96T4C?type=02&bank=100000000014&sum=277200&cur=RUB&crc=43EA'
    #res = device.device.shell('dumpsys activity activities')
    # for i in range(20):
    #     device.device.input_keyevent(i)
    #     time.sleep(2)
    #
    #     time.sleep(2)

    device.device.input_keyevent(' KEYCODE_APP_SWITCH')
    time.sleep(3)
    device.device.input_swipe(502, 148, 502, 1725, 500)
    time.sleep(3)
    device.click(867, 169)
    #res = device.device.killforward_all()

    # device.add_queue(link, '1320')
    # device.try_pay()
   # device.run_update_adb()
    # codes = {'1': [233, 1047], '2': [540, 1047], '3': [846, 1047],
    #          '4': [233, 1244], '5': [540, 1244], '6': [846, 1244],
    #          '7': [233, 1426], '8': [540, 1426], '9': [846, 1426], '0': [534, 1621]}
    # pin = '1320'
    # for i in pin:
    #     print(i, codes[i[0][0]])
    # device.add_queue(link)
    # device.try_pay()
