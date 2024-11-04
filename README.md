# geetest-v3-click-crack
极验三代文字点选验证码破解

**本项目仅供学习交流使用，请勿用于商业用途，否则后果自负。**

**本项目仅供学习交流使用，请勿用于商业用途，否则后果自负。**

**本项目仅供学习交流使用，请勿用于商业用途，否则后果自负。**

# 使用方法

安装相关依赖

```commandline
pip install -r requirements.txt
```
运行

```commandline
python main.py
```

验证全过程耗时4s左右 (极验限制，不能更短)

成功率80%左右

# DEMO

``` python
# 实例化两个类
crack = Crack(gt, challenge)
model = Model()
# 按顺序执行以下四个函数
crack.gettype()
crack.get_c_s()
crack.ajax()
for retry in range(6):
    pic_content = crack.get_pic(retry)
    # 检测文字位置
    small_img, big_img = model.detect(pic_content)
    # 判断点选顺序
    result_list = model.siamese(small_img, big_img)
    point_list = []
    for i in result_list:
        left = str(round((i[0] + 30) / 333 * 10000))
        top = str(round((i[1] + 30) / 333 * 10000))
        point_list.append(f"{left}_{top}")
    # 验证请求
    # 注意 请确保验证与获取图片间隔不小于2s
    # 否则会报 duration short
    result = crack.verify(point_list)
    print(result)
    if eval(result)["data"]["result"] == "success":
        break
```

# 协议
本项目遵循 AGPL-3.0 协议开源，请遵守相关协议。

# 鸣谢
[ultralytics](https://github.com/ultralytics/ultralytics/) 提供目标检测模型

[Siamese-pytorch](https://github.com/bubbliiiing/Siamese-pytorch) 提供孪生网络模型

[biliTicker_gt](https://github.com/Amorter/biliTicker_gt) 提供部分思路

[https://www.52pojie.cn/thread-1909489-1-1.html](https://www.52pojie.cn/thread-1909489-1-1.html) 提供部分思路

ChatGPT 提供逆向支持
