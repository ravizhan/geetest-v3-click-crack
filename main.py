import json
import time
from crack import Crack
from model import Model
import httpx


t = time.time()

tt = time.time()
reg = httpx.get(
    f"https://www.geetest.com/demo/gt/register-click-official?t={str(round(time.time()))}"
).json()
print(time.time() - tt)

crack = Crack(reg["gt"], reg["challenge"])

tt = time.time()
crack.gettype()
print(time.time() - tt)

tt = time.time()
crack.get_c_s()
print(time.time() - tt)

time.sleep(0.5)

tt = time.time()
crack.ajax()
print(time.time() - tt)

model = Model()

for retry in range(6):
    tt = time.time()
    pic_content = crack.get_pic(retry)
    print(time.time() - tt)

    ttt = tt = time.time()
    small_img, big_img = model.detect(pic_content)
    print(
        f"检测到小图: {len(small_img.keys())}个,大图: {len(big_img)} 个,用时: {time.time() - tt}s"
    )
    tt = time.time()
    result_list = model.siamese(small_img, big_img)
    print(f"文字配对完成,用时: {time.time() - tt}")
    point_list = []
    # print(result_list)
    for i in result_list:
        left = str(round((i[0] + 30) / 333 * 10000))
        top = str(round((i[1] + 30) / 333 * 10000))
        point_list.append(f"{left}_{top}")
    wait_time = 2.0 - (time.time() - ttt)
    time.sleep(wait_time)
    tt = time.time()
    result = json.loads(crack.verify(point_list))
    print(result)
    print(time.time() - tt)
    if result["data"]["result"] == "success":
        break
total_time = time.time() - t
print(f"总计耗时(含等待{wait_time}s): {total_time}")
