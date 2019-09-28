#!/user/bin/env python3
#检测调试的手机系统版本信息
import minium

mini = minium.Minium()
system_info = mini.get_system_info()
print(system_info)