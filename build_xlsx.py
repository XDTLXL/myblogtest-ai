# -*- coding: utf-8 -*-
"""生成《博客登录页测试用例》—— 规范测试用例格式（步骤级展开）"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\study\AI\deepseek-day\博客登录页_测试用例.xlsx"

# ================= 样式 =================
HDR_FILL = PatternFill("solid", fgColor="2F5597")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10.5, name="微软雅黑")
TITLE_FONT = Font(bold=True, size=14, name="微软雅黑")
FONT = Font(size=10, name="微软雅黑")
BOLD = Font(bold=True, size=10, name="微软雅黑")
BOLD_RED = Font(bold=True, size=10, name="微软雅黑", color="C00000")
THIN = Side(style="thin", color="B4C6E7")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
WRAP_C = Alignment(wrap_text=True, vertical="center", horizontal="center")
CENTER = Alignment(horizontal="center", vertical="center")

CASE_A = PatternFill("solid", fgColor="FFFFFF")   # 奇数用例底色
CASE_B = PatternFill("solid", fgColor="F2F7FC")   # 偶数用例底色
SEC_FILL = PatternFill("solid", fgColor="DDEBF7")

# ================= 用例数据 =================
# 每条: 编号, 模块, 标题, 优先级, 设计方法, 前置条件, 测试数据, [步骤(操作, 预期, 实际)], 结论
CASES = [
    ("A1", "A 正常登录", "正确账号密码登录成功并写入登录态", "P0", "等价类划分",
     "1.被测环境 http://127.0.0.1:9090 已启动可访问\n"
     "2.浏览器已打开登录页 /blog_login.html\n"
     "3.已清空 localStorage 中的 user_token",
     "用户名：zhangsan\n密码：123456",
     [("在\"用户名\"输入框输入 zhangsan", "输入框正确回显 zhangsan", "输入框回显 zhangsan"),
      ("在\"密码\"输入框输入 123456", "密码以掩码形式显示，不回显明文", "密码以掩码显示"),
      ("点击\"提交\"按钮", "发起 POST /user/login 请求，返回 code=SUCCESS 且 data 非空", "返回 code=SUCCESS，data 为非空 token 字符串"),
      ("登录成功后查看浏览器地址栏", "页面自动跳转到 blog_list.html", "URL 变为 /blog_list.html，标题切换为列表页"),
      ("查看 localStorage 中的 user_token", "token 已写入且与接口返回的 data 完全一致", "token 已写入，与响应体 data 一致")],
     "通过"),

    ("A2", "A 正常登录", "登录成功后跳转到博客列表页", "P0", "场景法",
     "1.被测环境已启动\n2.已打开登录页",
     "用户名：zhangsan\n密码：123456",
     [("输入正确的用户名与密码", "输入内容正确显示", "输入正确"),
      ("点击\"提交\"按钮", "登录成功后页面跳转至 blog_list.html", "跳转至 blog_list.html"),
      ("观察跳转后页面的标题", "标题不再是\"博客登陆页\"，应为列表页标题", "标题已切换，非\"博客登陆页\"")],
     "通过"),

    ("A3", "A 正常登录", "登录态在跳转后可持续（刷新不丢失）", "P0", "状态迁移",
     "1.被测环境已启动\n2.已成功登录一次",
     "用户名：zhangsan\n密码：123456",
     [("完成一次成功登录", "跳转至 blog_list.html", "登录成功并跳转"),
      ("读取 localStorage 中的 user_token", "能读到非空 token", "读到非空 token"),
      ("按 F5 刷新当前页面", "页面正常刷新，不发生跳转回登录页", "页面正常刷新，仍停留在列表页"),
      ("再次读取 localStorage 中的 user_token", "token 与刷新前保持一致（持久化存储）", "token 与刷新前完全一致")],
     "通过"),

    ("A4", "A 正常登录", "同一账号重复登录覆盖旧 token", "P1", "边界值分析",
     "1.被测环境已启动\n2.已打开登录页",
     "用户名：zhangsan\n密码：123456（同一账号连续登录两次）",
     [("首次登录并记录 localStorage 中的 token 值", "登录成功，token 被写入", "登录成功，token 写入"),
      ("再次使用同一账号登录", "第二次登录同样成功", "第二次登录成功"),
      ("对比两次的 token 值", "token 被重新写入；若两次签发值不同则以新值为准", "token 被重新签发（JWT 含 exp，两次值可能相同）")],
     "通过"),

    ("B1", "B 异常登录与提示", "用户名和密码均为空时提交", "P0", "边界值分析",
     "1.被测环境已启动\n2.已打开登录页\n3.已清空 localStorage",
     "用户名：（空）\n密码：（空）",
     [("两个输入框均不输入任何内容", "输入框保持为空", "输入框为空"),
      ("点击\"提交\"按钮", "接口返回 code=FAIL、data=null", "返回 code=FAIL，data 为 null"),
      ("观察页面弹出的提示", "弹出提示\"账号或密码不能为空\"", "弹出提示\"账号或密码不能为空\""),
      ("检查页面地址与 localStorage", "停留在登录页，且未写入 user_token", "停留在登录页，token 为空")],
     "通过"),

    ("B2", "B 异常登录与提示", "仅填写用户名、密码为空时提交", "P0", "边界值分析",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：zhangsan\n密码：（空）",
     [("只填写\"用户名\"为 zhangsan", "用户名输入框回显 zhangsan", "输入正确"),
      ("密码输入框留空", "密码框保持为空", "密码框为空"),
      ("点击\"提交\"按钮", "返回 code=FAIL，弹出提示\"账号或密码不能为空\"", "提示\"账号或密码不能为空\""),
      ("检查是否跳转、是否写入 token", "不跳转，localStorage 中无 token", "未跳转，token 为空")],
     "通过"),

    ("B3", "B 异常登录与提示", "仅填写密码、用户名为空时提交", "P0", "边界值分析",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：（空）\n密码：123456",
     [("用户名输入框留空", "用户名框保持为空", "用户名框为空"),
      ("只填写\"密码\"为 123456", "密码框以掩码显示", "密码框已填写"),
      ("点击\"提交\"按钮", "返回 code=FAIL，弹出提示\"账号或密码不能为空\"", "提示\"账号或密码不能为空\""),
      ("检查是否跳转、是否写入 token", "不跳转，localStorage 中无 token", "未跳转，token 为空")],
     "通过"),

    ("B4", "B 异常登录与提示", "用户名不存在时登录", "P0", "错误推测",
     "1.已打开登录页\n2.已清空 localStorage\n3.确认库中不存在该账号",
     "用户名：no_such_user_9527\n密码：123456",
     [("输入不存在的用户名 no_such_user_9527", "输入框回显该值", "输入正确"),
      ("输入任意密码并点击\"提交\"", "返回 code=FAIL", "返回 code=FAIL"),
      ("观察弹出的提示文案", "弹出提示\"用户不存在\"", "弹出提示\"用户不存在\""),
      ("检查页面地址与 localStorage", "停留在登录页，未签发 token", "停留登录页，token 为空")],
     "通过"),

    ("B5", "B 异常登录与提示", "用户名存在但密码错误时登录", "P0", "等价类划分",
     "1.已打开登录页\n2.已清空 localStorage\n3.确认 zhangsan 账号存在",
     "用户名：zhangsan\n密码：wrong_password_123",
     [("输入存在的用户名 zhangsan", "输入框回显 zhangsan", "输入正确"),
      ("输入错误密码 wrong_password_123", "密码以掩码显示", "已输入"),
      ("点击\"提交\"按钮", "返回 code=FAIL 且 data=null", "返回 code=FAIL，data 为 null"),
      ("观察弹出提示并检查登录态", "有明确错误提示，不跳转，不签发 token", "提示\"密码错误\"，未跳转，token 为空")],
     "通过"),

    ("B6", "B 异常登录与提示", "密码大小写敏感性验证", "P1", "错误推测",
     "1.已打开登录页\n2.已清空 localStorage\n注意：当前账号密码为纯数字，无法完整覆盖该场景",
     "用户名：zhangsan\n密码：WrongPasswordABC（大写形式）\n密码：wrongpasswordabc（小写形式）",
     [("用含字母的大写错误密码 WrongPasswordABC 调用登录接口", "返回 code=FAIL，不签发 token", "返回 FAIL，data 为 null"),
      ("用含字母的小写错误密码 wrongpasswordabc 调用登录接口", "返回 code=FAIL，不签发 token", "返回 FAIL，data 为 null"),
      ("在界面填入 WrongPasswordABC 并点击\"提交\"", "提示错误，停留在登录页，不写 token", "提示错误，停留登录页，token 为空"),
      ("验证 toUpperCase() 是否改变测试账号密码", "若密码为纯数字则本用例无法验证大小写敏感性，需补充含字母账号", "密码 123456 为纯数字，toUpperCase() 结果不变，该场景未能完整覆盖")],
     "通过（部分覆盖）"),

    ("B7", "B 异常登录与提示", "密码末尾追加空格时登录", "P1", "边界值分析",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：zhangsan\n密码：\"123456 \"（末尾一个半角空格）",
     [("在密码框输入 123456，并在末尾追加一个空格", "密码框以掩码显示，长度增加 1", "已输入，含末尾空格"),
      ("点击\"提交\"按钮", "返回 code=FAIL（服务端不对密码做 trim）", "返回 code=FAIL"),
      ("检查 localStorage 中的 token", "未签发 token", "token 为空")],
     "通过"),

    ("B8", "B 异常登录与提示", "用户名前后含空格时登录（trim 基线）", "P2", "边界值分析",
     "1.接口 /user/login 可访问",
     "用户名：\" zhangsan \"（前后各一个空格）\n密码：123456",
     [("用前后带空格的用户名调用登录接口", "记录服务端是否对用户名做 trim；SUCCESS 或 FAIL 均属基线行为", "服务端做了 trim，返回 code=SUCCESS 且 data 非空"),
      ("确认该行为是否稳定（参数化）", "行为可复现，不出现偶发差异", "行为稳定一致")],
     "通过"),

    ("C1", "C 输入域校验与边界", "超长用户名与密码输入", "P1", "边界值分析",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：'a' 重复 1000 次\n密码：'b' 重复 1000 次",
     [("在用户名输入 1000 个字符 a", "输入框可接受该长度输入", "输入成功"),
      ("在密码输入 1000 个字符 b", "密码框可接受该长度输入", "输入成功"),
      ("点击\"提交\"按钮", "接口不返回 5xx，返回可读的 FAIL", "返回 code=FAIL，HTTP 200"),
      ("检查页面是否卡死、是否写入 token", "页面可正常操作，未签发 token", "页面正常，token 为空")],
     "通过"),

    ("C2", "C 输入域校验与边界", "特殊字符作为用户名", "P1", "错误推测",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：!@#$%^&*()_+-=[]{}|;:'\",.<>/?\\\n密码：p@ss",
     [("输入上述特殊字符作为用户名", "输入框正确回显，无异常", "输入正常"),
      ("输入任意密码并点击\"提交\"", "无 JS 异常；服务端返回可读 FAIL", "无 pageerror，返回 code=FAIL"),
      ("检查控制台是否报错", "无未捕获的 JS 异常", "无未捕获异常")],
     "通过"),

    ("C3", "C 输入域校验与边界", "中文与 emoji 作为用户名", "P1", "错误推测",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：张三🔒测试\n密码：密码123",
     [("输入\"张三🔒测试\"作为用户名", "输入框正确显示，不乱码", "显示正常，无乱码"),
      ("输入\"密码123\"作为密码", "密码框以掩码显示", "已输入"),
      ("点击\"提交\"按钮", "接口不返回 5xx，不误判为登录成功", "返回 code=FAIL，未签发 token")],
     "通过"),

    ("C4", "C 输入域校验与边界", "纯空格作为用户名和密码", "P1", "边界值分析",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：\"    \"（4 个半角空格）\n密码：\"    \"（4 个半角空格）",
     [("两个输入框均输入 4 个空格", "输入框显示为空白但实际有内容", "已输入"),
      ("点击\"提交\"按钮", "返回 code=FAIL，不得被当作有效凭据放行", "返回 code=FAIL"),
      ("检查 localStorage 中的 token", "未签发 token", "token 为空")],
     "通过"),

    ("C5", "C 输入域校验与边界", "输入后清空再重新输入", "P1", "场景法",
     "1.已打开登录页",
     "首次输入：临时内容 / 临时密码\n重新输入：zhangsan / 123456",
     [("在用户名与密码框输入\"临时内容\"和\"临时密码\"", "输入框正确显示", "显示正确"),
      ("清空两个输入框", "两个输入框值均为空", "值均为空，断言通过"),
      ("重新输入 zhangsan 和 123456", "输入框显示为最新值，值绑定正确", "显示为最新值"),
      ("点击\"提交\"按钮", "登录成功，返回 code=SUCCESS", "返回 code=SUCCESS，登录成功")],
     "通过"),

    ("C6", "C 输入域校验与边界", "密码框掩码显示校验", "P1", "界面检查",
     "1.已打开登录页",
     "密码：123456",
     [("检查密码输入框的 type 属性", "type 属性值为 password", "type=password，断言通过"),
      ("在密码框输入 123456", "页面以圆点等掩码形式显示，不显示明文", "掩码显示，未暴露明文"),
      ("读取输入框的实际值", "实际值仍为 123456，仅显示被掩码", "inputValue 为 123456")],
     "通过"),

    ("D1", "D 安全测试", "SQL 注入防护（5 种载荷）", "P0", "错误推测",
     "1.已打开登录页\n2.已清空 localStorage\n3.接口 /user/login 可访问",
     "载荷1：' or '1'='1\n载荷2：' or 1=1 --\n载荷3：admin'--\n"
     "载荷4：\" or \"\"=\"\n载荷5：'; DROP TABLE user; --\n"
     "（每种载荷同时作为用户名与密码）",
     [("用载荷1 \"' or '1'='1\" 作为用户名和密码提交", "登录失败，返回 FAIL，不签发 token", "返回 FAIL，未签发 token"),
      ("用载荷2 \"' or 1=1 --\" 提交", "登录失败，不签发 token", "返回 FAIL，未签发 token"),
      ("用载荷3 \"admin'--\" 提交", "登录失败，不签发 token", "返回 FAIL，未签发 token"),
      ("用载荷4 '\" or \"\"=\"' 提交", "登录失败，不签发 token", "返回 FAIL，未签发 token"),
      ("用载荷5 \"'; DROP TABLE user; --\" 提交", "登录失败，不签发 token，数据表未被破坏", "返回 FAIL，未签发 token，后续用例仍可正常查询用户"),
      ("检查接口响应状态码", "不返回 5xx", "全部为 HTTP 200")],
     "通过"),

    ("D2", "D 安全测试", "XSS 载荷在错误提示路径是否执行", "P0", "错误推测",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：<script>alert('xss')</script>\n密码：<img src=x onerror=alert('xss')>",
     [("用户名输入 <script>alert('xss')</script>", "输入框原样显示该字符串", "已输入"),
      ("密码输入 <img src=x onerror=alert('xss')>", "密码框掩码显示", "已输入"),
      ("点击\"提交\"并监听所有弹窗", "只弹出服务端固定错误提示，不执行注入脚本", "仅弹出服务端固定提示，脚本未执行"),
      ("检查是否产生 JS 异常", "无未捕获的 JS 异常", "无 pageerror")],
     "通过"),

    ("D3", "D 安全测试", "错误提示是否回显用户输入", "P1", "错误推测",
     "1.接口 /user/login 可访问",
     "用户名：echo_probe_9527\n密码：whatever",
     [("用标记串 echo_probe_9527 作为用户名调用登录接口", "返回 code=FAIL", "返回 code=FAIL"),
      ("检查响应体 errMsg 字段内容", "理想情况下不应包含用户输入内容", "errMsg 为\"用户不存在\"，未回显输入，无回显风险")],
     "通过"),

    ("D4", "D 安全测试", "登录失败提示是否存在用户枚举", "P0", "错误推测",
     "1.接口 /user/login 可访问\n2.确认 no_such_user_8888 不存在、zhangsan 存在",
     "不存在账号：no_such_user_8888 / any\n存在账号：zhangsan / definitely_wrong_pwd",
     [("用不存在的账号登录并记录 errMsg", "记录提示文案", "返回\"用户不存在\""),
      ("用存在账号+错误密码登录并记录 errMsg", "记录提示文案", "返回\"密码错误\""),
      ("比对两次的提示文案是否一致", "提示应一致，不可区分账号是否存在", "两者不一致，可明确区分"),
      ("评估风险", "若可区分则存在用户枚举风险，需记为缺陷", "确认存在用户枚举风险，已记为 BUG-02")],
     "发现缺陷 BUG-02"),

    ("D5", "D 安全测试", "无有效凭据不得签发 token", "P0", "边界值分析",
     "1.已打开登录页\n2.已清空 localStorage",
     "用户名：（空）\n密码：（空）",
     [("清空 localStorage 后以空凭据调用登录接口", "返回 code=FAIL 且 data 为 null", "返回 code=FAIL，data 为 null"),
      ("检查 localStorage 是否被写入 token", "localStorage 中不存在 user_token", "user_token 为 null")],
     "通过"),

    ("D6", "D 安全测试", "连续多次登录失败是否限流", "P1", "边界值分析",
     "1.已打开登录页\n2.接口 /user/login 可访问",
     "用户名：zhangsan\n密码：wrong_0 至 wrong_4（连续 5 次错误密码）",
     [("连续 5 次用错误密码调用登录接口", "每次均返回 code=FAIL", "5 次均返回 code=FAIL"),
      ("记录每次响应的 HTTP 状态码", "应在若干次失败后出现限流（429/403）或锁定", "5 次均为 HTTP 200，无任何限流"),
      ("评估风险", "无限流则存在暴力破解风险，需记为缺陷", "确认存在暴力破解风险，已记为 BUG-03")],
     "发现缺陷 BUG-03"),

    ("D7", "D 安全测试", "未登录访问 blog_list.html 应被拦截", "P0", "场景法",
     "1.已打开登录页\n2.已清空 localStorage 登录态",
     "目标地址：http://127.0.0.1:9090/blog_list.html",
     [("清空 localStorage 中的登录态", "token 为空", "token 已清空"),
      ("在地址栏直接访问 blog_list.html", "页面应先到达 blog_list.html", "已到达 blog_list.html"),
      ("观察是否被登录守卫拦截", "被守卫拦截并跳转回 blog_login.html", "跳转回 blog_login.html，守卫生效"),
      ("检查登录页元素是否正常展示", "登录页表单可见", "提交按钮可见，页面正常")],
     "通过"),

    ("D8", "D 安全测试", "未登录访问 blog_edit.html 是否被拦截", "P0", "场景法",
     "1.已打开登录页\n2.已清空 localStorage 登录态",
     "目标地址：http://127.0.0.1:9090/blog_edit.html",
     [("清空 localStorage 中的登录态", "token 为空", "token 已清空"),
      ("在地址栏直接访问 blog_edit.html", "应被登录守卫拦截，行为与 blog_list.html 一致", "未发生任何跳转"),
      ("观察最终 URL", "应跳转回 blog_login.html", "仍停留在 blog_edit.html，页面被直接打开"),
      ("评估风险", "若可直接访问则存在未授权访问风险，需记为缺陷", "确认缺少登录守卫，已记为 BUG-01")],
     "发现缺陷 BUG-01"),

    ("E1", "E 交互与健壮性", "快速连点提交按钮", "P1", "错误推测",
     "1.已打开登录页\n2.已填入有效账号密码",
     "用户名：zhangsan\n密码：123456（连续点击\"提交\"3 次）",
     [("填写有效账号密码", "输入正确", "输入正确"),
      ("并发触发 3 次\"提交\"点击", "统计实际发出的 /user/login 请求数", "实测仅发出 1 次请求"),
      ("检查页面是否出现 JS 异常或崩溃", "无未捕获异常", "无 pageerror"),
      ("检查最终登录状态是否合法", "要么已登录跳转，要么停留在登录页，不得出现中间态", "最终状态合法（已登录并跳转）")],
     "通过"),

    ("E2", "E 交互与健壮性", "回车键是否可提交表单", "P1", "错误推测",
     "1.已打开登录页\n2.已填入有效账号密码",
     "用户名：zhangsan\n密码：123456",
     [("在用户名和密码框填入有效内容", "输入正确", "输入正确"),
      ("在密码框中按 Enter 键", "理想情况下应触发登录请求", "未发起任何登录请求，页面无反应"),
      ("评估影响", "若回车无效，属体验缺陷，需记录", "确认回车无法提交，已记为 BUG-05")],
     "发现缺陷 BUG-05"),

    ("E3", "E 交互与健壮性", "Tab 键焦点切换顺序", "P2", "界面检查",
     "1.已打开登录页",
     "无",
     [("点击用户名输入框使其获得焦点", "用户名输入框为当前焦点", "焦点正确"),
      ("按一次 Tab 键", "焦点移动到密码输入框", "焦点在密码框"),
      ("再按一次 Tab 键", "焦点移动到\"提交\"按钮", "焦点在提交按钮")],
     "通过"),

    ("E4", "E 交互与健壮性", "登录接口不可用时的用户反馈", "P1", "错误推测",
     "1.已打开登录页\n2.可拦截接口请求（如返回 500）",
     "拦截规则：/user/login 返回 HTTP 500",
     [("拦截 /user/login 并使其返回 HTTP 500", "拦截规则生效", "拦截生效"),
      ("填写账号密码并点击\"提交\"", "页面应给出明确的错误提示", "页面无任何提示、无 loading、无错误信息"),
      ("观察用户是否能感知异常", "用户应能明确感知失败原因", "用户完全无感知"),
      ("检查是否产生未捕获异常导致白屏", "不应白屏", "无未捕获异常，页面未白屏"),
      ("评估影响", "静默失败属健壮性缺陷，需记录", "确认缺少 error 回调，已记为 BUG-04")],
     "发现缺陷 BUG-04"),

    ("E5", "E 交互与健壮性", "接口返回非 JSON 内容时页面不白屏", "P1", "错误推测",
     "1.已打开登录页\n2.可拦截接口请求",
     "拦截规则：/user/login 返回 200 且内容为 text/html \n<body><html>oops</html>",
     [("拦截 /user/login 使其返回 text/html 内容", "拦截规则生效", "拦截生效"),
      ("填写账号密码并点击\"提交\"", "页面不崩溃、不白屏", "页面正常，未白屏"),
      ("检查页面地址与元素", "仍停留在登录页，表单可用", "URL 仍在 blog_login.html，提交按钮可见")],
     "通过"),

    ("F1", "F UI 与兼容", "标题文案与输入框必填约束检查", "P2", "界面检查",
     "1.已打开登录页",
     "无",
     [("查看登录对话框的标题文案", "文案应规范，应为\"登录\"", "标题为\"登陆\"，用词不规范"),
      ("检查用户名输入框的 required 属性", "应有必填约束或前端校验", "required 为 false，无必填约束"),
      ("检查密码输入框的 required 属性", "应有必填约束或前端校验", "required 为 false，无必填约束"),
      ("检查页面是否存在 form 元素", "规范的表单应包裹在 form 中", "页面不存在 form 元素"),
      ("评估影响", "文案与必填缺失属可用性缺陷，需记录", "确认文案与必填缺失，已记为 BUG-06")],
     "发现缺陷 BUG-06"),

    ("F2", "F UI 与兼容", "多分辨率下登录框可见且不溢出", "P2", "兼容性测试",
     "1.已打开登录页\n2.可调整浏览器窗口尺寸",
     "分辨率：1920x1080、1366x768、768x1024、375x667",
     [("设置窗口为 1920x1080 并访问登录页", "输入框与提交按钮可见，未溢出视口", "元素均可见，未溢出"),
      ("设置窗口为 1366x768", "元素可见且未溢出", "通过"),
      ("设置窗口为 768x1024", "元素可见且未溢出", "通过"),
      ("设置窗口为 375x667", "元素可见且未溢出，按钮边界在视口内", "元素可见，按钮未溢出")],
     "通过"),

    ("F3", "F UI 与兼容", "导航链接跳转行为一致性", "P1", "场景法",
     "1.已打开登录页\n2.已清空 localStorage 登录态",
     "导航链接：\"主页\"、\"写博客\"",
     [("点击导航栏\"主页\"链接", "跳转到 blog_list.html", "已到达 blog_list.html"),
      ("观察是否被登录守卫拦截", "未登录时应被拦截并弹回登录页", "被弹回 blog_login.html"),
      ("点击导航栏\"写博客\"链接", "行为应与\"主页\"一致，未登录时被拦截", "直接进入 blog_edit.html，未被拦截"),
      ("比对两页守卫行为", "两页守卫行为应一致", "行为不一致，已关联 BUG-01")],
     "发现缺陷 BUG-01"),

    ("F4", "F UI 与兼容", "静态资源可用性检查", "P2", "界面检查",
     "1.已打开登录页\n2.可监听网络响应",
     "访问 http://127.0.0.1:9090/blog_login.html",
     [("打开登录页并监听所有网络响应", "页面 HTML 应返回 200", "blog_login.html 返回 200"),
      ("记录所有状态码 >= 400 的资源", "依赖的 CSS/JS 资源应全部加载成功", "本次运行未出现状态码 >= 400 的资源"),
      ("确认页面样式与脚本已生效", "样式与 jQuery 正常加载", "样式正常，jQuery 可用")],
     "通过"),

    ("F5", "F UI 与兼容", "登录后浏览器后退的登录态表现", "P2", "状态迁移",
     "1.已打开登录页\n2.可使用有效账号登录",
     "用户名：zhangsan\n密码：123456",
     [("完成一次成功登录", "跳转至 blog_list.html", "登录成功并跳转"),
      ("点击浏览器\"后退\"按钮", "回到登录页 blog_login.html", "回到 blog_login.html"),
      ("检查 localStorage 中的 token 是否仍存在", "记录 token 状态", "token 仍存在（未失效）"),
      ("检查登录页表单是否可再次使用", "登录页正常展示，可再次登录", "提交按钮可见，页面可用")],
     "通过（基线）"),
]

DEFECTS = [
    ("BUG-01", "高", "安全", "blog_edit.html 缺少登录守卫",
     "未登录状态下可直接打开写博客页面，页面未做任何登录态校验。"
     "对比同一系统的 blog_list.html 具备守卫（会跳回登录页），两者行为不一致。",
     "1）清空 localStorage 登录态；\n2）直接访问 http://127.0.0.1:9090/blog_edit.html；\n"
     "3）观察页面是否正常打开。",
     "blog_list.html 跳转链路为 blog_list.html → blog_login.html（守卫生效）；\n"
     "blog_edit.html 无任何跳转，页面被直接打开（守卫缺失）。",
     "未授权用户可访问写操作页面，存在越权访问风险。",
     "为 blog_edit.html 增加与 blog_list.html 一致的登录态校验，未登录时跳转至登录页。",
     "D8、F3", "待修复"),
    ("BUG-02", "中", "安全", "登录失败提示存在用户枚举",
     "账号不存在与密码错误返回的提示文案不同，攻击者可据此区分账号是否存在。",
     "1）用不存在的账号 no_such_user_8888 登录并记录提示；\n"
     "2）用已存在账号 zhangsan + 错误密码登录并记录提示；\n3）对比两者。",
     "不存在账号返回\"用户不存在\"；密码错误返回\"密码错误\"，两者可明确区分。",
     "可批量探测系统内有效账号，为撞库攻击提供前提。",
     "两种情况统一返回模糊提示，例如\"账号或密码错误\"。",
     "D4", "待修复"),
    ("BUG-03", "中", "安全", "缺少登录失败次数限制",
     "连续多次错误登录未触发任何限流、锁定或验证码机制。",
     "1）连续 5 次用错误密码调用 /user/login 接口；\n2）记录每次响应状态码。",
     "5 次失败均返回 HTTP 200 与 code=FAIL，无限流、无锁定、无验证码。",
     "可被暴力破解或撞库，系统无任何阻断能力。",
     "增加失败次数限制、图形验证码或账号临时锁定策略。",
     "D6", "待修复"),
    ("BUG-04", "低", "健壮性", "AJAX 缺少 error 回调导致异常静默失败",
     "登录接口异常时前端不给用户任何反馈。",
     "1）拦截 /user/login 并返回 HTTP 500；\n2）提交登录表单；\n3）观察页面反馈。",
     "页面无任何提示、无 loading 状态、无错误信息，用户完全无感知；"
     "但未出现未捕获异常导致的白屏。",
     "网络或服务端异常时用户会误以为点击无效而反复点击。",
     "为 $.ajax 增加 error 回调，提示\"网络异常，请稍后重试\"。",
     "E4", "待修复"),
    ("BUG-05", "低", "可用性", "回车键无法提交表单",
     "页面没有 form 元素，也没有键盘事件监听，回车键无效。",
     "1）填写用户名与密码；\n2）在密码框按 Enter；\n3）观察是否发起登录请求。",
     "未发起任何登录请求，页面无任何反应。",
     "违反用户对登录表单的常规预期，降低操作效率。",
     "将表单包裹在 form 元素中，或监听 keydown 回车事件触发提交。",
     "E2", "待修复"),
    ("BUG-06", "低", "文案与规范", "标题文案不规范且输入框缺少必填约束",
     "登录框标题使用\"登陆\"，且两个输入框均未设置 required 属性，页面无 form 元素。",
     "1）查看登录对话框标题文案；\n2）检查 #username 与 #password 的 required 属性。",
     "标题为\"登陆\"（规范用词应为\"登录\"）；两个输入框 required 均为 false；"
     "页面不存在 form 元素。",
     "文案不规范；缺少前端必填校验，空值校验完全依赖服务端。",
     "修正文案为\"登录\"；为输入框补充 required 属性或前端校验提示。",
     "F1", "待修复"),
]

MODULES = [
    ("A 正常登录", "验证正确凭据下的登录主流程、登录态写入与页面跳转", "正常功能"),
    ("B 异常登录与提示", "验证各类错误输入的错误提示、失败后不留登录态", "异常功能"),
    ("C 输入域校验与边界", "验证输入框在极端与非法输入下的健壮性", "边界测试"),
    ("D 安全测试", "验证注入防护、错误信息泄露、越权访问、暴力破解防护", "安全测试"),
    ("E 交互与健壮性", "验证用户交互细节与前端异常场景下的表现", "健壮性测试"),
    ("F UI 与兼容", "验证文案规范、必填约束、多分辨率与静态资源", "兼容性测试"),
]

wb = Workbook()

# ============================================================
# Sheet 1: 用例说明（模板定义）
# ============================================================
ws0 = wb.active
ws0.title = "用例说明"
ws0.sheet_view.showGridLines = False
ws0["A1"] = "博客登录页 测试用例"
ws0["A1"].font = TITLE_FONT
ws0.merge_cells("A1:B1")

rows0 = [
    ("被测系统", "博客系统（我的博客系统）"),
    ("被测页面", "http://127.0.0.1:9090/blog_login.html"),
    ("核心接口", "POST /user/login（application/json 响应，code=SUCCESS/FAIL）"),
    ("测试账号", "zhangsan / 123456"),
    ("用例总数", f"{len(CASES)} 条"),
    ("测试步骤总数", f"{sum(len(c[7]) for c in CASES)} 步"),
    ("执行结果", "全部执行通过；其中 6 条用例在执行中发现缺陷（详见\"缺陷清单\"）"),
    ("", ""),
    ("【字段说明】", ""),
    ("用例编号", "模块字母 + 序号，如 A1 表示 A 模块第 1 条用例"),
    ("所属模块", "按测试类型划分为 A~F 共 6 个模块"),
    ("用例标题", "一句话描述该用例验证的目标"),
    ("优先级", "P0 冒烟/核心必测；P1 重要；P2 一般"),
    ("设计方法", "该用例采用的设计方法，如等价类划分、边界值分析、错误推测、场景法等"),
    ("前置条件", "执行该用例前必须满足的环境与数据状态"),
    ("测试数据", "该用例使用的具体输入数据"),
    ("步骤序号", "用例内的步骤序号，每条用例的步骤从 1 开始编号"),
    ("测试步骤", "该步骤的具体操作动作"),
    ("预期结果", "该步骤执行后应出现的正确结果"),
    ("实际结果", "实际执行后观察到的结果（本次为自动化实测值）"),
    ("结论", "该用例的整体执行结论"),
    ("", ""),
    ("【阅读说明】", ""),
    ("行结构", "一个测试步骤占用一行；同一用例的多个步骤共用左上角的用例信息（仅首行显示）"),
    ("底色区分", "相邻用例以白色/浅蓝色交替底色区分，便于快速定位每条用例的范围"),
    ("结论列", "标注\"发现缺陷 BUG-xx\"的用例，表示该用例执行后确认了缺陷，"
              "对应缺陷详情见\"缺陷清单\"工作表"),
]
r = 3
for k, v in rows0:
    c1 = ws0.cell(r, 1, k)
    c1.font = BOLD if not k.startswith("【") else Font(bold=True, size=11, name="微软雅黑", color="C00000")
    c1.fill = SEC_FILL
    c1.border = BORDER
    c1.alignment = WRAP
    c2 = ws0.cell(r, 2, v)
    c2.font = FONT
    c2.border = BORDER
    c2.alignment = WRAP
    ws0.row_dimensions[r].height = 20 if len(v) < 45 else 34
    r += 1
ws0.column_dimensions["A"].width = 16
ws0.column_dimensions["B"].width = 92

# ============================================================
# Sheet 2: 测试用例（步骤级展开，规范格式）
# ============================================================
ws = wb.create_sheet("测试用例")
ws.sheet_view.showGridLines = False
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True

HEADERS = ["用例编号", "所属模块", "用例标题", "优先级", "设计方法",
           "前置条件", "测试数据", "步骤序号", "测试步骤", "预期结果", "实际结果", "结论"]
WIDTHS = [9, 14, 24, 7, 12, 30, 26, 7, 34, 34, 34, 13]

for i, (h, w) in enumerate(zip(HEADERS, WIDTHS), start=1):
    c = ws.cell(1, i, h)
    c.font = HDR_FONT
    c.fill = HDR_FILL
    c.alignment = CENTER
    c.border = BORDER
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 26
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:L{1 + sum(len(c[7]) for c in CASES)}"

ST_COLOR = {"发现缺陷": "C00000", "通过": "1F6B33"}
row = 2
for idx, case in enumerate(CASES):
    cid, mod, title, pri, method, pre, data, steps, result = case
    fill = CASE_A if idx % 2 == 0 else CASE_B
    start = row
    for si, (op, exp, act) in enumerate(steps, start=1):
        vals = [cid, mod, title, pri, method, pre, data, si, op, exp, act, ""]
        for ci, v in enumerate(vals, start=1):
            cell = ws.cell(row, ci, v)
            cell.font = FONT
            cell.border = BORDER
            cell.fill = fill
            cell.alignment = CENTER if ci in (4, 8) else WRAP
        # 优先级着色
        if pri == "P0":
            ws.cell(row, 4).font = BOLD_RED
        elif pri == "P1":
            ws.cell(row, 4).font = BOLD
        # 结论只写在最后一行
        if si == len(steps):
            cc = ws.cell(row, 12, result)
            cc.font = Font(bold=True, size=10, name="微软雅黑",
                           color=ST_COLOR["发现缺陷"] if result.startswith("发现缺陷") else ST_COLOR["通过"])
            cc.alignment = WRAP_C
            cc.border = BORDER
            cc.fill = fill
        row += 1
    # 合并用例级字段
    for ci in (1, 2, 3, 4, 5, 6, 7):
        if len(steps) > 1:
            ws.merge_cells(start_row=start, start_column=ci,
                           end_row=row - 1, end_column=ci)
        ws.cell(start, ci).alignment = WRAP_C if ci in (1, 2, 4) else WRAP
    end = row - 1
    for ci in (1, 2, 3, 4, 5, 6, 7):
        if len(steps) > 1:
            ws.cell(start, ci).alignment = Alignment(
                wrap_text=True, vertical="center",
                horizontal="center" if ci in (1, 2, 4, 5) else "left")

# ============================================================
# Sheet 3: 模块划分
# ============================================================
ws1 = wb.create_sheet("模块划分")
ws1.sheet_view.showGridLines = False
ws1["A1"] = "测试模块划分"
ws1["A1"].font = TITLE_FONT
ws1.merge_cells("A1:F1")
for i, (h, w) in enumerate(zip(
        ["模块", "模块说明", "测试类型", "用例数", "步骤数", "用例编号"],
        [16, 44, 12, 9, 9, 30]), start=1):
    c = ws1.cell(3, i, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws1.column_dimensions[get_column_letter(i)].width = w
r = 4
for name, desc, ttype in MODULES:
    sub = [c for c in CASES if c[1] == name]
    ids = "、".join(c[0] for c in sub)
    vals = [name, desc, ttype, len(sub), sum(len(c[7]) for c in sub), ids]
    for ci, v in enumerate(vals, start=1):
        cell = ws1.cell(r, ci, v)
        cell.font = FONT; cell.border = BORDER
        cell.alignment = WRAP if ci == 2 else WRAP_C
    r += 1
tot = ["合计", "", "", len(CASES), sum(len(c[7]) for c in CASES),
       f"{len(CASES)} 条用例 / {sum(len(c[7]) for c in CASES)} 个步骤"]
for ci, v in enumerate(tot, start=1):
    cell = ws1.cell(r, ci, v)
    cell.font = BOLD; cell.fill = SEC_FILL; cell.border = BORDER
    cell.alignment = WRAP_C

# ============================================================
# Sheet 4: 缺陷清单
# ============================================================
ws2 = wb.create_sheet("缺陷清单")
ws2.sheet_view.showGridLines = False
ws2.page_setup.orientation = "landscape"
ws2.sheet_properties.pageSetUpPr.fitToPage = True
ws2.page_setup.fitToWidth = 1
dh = ["缺陷编号", "严重级别", "类别", "缺陷标题", "缺陷描述",
      "复现步骤", "实际结果", "影响", "修复建议", "关联用例", "状态"]
dw = [10, 10, 10, 26, 34, 36, 36, 28, 32, 12, 10]
for i, (h, w) in enumerate(zip(dh, dw), start=1):
    c = ws2.cell(1, i, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.row_dimensions[1].height = 26
ws2.freeze_panes = "A2"
SEV_FILL = {"高": PatternFill("solid", fgColor="F4B6B6"),
            "中": PatternFill("solid", fgColor="FDE9C9"),
            "低": PatternFill("solid", fgColor="E2EFDA")}
for ri, d in enumerate(DEFECTS, start=2):
    for ci, v in enumerate(d, start=1):
        c = ws2.cell(ri, ci, v)
        c.font = FONT; c.border = BORDER
        c.alignment = WRAP_C if ci in (1, 2, 3, 10, 11) else WRAP
    ws2.cell(ri, 2).fill = SEV_FILL[d[1]]
    ws2.cell(ri, 2).font = BOLD

# ============================================================
# Sheet 5: 执行统计
# ============================================================
ws3 = wb.create_sheet("执行统计")
ws3.sheet_view.showGridLines = False
ws3["A1"] = "执行统计"
ws3["A1"].font = TITLE_FONT
ws3.merge_cells("A1:D1")
for i, (h, w) in enumerate(zip(["统计项", "数值", "说明", ""], [22, 12, 46, 2]), start=1):
    c = ws3.cell(3, i, h)
    if i <= 3:
        c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws3.column_dimensions[get_column_letter(i)].width = w
stats = [
    ("用例总数", f"{len(CASES)} 条", "见\"测试用例\"工作表"),
    ("测试步骤总数", f"{sum(len(c[7]) for c in CASES)} 步", "每条用例按步骤逐行展开"),
    ("自动化执行次数", "40 次", "D1 SQL 注入参数化为 5 次执行"),
    ("执行通过", "40 次", "断言层面无失败"),
    ("通过率", "100%", "40 / 40"),
    ("发现缺陷", f"{len(DEFECTS)} 个", "1 高 / 2 中 / 3 低，详见\"缺陷清单\""),
    ("结论为\"发现缺陷\"的用例", "6 条", "D4、D6、D8、E2、E4、F1"),
    ("未能完整覆盖", "1 条", "B6 密码大小写敏感性：账号密码为纯数字，无法验证"),
]
r = 4
for k, v, note in stats:
    for ci, val in enumerate([k, v, note], start=1):
        c = ws3.cell(r, ci, val)
        c.font = BOLD if ci == 1 else FONT
        c.border = BORDER
        c.alignment = WRAP_C if ci != 3 else WRAP
    r += 1

# 优先级分布
r += 1
ws3.cell(r, 1, "优先级分布").font = BOLD
r += 1
for ci, h in enumerate(["优先级", "用例数", "含义"], start=1):
    c = ws3.cell(r, ci, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
r += 1
for p, mean in [("P0", "冒烟/核心必测"), ("P1", "重要功能"), ("P2", "一般功能")]:
    n = sum(1 for c in CASES if c[3] == p)
    for ci, v in enumerate([p, n, mean], start=1):
        c = ws3.cell(r, ci, v)
        c.font = FONT; c.border = BORDER
        c.alignment = WRAP_C if ci != 3 else WRAP
    r += 1

wb.save(OUT)
print("OK", len(CASES), "cases,", sum(len(c[7]) for c in CASES), "steps")
