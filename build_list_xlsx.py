# -*- coding: utf-8 -*-
"""生成《博客列表页测试用例》—— 规范测试用例格式（步骤级展开）"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\study\AI\deepseek-day\博客列表页_测试用例.xlsx"

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
CASE_A = PatternFill("solid", fgColor="FFFFFF")
CASE_B = PatternFill("solid", fgColor="F2F7FC")
SEC_FILL = PatternFill("solid", fgColor="DDEBF7")

LOGIN_PRE = ("1.被测环境 http://127.0.0.1:9090 已启动\n"
             "2.已用 zhangsan/123456 登录并持有有效 user_token")

# (编号, 模块, 标题, 优先级, 设计方法, 前置条件, 测试数据, [(操作, 预期, 实际)], 结论)
CASES = [
    ("A1", "A 列表渲染", "正常登录后列表页渲染出博客卡片", "P0", "场景法", LOGIN_PRE,
     "登录账号：zhangsan / 123456",
     [("使用有效账号完成登录", "登录成功并跳转到 blog_list.html", "登录成功，跳转列表页"),
      ("等待右侧博客列表渲染完成", "右侧出现至少 1 个博客卡片", "渲染出 1 个博客卡片"),
      ("统计卡片数量并与接口返回条数比对", "卡片数与 /blog/getList 返回的 data 长度一致", "卡片数 1，接口返回 1 条，一致"),
      ("检查页面标题", "标题为\"博客列表页\"", "标题为\"博客列表页\"，断言通过")],
     "通过"),

    ("A2", "A 列表渲染", "卡片四个字段均正确渲染", "P0", "界面检查", LOGIN_PRE,
     "拦截 /blog/getList 返回：\nid=10001, title=字段校验标题,\ncontent=字段校验内容, createTime=2025-06-01 09:30",
     [("拦截 getList 接口返回上述单条数据", "拦截生效", "拦截生效"),
      ("打开列表页并等待渲染", "渲染出 1 个博客卡片", "渲染 1 个卡片"),
      ("校验标题字段", "显示\"字段校验标题\"", "显示\"字段校验标题\""),
      ("校验日期字段", "显示包含 2025-06-01", "显示 2025-06-01 09:30"),
      ("校验内容字段", "显示包含\"字段校验内容\"", "显示\"字段校验内容\""),
      ("校验详情链接", "href 为 blog_detail.html?blogId=10001", "href 正确")],
     "通过"),

    ("A3", "A 列表渲染", "详情链接 href 与接口 id 一致", "P0", "界面检查", LOGIN_PRE,
     "拦截 getList 返回 id=54321 的单条数据",
     [("拦截 getList 返回 id=54321 的数据", "拦截生效", "拦截生效"),
      ("打开列表页并读取详情链接 href", "href 为 blog_detail.html?blogId=54321", "href 与 id 完全一致")],
     "通过"),

    ("A4", "A 列表渲染", "多条博客按接口顺序渲染", "P0", "场景法", LOGIN_PRE,
     "拦截 getList 返回 3 条：第一篇(id=1)、第二篇(id=2)、第三篇(id=3)",
     [("拦截 getList 返回 3 条数据", "拦截生效", "拦截生效"),
      ("打开列表页并统计卡片数", "卡片数为 3", "卡片数为 3"),
      ("读取标题顺序", "顺序为 第一篇、第二篇、第三篇，与接口顺序一致", "顺序与接口完全一致")],
     "通过"),

    ("A5", "A 列表渲染", "超长标题与内容不被截断", "P1", "边界值分析", LOGIN_PRE,
     "拦截 getList 返回：标题 200 字、内容 800 字",
     [("拦截 getList 返回超长标题与内容", "拦截生效", "拦截生效"),
      ("渲染后读取标题实际长度", "记录是否截断", "标题 200 字 → 渲染 200 字，未截断"),
      ("读取内容实际长度", "记录是否截断", "内容 800 字 → 渲染 800 字，未截断"),
      ("评估影响", "长文本全量渲染在大数据量下可能影响性能", "当前不做截断，已记录为性能建议项")],
     "通过"),

    ("A6", "A 列表渲染", "特殊字符标题的渲染与转义", "P1", "错误推测", LOGIN_PRE,
     "标题与内容：引号\"单引号'与&符号<>尖括号",
     [("拦截 getList 返回含特殊字符的数据", "拦截生效", "拦截生效"),
      ("检查渲染文本是否包含 & 与\"尖括号\"", "文本正常显示，无乱码", "正常显示 & 与\"尖括号\""),
      ("检查标题内是否产生真实子元素", "尖括号未形成元素（作为文本渲染）", "子元素数 0，作为文本渲染")],
     "通过"),

    ("B1", "B 鉴权与访问控制", "未登录访问列表页被守卫拦截", "P0", "场景法",
     "1.已打开登录页\n2.已清空 localStorage 登录态",
     "目标地址：http://127.0.0.1:9090/blog_list.html",
     [("清空 localStorage 中的 user_token", "token 为空", "token 已清空"),
      ("在地址栏直接访问 blog_list.html", "先到达 blog_list.html", "已到达 blog_list.html"),
      ("观察是否被登录守卫拦截", "跳转回 blog_login.html", "跳转回登录页，守卫生效")],
     "通过"),

    ("B2", "B 鉴权与访问控制", "伪造 token 访问列表页被拦截", "P0", "错误推测",
     "1.已打开登录页",
     "伪造 token：garbage.token.xxx",
     [("向 localStorage 写入伪造 token", "token 已写入", "写入成功"),
      ("访问 blog_list.html", "接口返回 401，前端跳转登录页", "跳转回 blog_login.html"),
      ("检查跳转链路", "链路包含 blog_list.html → blog_login.html", "链路正确")],
     "通过"),

    ("B3", "B 鉴权与访问控制", "空字符串 token 请求列表接口返回 401", "P0", "边界值分析",
     "1.接口 /blog/getList 可访问",
     "请求头：user_token_header: \"\"（空字符串）",
     [("以空字符串 token 作为请求头调用 getList", "返回 HTTP 401", "返回 401，鉴权拒绝")],
     "通过"),

    ("B4", "B 鉴权与访问控制", "token 头名称错误时返回 401", "P0", "错误推测",
     "1.已获取有效 token\n2.接口可访问",
     "正确头名：user_token_header\n错误头名：user_token\n值：同一个有效 token",
     [("用错误头名 user_token 携带有效 token 请求", "返回 401", "返回 401"),
      ("用正确头名 user_token_header 携带同一 token 请求", "返回 200 且 code=SUCCESS", "返回 200 SUCCESS"),
      ("确认鉴权严格依赖头名", "头名错误即拒绝，说明鉴权按头名取值", "确认严格依赖 user_token_header")],
     "通过"),

    ("B5", "B 鉴权与访问控制", "有效 token 正常获取列表数据", "P0", "等价类划分", LOGIN_PRE,
     "有效 token（由 /user/login 获取）",
     [("以有效 token 调用 getList", "返回 200 且 code=SUCCESS", "返回 200 SUCCESS"),
      ("检查 data 字段类型", "data 为数组", "data 为数组，断言通过")],
     "通过"),

    ("C1", "C 注销", "点击注销清除 token 并跳转登录页", "P0", "场景法", LOGIN_PRE,
     "登录账号：zhangsan / 123456",
     [("确认当前已登录（token 存在）", "token 非空", "token 存在"),
      ("点击导航栏\"注销\"链接", "清除 user_token 并跳转 blog_login.html", "token 被清除，跳转登录页"),
      ("检查 localStorage", "user_token 为 null", "user_token 为 null")],
     "通过"),

    ("C2", "C 注销", "注销后再访问列表页被拦截", "P0", "场景法", LOGIN_PRE,
     "登录账号：zhangsan / 123456",
     [("完成登录后点击注销", "注销成功，跳转登录页", "注销成功"),
      ("再次访问 blog_list.html", "被守卫拦截并跳转登录页", "跳转回 login 页，拦截有效")],
     "通过"),

    ("C3", "C 注销", "注销后浏览器后退的状态", "P2", "状态迁移", LOGIN_PRE,
     "登录账号：zhangsan / 123456",
     [("完成登录后点击注销", "注销成功，跳转登录页", "注销成功"),
      ("点击浏览器\"后退\"按钮", "回到历史页面", "回到 blog_list.html#"),
      ("检查 localStorage 中的 token", "token 不得被恢复", "token 仍为空，未被恢复"),
      ("确认无可用登录态", "不存在可用登录态", "确认无登录态")],
     "通过"),

    ("D1", "D 错误与异常处理", "getList 返回 FAIL 时无任何提示", "P1", "错误推测", LOGIN_PRE,
     "拦截 /blog/getList 返回：{\"code\":\"FAIL\",\"errMsg\":\"服务器开小差了\",\"data\":null}",
     [("拦截 getList 返回 code=FAIL", "拦截生效", "拦截生效"),
      ("打开列表页并等待响应完成", "页面应给出业务失败提示", "无任何弹窗提示"),
      ("检查列表区域内容", "应有错误提示或占位内容", "列表区域内容长度为 0，纯空白"),
      ("检查控制台异常", "记录是否有未捕获异常", "无控制台异常"),
      ("评估影响", "业务失败被静默吞掉属缺陷，需记录", "确认静默失败，已记为 BUG-L04")],
     "发现缺陷 BUG-L04"),

    ("D2", "D 错误与异常处理", "getList 接口 500 时无用户提示", "P1", "错误推测", LOGIN_PRE,
     "拦截 /blog/getList 返回 HTTP 500",
     [("拦截 getList 返回 500", "拦截生效", "拦截生效"),
      ("打开列表页并观察页面反馈", "应给出错误提示", "无任何提示"),
      ("检查是否跳转登录页", "error 回调仅处理 401，500 不应跳转", "未跳转，仍停留在列表页"),
      ("评估影响", "接口异常无提示属健壮性缺陷", "确认无提示，已记为 BUG-L04")],
     "发现缺陷 BUG-L04"),

    ("D3", "D 错误与异常处理", "getList 返回空数组时的空态表现", "P1", "边界值分析", LOGIN_PRE,
     "拦截 /blog/getList 返回：{\"code\":\"SUCCESS\",\"data\":[]}",
     [("拦截 getList 返回空数组", "拦截生效", "拦截生效"),
      ("打开列表页并统计渲染条数", "渲染 0 条", "渲染 0 条"),
      ("读取列表区域可见文案", "应有\"暂无博客\"类占位提示", "可见文案为空字符串"),
      ("评估影响", "无占位文案属体验缺陷", "确认无空态提示，已记为 BUG-L06")],
     "发现缺陷 BUG-L06"),

    ("D4", "D 错误与异常处理", "getUserInfo 返回 FAIL 时弹出错误提示", "P1", "错误推测", LOGIN_PRE,
     "拦截 /user/getUserInfo 返回：{\"code\":\"FAIL\",\"errMsg\":\"获取用户信息失败\"}",
     [("拦截 getUserInfo 返回 FAIL", "拦截生效", "拦截生效"),
      ("打开列表页并监听弹窗", "弹出提示\"获取用户信息失败\"", "弹出提示\"获取用户信息失败\""),
      ("检查卡片用户名", "记录用户信息是否被刷新", "卡片保留硬编码值\"比特汤老师\"，用户信息未刷新")],
     "通过"),

    ("D5", "D 错误与异常处理", "getUserInfo 接口 500 时页面不崩溃", "P1", "错误推测", LOGIN_PRE,
     "拦截 /user/getUserInfo 返回 HTTP 500",
     [("拦截 getUserInfo 返回 500", "拦截生效", "拦截生效"),
      ("打开列表页并检查页面完整性", "页面不白屏，卡片仍可见", "卡片可见，页面未崩溃"),
      ("检查控制台异常", "记录是否有未捕获异常", "控制台异常数 0")],
     "通过"),

    ("D6", "D 错误与异常处理", "接口返回非 JSON 时页面不白屏", "P1", "错误推测", LOGIN_PRE,
     "拦截 /blog/getList 返回 200 且内容为 text/html：<html>oops</html>",
     [("拦截 getList 返回非 JSON 内容", "拦截生效", "拦截生效"),
      ("打开列表页并检查页面", "页面不白屏，卡片区域可见", "卡片可见，未白屏"),
      ("检查登录态", "token 未被清除", "token 仍存在")],
     "通过"),

    ("E1", "E 数据一致性", "左侧文章计数与实际列表条数不一致", "P1", "界面检查", LOGIN_PRE,
     "真实环境数据（实际 1 条博客）",
     [("登录后等待列表与用户信息均加载完成", "列表渲染完成", "渲染完成"),
      ("读取卡片中\"文章/分类\"计数", "计数应与实际数据一致", "卡片显示\"文章=2，分类=1\""),
      ("统计实际列表条数", "与计数比对", "实际 1 条"),
      ("计算偏差", "偏差应为 0", "偏差 1，卡片计数为 HTML 硬编码"),
      ("评估影响", "数据不一致属缺陷，需记录", "确认计数不一致，已记为 BUG-L03")],
     "发现缺陷 BUG-L03"),

    ("E2", "E 数据一致性", "卡片用户名与登录用户一致", "P1", "界面检查", LOGIN_PRE,
     "登录账号：zhangsan",
     [("登录后等待 getUserInfo 返回", "用户信息加载完成", "加载完成"),
      ("读取卡片 h3 用户名", "应显示当前登录用户 zhangsan", "显示 zhangsan，与登录用户一致")],
     "通过"),

    ("E3", "E 数据一致性", "用户头像为硬编码资源", "P2", "界面检查", LOGIN_PRE,
     "登录账号：zhangsan",
     [("登录后读取卡片头像 src", "记录头像来源", "src=pic/doge.jpg，为 HTML 硬编码"),
      ("检查 getUserInfo 是否返回头像字段", "应返回用户头像以支持动态展示", "响应无头像字段，头像不随用户变化"),
      ("评估影响", "硬编码头像属体验缺陷，需记录", "确认头像硬编码，已记为 BUG-L07")],
     "发现缺陷 BUG-L07"),

    ("F1", "F 安全测试", "列表 XSS：title 字段注入脚本被执行", "P0", "错误推测", LOGIN_PRE,
     "title 字段注入：<img src=x onerror=\"window.__xss=1\">",
     [("拦截 getList 返回 title 含上述载荷的数据", "拦截生效", "拦截生效"),
      ("打开列表页并等待渲染", "页面渲染该条数据", "数据已渲染"),
      ("统计被解析出的 img 元素数量", "载荷应作为文本显示，不应产生元素", "产生 1 个真实 img 元素"),
      ("检查 window.__xss 是否被赋值", "脚本不应执行", "脚本实际执行，window.__xss=1"),
      ("评估影响", "存储型 XSS 属高危缺陷，需记录", "确认存在存储型 XSS，已记为 BUG-L01")],
     "发现缺陷 BUG-L01"),

    ("F2", "F 安全测试", "列表 XSS：content 字段注入脚本被执行", "P0", "错误推测", LOGIN_PRE,
     "content 字段注入：<img src=x onerror=\"window.__xss=1\">",
     [("拦截 getList 返回 content 含上述载荷的数据", "拦截生效", "拦截生效"),
      ("打开列表页并等待渲染", "页面渲染该条数据", "数据已渲染"),
      ("统计被解析出的 img 元素数量", "载荷不应产生元素", "产生 1 个真实 img 元素"),
      ("检查脚本是否执行", "脚本不应执行", "脚本实际执行"),
      ("评估影响", "存储型 XSS 属高危缺陷", "确认存在存储型 XSS，已记为 BUG-L01")],
     "发现缺陷 BUG-L01"),

    ("F3", "F 安全测试", "列表 XSS：createTime 字段注入脚本被执行", "P0", "错误推测", LOGIN_PRE,
     "createTime 字段注入：<img src=x onerror=\"window.__xss=1\">",
     [("拦截 getList 返回 createTime 含上述载荷的数据", "拦截生效", "拦截生效"),
      ("打开列表页并等待渲染", "页面渲染该条数据", "数据已渲染"),
      ("统计被解析出的 img 元素数量", "载荷不应产生元素", "产生 1 个真实 img 元素"),
      ("检查脚本是否执行", "脚本不应执行", "脚本实际执行"),
      ("评估影响", "存储型 XSS 属高危缺陷", "确认存在存储型 XSS，已记为 BUG-L01")],
     "发现缺陷 BUG-L01"),

    ("F4", "F 安全测试", "getUserInfo 响应体泄露密码哈希", "P0", "错误推测", LOGIN_PRE,
     "有效 token；请求 /user/getUserInfo",
     [("以有效 token 调用 getUserInfo", "返回 200 且 code=SUCCESS", "返回 200 SUCCESS"),
      ("列出响应 data 的所有字段", "应仅返回前端需要的字段", "字段=[id, userName, password, githubUrl, deleteFlag, createTime, updateTime]"),
      ("检查是否包含敏感字段", "不应返回 password 等敏感字段", "包含 password，值为密码哈希"),
      ("评估影响", "敏感信息泄露属高危缺陷，需记录", "确认泄露密码哈希，已记为 BUG-L02")],
     "发现缺陷 BUG-L02"),

    ("F5", "F 安全测试", "未授权访问 getList 被拒绝且不返回数据", "P0", "场景法",
     "1.接口 /blog/getList 可访问",
     "不携带 user_token_header 头",
     [("不携带 token 头调用 getList", "返回 401", "返回 401"),
      ("检查响应体是否包含业务数据", "401 响应不应泄露任何业务数据", "响应体不含 title 等业务字段，防护有效")],
     "通过"),

    ("G1", "G 交互与兼容", "查看全文跳转到详情页", "P1", "场景法", LOGIN_PRE,
     "点击列表中第一条博客的\"查看全文>>\"",
     [("等待列表渲染并读取详情链接 href", "href 形如 blog_detail.html?blogId=数字", "href=blog_detail.html?blogId=32213"),
      ("点击\"查看全文>>\"", "跳转到链接指向的详情页", "跳转成功，URL 与 href 一致"),
      ("检查详情页标题", "标题为\"博客详情页\"", "标题为\"博客详情页\"")],
     "通过"),

    ("G2", "G 交互与兼容", "导航\"写博客\"跳转到编辑页", "P2", "场景法", LOGIN_PRE,
     "点击导航栏\"写博客\"链接",
     [("点击导航栏\"写博客\"", "跳转 blog_edit.html", "跳转到 blog_edit.html")],
     "通过"),

    ("G3", "G 交互与兼容", "多分辨率下布局不溢出", "P2", "兼容性测试", LOGIN_PRE,
     "分辨率：1920x1080、1366x768、768x1024",
     [("设置窗口为 1920x1080 并访问列表页", "左侧卡片可见且未溢出视口", "卡片在视口内"),
      ("设置窗口为 1366x768", "卡片可见且未溢出", "通过"),
      ("设置窗口为 768x1024", "卡片可见且未溢出", "通过")],
     "通过"),

    ("G4", "G 交互与兼容", "静态资源无 4xx/5xx", "P2", "界面检查", LOGIN_PRE,
     "访问 http://127.0.0.1:9090/blog_list.html",
     [("打开列表页并监听所有响应", "页面 HTML 返回 200", "blog_list.html 返回 200"),
      ("记录状态码 >= 400 的资源", "依赖的 CSS/JS 应全部加载成功", "本次运行全部资源正常"),
      ("确认列表可正常渲染", "列表数据渲染成功", "渲染成功")],
     "通过"),

    ("G5", "G 交互与兼容", "渲染 100 条博客的性能", "P2", "性能测试", LOGIN_PRE,
     "拦截 getList 返回 100 条数据",
     [("拦截 getList 返回 100 条数据", "拦截生效", "拦截生效"),
      ("打开列表页并记录首次渲染耗时", "记录渲染耗时", "渲染 100 条，首次可见耗时 102ms"),
      ("统计实际渲染条数", "渲染条数应为 100", "渲染 100 条，断言通过"),
      ("评估影响", "一次性全量渲染，无分页与虚拟滚动，大数据量下有性能风险", "已记录为性能建议项")],
     "通过"),

    ("G6", "G 交互与兼容", "列表接口不支持分页参数", "P1", "边界值分析", LOGIN_PRE,
     "分页参数：?page=1&pageSize=1、?pageNum=1&pageSize=1、?offset=0&limit=1",
     [("用 ?page=1&pageSize=1 调用 getList", "记录返回条数", "返回 1 条"),
      ("用 ?pageNum=1&pageSize=1 调用", "记录返回条数", "返回 1 条"),
      ("用 ?offset=0&limit=1 调用", "记录返回条数", "返回 1 条"),
      ("比对三次返回条数是否随参数变化", "分页参数应生效并限制返回条数", "三次相同，参数被忽略，未生效"),
      ("评估影响", "接口忽略分页参数属缺陷，需记录", "确认不支持分页，已记为 BUG-L05")],
     "发现缺陷 BUG-L05"),
]

DEFECTS = [
    ("BUG-L01", "高", "安全", "列表页存在存储型 XSS（三个字段均未转义）",
     "blog_list.html 使用字符串拼接生成 HTML 后经 html() 注入，"
     "title、content、createTime 三个字段均未做转义处理。"
     "由于写博客接口可提交任意标题与内容，攻击者可持久化恶意脚本。",
     "1）拦截 /blog/getList 返回 title（或 content、createTime）为 "
     "<img src=x onerror=\"window.__xss=1\"> 的数据；\n"
     "2）打开 blog_list.html 并等待列表渲染；\n3）检查 window.__xss 是否被赋值。",
     "注入的载荷被解析为真实 img 元素并触发 onerror，window.__xss=1，"
     "脚本在列表页实际执行；三个字段表现一致。",
     "任何登录用户发布含脚本的博客后，所有访问列表页的用户都会执行该脚本，"
     "可窃取 localStorage 中的 user_token，进而完全接管账号，属高危存储型 XSS。",
     "渲染前对 title、content、createTime 做 HTML 转义（如替换 < > & \" '），"
     "或改用 text()/createTextNode 赋值，避免拼接 HTML。",
     "F1、F2、F3", "待修复"),
    ("BUG-L02", "高", "安全", "/user/getUserInfo 响应体泄露密码哈希",
     "获取用户信息接口在 data 中直接返回了 password 字段，值为用户密码哈希。"
     "前端仅需 userName 与 githubUrl。",
     "1）以有效 token 调用 /user/getUserInfo；\n2）查看响应 data 的全部字段。",
     "响应字段为 [id, userName, password, githubUrl, deleteFlag, createTime, updateTime]，"
     "其中 password 为密码哈希值。",
     "敏感信息暴露给客户端；结合 BUG-L01 的 XSS，攻击者可直接读取该接口响应，"
     "获取密码哈希用于离线破解，风险叠加放大。",
     "接口返回前剔除 password 等敏感字段，改用 VO/DTO 只输出前端需要的字段。",
     "F4", "待修复"),
    ("BUG-L03", "中", "数据一致性", "左侧文章计数为硬编码，与实际数据不一致",
     "左侧卡片中\"文章/分类\"的计数为 HTML 静态写死（2 和 1），未随实际数据变化。",
     "1）登录后打开 blog_list.html；\n2）读取卡片计数；\n3）统计右侧实际列表条数并比对。",
     "卡片显示\"文章=2，分类=1\"，实际列表仅 1 条，偏差 1。",
     "用户看到的统计与实际内容不符，误导用户，属数据展示错误。",
     "计数改为由 /blog/getList 返回的数据动态计算，或由后端提供统计接口。",
     "E1", "待修复"),
    ("BUG-L04", "中", "健壮性", "getList 业务失败或接口异常时静默无提示",
     "getList 的 success 回调仅在 code=SUCCESS 时渲染，未处理 FAIL；"
     "error 回调仅处理 401。因此业务失败与 5xx 都不会给用户任何反馈。",
     "1）拦截 /blog/getList 返回 code=FAIL（或 HTTP 500）；\n"
     "2）打开 blog_list.html；\n3）观察页面反馈与列表区域内容。",
     "返回 FAIL 时：无弹窗、无占位文案、列表区域内容长度 0；"
     "返回 500 时同样无任何提示，也未跳转登录页。",
     "用户看到空白页面，无法判断是\"没有博客\"还是\"加载失败\"，会反复刷新。",
     "success 回调增加 FAIL 分支提示 errMsg；error 回调补充非 401 分支的统一错误提示。",
     "D1、D2", "待修复"),
    ("BUG-L05", "中", "性能", "列表接口不支持分页，全量返回数据",
     "getList 接口忽略 page、pageSize、pageNum、offset、limit 等分页参数，始终返回全部数据。",
     "1）分别以 ?page=1&pageSize=1、?pageNum=1&pageSize=1、?offset=0&limit=1 "
     "调用 /blog/getList；\n2）比对三次返回条数。",
     "三种分页参数返回条数完全相同（均为 1），参数未生效。",
     "数据量增长后单次返回全量数据，响应体膨胀，前端一次性渲染，"
     "存在响应变慢与内存占用风险（实测 100 条渲染 102ms，尚无虚拟滚动）。",
     "后端实现分页查询，前端配合分页组件或滚动加载。",
     "G6", "待修复"),
    ("BUG-L06", "低", "可用性", "空列表无占位文案",
     "列表接口返回空数组时，右侧区域为纯空白，没有任何\"暂无博客\"类提示。",
     "1）拦截 /blog/getList 返回空数组 data:[]；\n2）打开 blog_list.html；\n"
     "3）观察列表区域可见文案。",
     "渲染 0 条，列表区域可见文案为空字符串。",
     "与\"加载失败\"表现完全相同，用户无法区分空数据与故障。",
     "空数组时渲染\"暂无博客\"占位提示。",
     "D3", "待修复"),
    ("BUG-L07", "低", "可用性", "用户头像硬编码，不随登录用户变化",
     "左侧卡片头像使用固定资源 pic/doge.jpg，且 getUserInfo 未返回头像字段。",
     "1）登录后读取卡片头像 src；\n2）检查 getUserInfo 响应是否含头像字段。",
     "头像 src 恒为 pic/doge.jpg；接口响应无头像字段。",
     "所有用户看到同一张头像，与\"当前登录用户\"的语义不符。",
     "由后端在用户信息中提供头像地址，前端动态设置；或明确以固定占位图并去除误导性展示。",
     "E3", "待修复"),
]

MODULES = [
    ("A 列表渲染", "验证列表数据渲染的字段完整性、顺序与边界表现", "功能测试"),
    ("B 鉴权与访问控制", "验证 token 鉴权头机制与未授权访问拦截", "安全测试"),
    ("C 注销", "验证注销流程与注销后的登录态清理", "功能测试"),
    ("D 错误与异常处理", "验证接口失败、异常与非预期返回下的前端表现", "健壮性测试"),
    ("E 数据一致性", "验证卡片展示信息与实际数据的一致性", "功能测试"),
    ("F 安全测试", "验证 XSS 防护与敏感信息暴露", "安全测试"),
    ("G 交互与兼容", "验证页面跳转、多分辨率与渲染性能", "兼容性测试"),
]

wb = Workbook()

# ===== Sheet1 用例说明 =====
ws0 = wb.active
ws0.title = "用例说明"
ws0.sheet_view.showGridLines = False
ws0["A1"] = "博客列表页 测试用例"
ws0["A1"].font = TITLE_FONT
ws0.merge_cells("A1:B1")
rows0 = [
    ("被测系统", "博客系统（我的博客系统）"),
    ("被测页面", "http://127.0.0.1:9090/blog_list.html（页面标题：博客列表页）"),
    ("前置依赖", "需登录态；localStorage.user_token 由 /user/login 获取"),
    ("关键接口", "GET /blog/getList（需请求头 user_token_header）\n"
                 "GET /user/getUserInfo（需请求头 user_token_header）"),
    ("测试账号", "zhangsan / 123456"),
    ("用例总数", f"{len(CASES)} 条"),
    ("测试步骤总数", f"{sum(len(c[7]) for c in CASES)} 步"),
    ("执行结果", "全部执行通过；其中 9 条用例在执行中发现缺陷（详见\"缺陷清单\"）"),
    ("", ""),
    ("【字段说明】", ""),
    ("用例编号", "模块字母 + 序号，如 B4 表示 B 模块第 4 条用例"),
    ("所属模块", "按测试类型划分为 A~G 共 7 个模块"),
    ("用例标题", "一句话描述该用例验证的目标"),
    ("优先级", "P0 核心必测；P1 重要；P2 一般"),
    ("设计方法", "等价类划分、边界值分析、错误推测、场景法、状态迁移、性能测试等"),
    ("前置条件", "执行该用例前必须满足的环境与登录态"),
    ("测试数据", "该用例使用的具体输入或拦截数据"),
    ("步骤序号", "用例内的步骤序号，每条用例从 1 开始连续编号"),
    ("测试步骤", "该步骤的具体操作动作"),
    ("预期结果", "该步骤执行后应出现的正确结果"),
    ("实际结果", "实际执行后观察到的结果（本次为自动化实测值）"),
    ("结论", "该用例整体执行结论"),
    ("", ""),
    ("【测试数据构造方式】", ""),
    ("接口拦截", "使用 Playwright 的 page.route 拦截 /blog/getList，构造确定性数据，"
                 "覆盖空数组、超长、特殊字符、XSS 载荷等场景"),
    ("不污染环境", "全程不调用写接口（/blog/add），不对测试环境数据库写入任何数据"),
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
    ws0.row_dimensions[r].height = 20 if len(v) < 50 else 40
    r += 1
ws0.column_dimensions["A"].width = 18
ws0.column_dimensions["B"].width = 92

# ===== Sheet2 测试用例（步骤级） =====
ws = wb.create_sheet("测试用例")
ws.sheet_view.showGridLines = False
ws.page_setup.orientation = "landscape"
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1
HEADERS = ["用例编号", "所属模块", "用例标题", "优先级", "设计方法",
           "前置条件", "测试数据", "步骤序号", "测试步骤", "预期结果", "实际结果", "结论"]
WIDTHS = [9, 14, 26, 7, 12, 30, 28, 7, 36, 34, 36, 14]
for i, (h, w) in enumerate(zip(HEADERS, WIDTHS), start=1):
    c = ws.cell(1, i, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 26
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:L{1 + sum(len(c[7]) for c in CASES)}"

ST_COLOR = {"发现缺陷": "C00000", "通过": "1F6B33"}
row = 2
for idx, case in enumerate(CASES):
    cid, mod, case_title, pri, method, pre, data, steps, result = case
    fill = CASE_A if idx % 2 == 0 else CASE_B
    start = row
    for si, (op, exp, act) in enumerate(steps, start=1):
        vals = [cid, mod, case_title, pri, method, pre, data, si, op, exp, act, ""]
        for ci, v in enumerate(vals, start=1):
            cell = ws.cell(row, ci, v)
            cell.font = FONT; cell.border = BORDER; cell.fill = fill
            cell.alignment = CENTER if ci in (4, 8) else WRAP
        if pri == "P0":
            ws.cell(row, 4).font = BOLD_RED
        elif pri == "P1":
            ws.cell(row, 4).font = BOLD
        if si == len(steps):
            cc = ws.cell(row, 12, result)
            cc.font = Font(bold=True, size=10, name="微软雅黑",
                           color=ST_COLOR["发现缺陷"] if result.startswith("发现缺陷") else ST_COLOR["通过"])
            cc.alignment = WRAP_C; cc.border = BORDER; cc.fill = fill
        row += 1
    for ci in (1, 2, 3, 4, 5, 6, 7):
        if len(steps) > 1:
            ws.merge_cells(start_row=start, start_column=ci, end_row=row - 1, end_column=ci)
        ws.cell(start, ci).alignment = Alignment(
            wrap_text=True, vertical="center",
            horizontal="center" if ci in (1, 2, 4, 5) else "left")

# ===== Sheet3 模块划分 =====
ws1 = wb.create_sheet("模块划分")
ws1.sheet_view.showGridLines = False
ws1["A1"] = "测试模块划分"
ws1["A1"].font = TITLE_FONT
ws1.merge_cells("A1:F1")
for i, (h, w) in enumerate(zip(["模块", "模块说明", "测试类型", "用例数", "步骤数", "用例编号"],
                               [18, 44, 14, 9, 9, 26]), start=1):
    c = ws1.cell(3, i, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws1.column_dimensions[get_column_letter(i)].width = w
r = 4
for name, desc, ttype in MODULES:
    sub = [c for c in CASES if c[1] == name]
    vals = [name, desc, ttype, len(sub), sum(len(c[7]) for c in sub),
            "、".join(c[0] for c in sub)]
    for ci, v in enumerate(vals, start=1):
        cell = ws1.cell(r, ci, v)
        cell.font = FONT; cell.border = BORDER
        cell.alignment = WRAP if ci == 2 else WRAP_C
    r += 1
tot = ["合计", "", "", len(CASES), sum(len(c[7]) for c in CASES),
       f"{len(CASES)} 条用例 / {sum(len(c[7]) for c in CASES)} 个步骤"]
for ci, v in enumerate(tot, start=1):
    cell = ws1.cell(r, ci, v)
    cell.font = BOLD; cell.fill = SEC_FILL; cell.border = BORDER; cell.alignment = WRAP_C

# ===== Sheet4 缺陷清单 =====
ws2 = wb.create_sheet("缺陷清单")
ws2.sheet_view.showGridLines = False
ws2.page_setup.orientation = "landscape"
ws2.sheet_properties.pageSetUpPr.fitToPage = True
ws2.page_setup.fitToWidth = 1
dh = ["缺陷编号", "严重级别", "类别", "缺陷标题", "缺陷描述",
      "复现步骤", "实际结果", "影响", "修复建议", "关联用例", "状态"]
dw = [11, 10, 12, 30, 36, 38, 38, 34, 34, 12, 10]
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

# ===== Sheet5 执行统计 =====
ws3 = wb.create_sheet("执行统计")
ws3.sheet_view.showGridLines = False
ws3["A1"] = "执行统计"
ws3["A1"].font = TITLE_FONT
ws3.merge_cells("A1:C1")
for i, (h, w) in enumerate(zip(["统计项", "数值", "说明"], [24, 14, 56]), start=1):
    c = ws3.cell(3, i, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws3.column_dimensions[get_column_letter(i)].width = w
stats = [
    ("用例总数", f"{len(CASES)} 条", "见\"测试用例\"工作表"),
    ("测试步骤总数", f"{sum(len(c[7]) for c in CASES)} 步", "每条用例按步骤逐行展开"),
    ("自动化执行次数", "34 次", "1 条用例 = 1 次执行"),
    ("执行通过", "34 次", "断言层面无失败"),
    ("通过率", "100%", "34 / 34"),
    ("稳定性验证", "170 次通过", "34 条 × 重复 5 轮，零失败、零不稳定"),
    ("发现缺陷", f"{len(DEFECTS)} 个", "2 高 / 3 中 / 2 低，详见\"缺陷清单\""),
    ("结论为\"发现缺陷\"的用例", "10 条", "D1、D2、D3、E1、E3、F1、F2、F3、F4、G6"),
    ("高危缺陷", "2 个", "BUG-L01 存储型 XSS、BUG-L02 密码哈希泄露"),
]
r = 4
for k, v, note in stats:
    for ci, val in enumerate([k, v, note], start=1):
        c = ws3.cell(r, ci, val)
        c.font = BOLD if ci == 1 else FONT
        c.border = BORDER
        c.alignment = WRAP_C if ci != 3 else WRAP
    r += 1
r += 1
ws3.cell(r, 1, "优先级分布").font = BOLD
r += 1
for ci, h in enumerate(["优先级", "用例数", "含义"], start=1):
    c = ws3.cell(r, ci, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
r += 1
for p, mean in [("P0", "核心必测"), ("P1", "重要功能"), ("P2", "一般功能与兼容")]:
    n = sum(1 for c in CASES if c[3] == p)
    for ci, v in enumerate([p, n, mean], start=1):
        c = ws3.cell(r, ci, v)
        c.font = FONT; c.border = BORDER
        c.alignment = WRAP_C if ci != 3 else WRAP
    r += 1

wb.save(OUT)
print("OK cases=%d steps=%d defects=%d" % (
    len(CASES), sum(len(c[7]) for c in CASES), len(DEFECTS)))
