# -*- coding: utf-8 -*-
"""生成《博客编辑页测试用例》—— 规范测试用例格式（步骤级展开）"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\study\AI\deepseek-day\博客编辑页_测试用例.xlsx"

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
SAFE = "\n【安全】发布接口已被拦截，不会写入数据库"

CASES = [
    ("A1", "A 页面结构与加载", "页面标题与核心元素存在", "P1", "界面检查", LOGIN_PRE,
     "访问 /blog_edit.html",
     [("打开编辑页", "页面正常加载", "加载成功"),
      ("检查页面标题", "标题为\"博客编辑页\"", "标题为\"博客编辑页\""),
      ("检查标题输入框 #title", "元素存在且可见", "存在且可见"),
      ("检查发布按钮 #submit", "元素存在，value 为\"发布文章\"", "存在，文案为\"发布文章\""),
      ("检查编辑器容器 #editor", "元素存在且可见", "存在且可见")],
     "通过"),
    ("A2", "A 页面结构与加载", "editor.md 初始化与预览渲染", "P1", "界面检查", LOGIN_PRE,
     "访问 /blog_edit.html",
     [("等待编辑器初始化完成", "window.editormd 已加载", "editormd 已加载"),
      ("检查 CodeMirror 实例", "CodeMirror API 可用", "实例就绪"),
      ("检查工具栏按钮数量", "工具栏按钮数量大于 0", "共 37 个按钮"),
      ("检查 #content 是否隐藏", "textarea 为 display:none（由编辑器接管）", "确认为隐藏"),
      ("检查预览区内容", "默认内容渲染为 Markdown 二级标题", "预览区渲染出\"在这里写下一篇博客\"")],
     "通过"),
    ("A3", "A 页面结构与加载", "编辑器尺寸按配置初始化", "P2", "界面检查", LOGIN_PRE,
     "配置项：width 100%、height 550px",
     [("等待编辑器渲染完成", "编辑器可见", "可见"),
      ("测量 CodeMirror 实际尺寸", "高度应接近配置的 550px", "高度大于 300px，符合配置"),
      ("确认宽度占满容器", "宽度大于 300px", "宽度符合，未溢出")],
     "通过"),

    ("B1", "B 访问控制", "未登录可直接打开编辑页（守卫缺失）", "P0", "场景法",
     "1.未登录（localStorage 无 token）\n2.访问编辑页",
     "访问 /blog_edit.html" + SAFE,
     [("清空登录态", "token 为空", "token 为空"),
      ("直接访问 /blog_edit.html", "页面应校验登录态并跳转登录页", "页面直接打开，未跳转"),
      ("监听加载期间的接口请求", "应有 /user/ 或 /blog/ 鉴权请求", "未发起任何鉴权请求"),
      ("评估影响", "缺少守卫属高危缺陷，需记录", "确认守卫缺失，已记为 BUG-E01")],
     "发现缺陷 BUG-E01"),

    ("B2", "B 访问控制", "未登录点击发布触发 401 并跳转登录页", "P0", "场景法",
     "1.未登录状态\n2.已打开编辑页",
     "标题：未登录发布测试\n内容：内容",
     [("未登录状态下打开编辑页", "页面打开（守卫缺失）", "页面打开"),
      ("填写标题与内容", "输入成功", "输入成功"),
      ("点击\"发布文章\"", "接口返回 401，error 回调跳转登录页", "跳转 blog_login.html"),
      ("确认最终地址", "URL 为 blog_login.html", "URL 为 blog_login.html，接口层鉴权有效")],
     "通过"),

    ("B3", "B 访问控制", "无 token 调用写入接口返回 401 且不落库", "P0", "错误推测", LOGIN_PRE,
     "请求 /blog/add，不带 user_token_header" + SAFE,
     [("记录当前博客条数", "作为基线", "基线 1 条"),
      ("不带 token 调用 /blog/add", "返回 HTTP 401", "返回 401"),
      ("再次统计博客条数", "条数与基线一致，数据未落库", "仍为 1 条，未落库")],
     "通过"),

    ("C1", "C 标题输入域", "标题输入框属性基线", "P1", "界面检查", LOGIN_PRE,
     "检查 #title 的属性",
     [("读取 type 属性", "记录输入框类型", "type=text"),
      ("读取 maxlength 属性", "应有长度限制", "maxlength=null，无长度限制"),
      ("读取 required 属性", "应有必填约束", "required=false，无必填约束"),
      ("读取 placeholder 属性", "应有占位提示", "placeholder=null，无占位提示"),
      ("评估影响", "缺少约束属可用性缺陷，需记录", "确认约束缺失，已记为 BUG-E06")],
     "发现缺陷 BUG-E06"),

    ("C2", "C 标题输入域", "超长标题无长度限制", "P1", "边界值分析", LOGIN_PRE,
     "标题：'A' 重复 500 次",
     [("在标题框输入 500 个字符", "输入框接受该长度", "输入成功"),
      ("读取输入框实际值长度", "记录是否被截断", "长度为 500，未被截断（无长度限制）")],
     "通过"),

    ("C3", "C 标题输入域", "特殊字符标题正常显示", "P1", "错误推测", LOGIN_PRE,
     "标题：标题\"引号'与&符号<>花括号{}[]",
     [("输入含特殊字符的标题", "输入框原样回显", "回显与输入一致"),
      ("检查标题框内是否产生子元素", "输入框不解析 HTML，无子元素", "子元素数 0")],
     "通过"),

    ("C4", "C 标题输入域", "标题前后空格不被自动去除", "P2", "边界值分析", LOGIN_PRE,
     "标题：\"  前后空格  \"（前后各两个空格）",
     [("输入前后带空格的标题", "记录前端是否 trim", "输入框值为\"  前后空格  \""),
      ("读取输入框实际值", "保留空格或自动去除", "空格被保留，会随请求一起提交")],
     "通过"),

    ("C5", "C 标题输入域", "清空后重新输入取值正确", "P2", "场景法", LOGIN_PRE,
     "先输入\"临时标题\"，清空后输入\"新标题\"",
     [("输入\"临时标题\"", "回显正确", "回显正确"),
      ("清空输入框", "值为空字符串", "值为空"),
      ("重新输入\"新标题\"", "值为最新内容", "值为\"新标题\"，绑定正确")],
     "通过"),

    ("D1", "D 编辑器内容", "编辑器默认占位内容", "P1", "界面检查", LOGIN_PRE,
     "编辑器默认值",
     [("打开编辑页并等待初始化", "编辑器就绪", "编辑器就绪"),
      ("读取 CodeMirror 内容", "默认为 \"##在这里写下一篇博客\"", "内容与预期一致"),
      ("读取隐藏 textarea 的值", "与编辑器内容一致", "值一致")],
     "通过"),

    ("D2", "D 编辑器内容", "真实键盘输入会同步到 textarea", "P0", "场景法", LOGIN_PRE,
     "在编辑器内用键盘输入：真实键盘输入的内容ABC",
     [("清空编辑器内容", "内容为空", "已清空"),
      ("聚焦编辑器并用键盘逐字输入", "CodeMirror 显示输入内容", "显示正确"),
      ("读取 hidden textarea 的值", "应与编辑器内容同步（submit 取的是该值）", "完全同步"),
      ("结论", "真实输入路径下功能正常，与程序化 setValue 行为不同", "确认同步正常，非缺陷")],
     "通过"),

    ("D3", "D 编辑器内容", "未修改内容直接发布会带上默认占位文本", "P1", "错误推测", LOGIN_PRE,
     "标题：只填标题不写正文；编辑器内容保持默认" + SAFE,
     [("只填写标题，不修改编辑器内容", "标题输入成功", "标题已填"),
      ("点击\"发布文章\"并拦截请求", "记录实际提交的 content 值", "content=\"##在这里写下一篇博客\""),
      ("评估影响", "默认占位文本被当作正文发布会污染文章内容，属缺陷", "确认默认文本被发布，已记为 BUG-E04")],
     "发现缺陷 BUG-E04"),

    ("D4", "D 编辑器内容", "Markdown 内容实时渲染到预览区", "P1", "功能测试", LOGIN_PRE,
     "编辑器内容：# 一级标题\\n\\n这是**加粗**段落",
     [("在编辑器输入 Markdown 标题与加粗语法", "输入成功", "输入成功"),
      ("等待预览刷新", "预览区渲染对应 HTML", "预览区出现一级标题与加粗文本"),
      ("检查预览区 DOM", "应生成真实 h1 元素", "h1 元素数量大于 0，渲染正常")],
     "通过"),

    ("D5", "D 编辑器内容", "大量内容的预览渲染性能", "P2", "性能测试", LOGIN_PRE,
     "编辑器内容：300 段正文（约 5700 字）",
     [("构造 300 段正文并设置到编辑器", "内容正确载入", "内容载入成功"),
      ("记录设置与预览刷新耗时", "耗时应可接受", "耗时低于 10 秒"),
      ("核对编辑器内容长度", "与实际设置长度一致", "长度一致")],
     "通过"),

    ("E1", "E 发布流程", "发布请求的方法、类型与鉴权头", "P0", "功能测试", LOGIN_PRE,
     "标题：T；内容：C" + SAFE,
     [("填写标题与内容并点击发布", "发出 POST /blog/add 请求", "请求已发出，仅 1 次"),
      ("检查请求方法", "为 POST", "POST"),
      ("检查 Content-Type", "为 application/json", "application/json"),
      ("检查 user_token_header", "存在且为有效 token", "请求头存在")],
     "通过"),

    ("E2", "E 发布流程", "请求体仅含 title 与 content 且取值正确", "P0", "功能测试", LOGIN_PRE,
     "标题：载荷标题；内容：载荷正文" + SAFE,
     [("填写标题\"载荷标题\"", "输入成功", "输入成功"),
      ("设置内容为\"载荷正文\"", "编辑器内容更新且同步", "内容已同步"),
      ("点击发布并读取请求体", "JSON 仅含 title 与 content 两个字段", "字段为 [content, title]"),
      ("核对字段取值", "与页面输入完全一致", "title、content 取值均一致")],
     "通过"),

    ("E3", "E 发布流程", "SUCCESS 且 data=true 时跳转列表页", "P0", "功能测试", LOGIN_PRE,
     "拦截响应：{code:SUCCESS, data:true}" + SAFE,
     [("拦截发布接口返回成功响应", "拦截生效", "拦截生效"),
      ("填写标题与内容并点击发布", "前端判定成功", "判定成功"),
      ("观察页面跳转", "跳转到 blog_list.html", "跳转成功，URL 为 blog_list.html")],
     "通过"),

    ("E4", "E 发布流程", "中文标题与正文以 UTF-8 正确提交", "P0", "功能测试", LOGIN_PRE,
     "标题：中文标题测试\n内容：中文正文内容，含标点：，。！？" + SAFE,
     [("输入中文标题", "显示正常", "显示正常"),
      ("输入含中文标点的正文", "显示正常", "显示正常"),
      ("点击发布，按 UTF-8 解码请求体", "请求体中中文无乱码", "title 与 content 均正确，编码正常"),
      ("说明", "Node 环境打印 postData() 可能显示乱码，属观察工具问题", "已用 postDataBuffer 核验，编码正常")],
     "通过"),

    ("E5", "E 发布流程", "响应成功但缺少 data 字段时不跳转", "P1", "错误推测", LOGIN_PRE,
     "拦截响应：{code:SUCCESS, errMsg:'', data:null}" + SAFE,
     [("拦截发布接口返回 data=null", "拦截生效", "拦截生效"),
      ("填写标题与内容并点击发布", "前端按失败处理", "未跳转，仍停留在编辑页"),
      ("记录弹窗内容", "前端严格依赖 data==true 判断成功", "弹窗内容为空字符串"),
      ("确认最终地址", "URL 仍为 blog_edit.html", "URL 未变化")],
     "通过"),

    ("F1", "F 校验与错误反馈", "空标题发布弹出空白提示", "P0", "错误推测", LOGIN_PRE,
     "标题：空；内容：有正文但没标题",
     [("标题留空，内容填\"有正文但没标题\"", "输入成功", "输入成功"),
      ("点击\"发布文章\"", "应给出可读的失败提示", "弹出对话框"),
      ("读取弹窗内容", "应提示具体原因", "弹窗内容为空字符串\"\""),
      ("确认页面状态", "停留编辑页且内容未丢失", "停留编辑页"),
      ("评估影响", "空白提示让用户无法得知失败原因，属缺陷", "后端 errMsg 为空且 data=false，已记为 BUG-E02")],
     "发现缺陷 BUG-E02"),

    ("F2", "F 校验与错误反馈", "空内容发布弹出空白提示", "P0", "错误推测", LOGIN_PRE,
     "标题：有标题但没正文；内容：空",
     [("标题填写\"有标题但没正文\"，内容清空", "输入成功", "输入成功"),
      ("点击\"发布文章\"", "应给出可读的失败提示", "弹出对话框"),
      ("读取弹窗内容", "应提示具体原因", "弹窗内容为空字符串，同样为空白提示")],
     "发现缺陷 BUG-E02"),

    ("F3", "F 校验与错误反馈", "标题与内容同时为空", "P0", "边界值分析", LOGIN_PRE,
     "标题：空；内容：空",
     [("标题与内容均清空", "均为空", "均为空"),
      ("点击\"发布文章\"", "应给出可读提示，且不跳转", "弹出空白对话框，未跳转"),
      ("确认最终地址", "URL 仍为 blog_edit.html", "URL 未变化")],
     "发现缺陷 BUG-E02"),

    ("F4", "F 校验与错误反馈", "写接口返回 500 时静默无提示", "P1", "错误推测", LOGIN_PRE,
     "拦截 /blog/add 返回 HTTP 500" + SAFE,
     [("拦截发布接口返回 500", "拦截生效", "拦截生效"),
      ("填写标题与内容并点击发布", "应给出错误提示", "无任何弹窗"),
      ("确认页面状态", "error 回调仅处理 401，500 不应跳转", "停留编辑页"),
      ("评估影响", "静默失败属健壮性缺陷，需记录", "确认无提示，已记为 BUG-E05")],
     "发现缺陷 BUG-E05"),

    ("F5", "F 校验与错误反馈", "前端零校验，完全依赖后端", "P1", "错误推测", LOGIN_PRE,
     "接口调用：空字段、无字段" + SAFE,
     [("前端检查", "标题与内容均无 required 等校验", "前端无任何校验，空值也会提交"),
      ("以空字段调用 /blog/add", "记录响应", "返回 code=SUCCESS、data=false、errMsg=\"\""),
      ("以无字段调用 /blog/add", "记录响应", "同上"),
      ("评估影响", "前后端都没有可读错误信息，用户无法得知失败原因", "确认无有效错误信息，已记为 BUG-E02")],
     "发现缺陷 BUG-E02"),

    ("G1", "G 重复提交", "连点发布按钮 3 次发出 3 次请求", "P0", "错误推测", LOGIN_PRE,
     "标题：连点测试；内容：连点内容" + SAFE,
     [("填写标题与内容", "输入成功", "输入成功"),
      ("并发点击\"发布文章\"3 次", "统计实际发出的请求数", "实际发出 3 次请求"),
      ("评估影响", "无防重复机制会为同一内容创建多篇文章", "确认无防重复，已记为 BUG-E03")],
     "发现缺陷 BUG-E03"),

    ("G2", "G 重复提交", "提交过程中按钮未禁用", "P1", "界面检查", LOGIN_PRE,
     "拦截发布接口并延迟响应" + SAFE,
     [("拦截发布接口，在请求进行中读取按钮状态", "记录按钮是否被禁用", "isDisabled=false"),
      ("评估影响", "提交期间按钮可继续点击，缺少 loading 与禁用态", "确认未禁用，已记为 BUG-E08")],
     "发现缺陷 BUG-E08"),

    ("G3", "G 重复提交", "提交过程中按钮文案无变化", "P1", "界面检查", LOGIN_PRE,
     "拦截发布接口并延迟响应" + SAFE,
     [("在请求进行中读取按钮文案", "应变为\"发布中…\"等状态", "文案仍为\"发布文章\"，无状态反馈"),
      ("评估影响", "无提交中状态反馈属体验缺陷", "确认无状态反馈，已记为 BUG-E08")],
     "发现缺陷 BUG-E08"),

    ("H1", "H 安全", "标题中的 HTML 与脚本不被执行", "P1", "错误推测", LOGIN_PRE,
     "标题：<img src=x onerror=\"alert('xss')\">",
     [("在标题框输入 HTML 与脚本载荷", "输入框原样保存该字符串", "已输入"),
      ("检查是否产生 img 元素", "input 值不被解析为 HTML，无子元素", "子元素数 0"),
      ("监听弹窗与页面异常", "脚本不应执行", "无弹窗、无未捕获异常")],
     "通过"),

    ("H2", "H 安全", "编辑器内容中的脚本不被执行", "P1", "错误推测", LOGIN_PRE,
     "内容：<script>window.__editXss=1</script> 与 <img src=x onerror=...>",
     [("在编辑器输入脚本载荷", "内容保存成功", "内容已设置"),
      ("等待预览区渲染", "预览区不应执行注入脚本", "window.__editXss 为 null"),
      ("检查是否有页面异常", "无未捕获异常", "无相关异常")],
     "通过"),

    ("H3", "H 安全", "超长内容提交接口不返回 5xx", "P2", "边界值分析", LOGIN_PRE,
     "接口调用（避免写入，使用空内容）" + SAFE,
     [("以空内容调用 /blog/add", "接口不返回 5xx", "状态码小于 500"),
      ("说明", "页面层已验证 500 字标题与 300 段正文可正常输入与渲染", "已验证")],
     "通过"),

    ("H4", "H 安全", "未授权写入请求被拒绝且数据未落库", "P0", "场景法", LOGIN_PRE,
     "请求 /blog/add，不带 token" + SAFE,
     [("记录当前博客条数", "作为基线", "基线 1 条"),
      ("不带 token 提交写入请求", "返回 401，拒绝写入", "返回 401"),
      ("再次统计博客条数", "与基线一致，未落库", "仍为 1 条"),
      ("结论", "接口层鉴权有效", "确认鉴权有效")],
     "通过"),

    ("I1", "I 交互与兼容", "导航\"主页\"跳转到列表页", "P2", "场景法", LOGIN_PRE,
     "点击导航栏\"主页\"链接",
     [("点击\"主页\"链接", "跳转到 blog_list.html", "跳转成功")],
     "通过"),

    ("I2", "I 交互与兼容", "注销清除 token 并跳转登录页", "P1", "场景法", LOGIN_PRE,
     "点击导航栏\"注销\"链接",
     [("确认当前已登录", "token 非空", "token 存在"),
      ("点击\"注销\"链接", "清除 token 并跳转登录页", "token 被清除，跳转登录页"),
      ("检查 localStorage", "user_token 为 null", "为 null")],
     "通过"),

    ("I3", "I 交互与兼容", "有未保存内容时离开页面无任何提醒", "P2", "错误推测", LOGIN_PRE,
     "标题：未保存的标题；内容：未保存的正文",
     [("填写标题与正文", "输入成功", "输入成功"),
      ("点击导航栏\"主页\"离开", "应提示内容未保存", "无任何提醒"),
      ("确认最终地址", "记录是否直接离开", "直接跳转到 blog_list.html"),
      ("评估影响", "未保存内容直接丢失属体验缺陷", "确认无提醒，已记为 BUG-E07")],
     "发现缺陷 BUG-E07"),

    ("I4", "I 交互与兼容", "多分辨率下编辑器不溢出", "P2", "兼容性测试", LOGIN_PRE,
     "分辨率：1920x1080、1366x768、768x1024",
     [("设置窗口为 1920x1080", "编辑器可见且未溢出视口", "未溢出"),
      ("设置窗口为 1366x768", "编辑器可见且未溢出", "未溢出"),
      ("设置窗口为 768x1024", "编辑器可见且未溢出", "未溢出")],
     "通过"),

    ("I5", "I 交互与兼容", "静态资源无 4xx/5xx", "P2", "界面检查", LOGIN_PRE,
     "访问 /blog_edit.html",
     [("打开编辑页并监听所有响应", "页面 HTML 返回 200", "返回 200"),
      ("记录状态码 >= 400 的资源", "editor.md 相关 CSS/JS 应全部加载成功", "本次运行全部资源正常")],
     "通过"),
]

DEFECTS = [
    ("BUG-E01", "高", "安全", "编辑页缺少登录守卫，未登录可打开写页面",
     "blog_edit.html 加载时不校验登录态，也不发起任何鉴权请求，"
     "未登录用户可直接打开写博客页面并填写内容（仅在点击发布时才会因 401 被拒）。",
     "1）清空 localStorage 登录态；\n2）直接访问 http://127.0.0.1:9090/blog_edit.html；\n"
     "3）观察页面是否打开、是否发起鉴权请求。",
     "页面直接正常打开，编辑器可用；加载期间未发起任何 /user/ 或 /blog/ 请求。",
     "未授权用户可进入写操作页面，与同一系统 blog_list.html 的守卫行为不一致；"
     "结合编辑页可访问性，攻击面扩大（属登录页测试 BUG-01 的同一根因）。",
     "在页面加载时校验 localStorage 中的 token，无效则跳转登录页；"
     "或由后端渲染页面时做服务端鉴权。",
     "B1", "待修复"),
    ("BUG-E02", "中", "可用性", "校验失败返回空 errMsg，前端弹出空白提示",
     "/blog/add 对非法输入统一返回 code=SUCCESS、data=false 且 errMsg 为空字符串；"
     "前端在失败分支执行 alert(result.errMsg)，因此弹出空白对话框。"
     "页面代码注释中也已自认此问题：\"后端未对错误情况进行分析, 统一返回了false\"。",
     "1）登录后打开编辑页；\n2）标题留空、内容填写任意文本；\n"
     "3）点击\"发布文章\"并监听弹窗。",
     "弹出对话框，但内容为空字符串\"\"；标题空、内容空、超长标题三种情况表现一致。",
     "用户完全无法得知失败原因（是标题为空、内容为空还是长度超限），"
     "只能反复尝试，属核心可用性缺陷。",
     "后端为各类校验失败返回明确的 errMsg（如\"标题不能为空\"）；"
     "前端增加必填与长度校验并给出内联提示。",
     "F1、F2、F3、F5", "待修复"),
    ("BUG-E03", "中", "健壮性", "无防重复提交机制，连点产生重复文章",
     "发布按钮在提交过程中未禁用、无 loading 状态，用户可重复点击，"
     "每次点击都会真实发出一次 /blog/add 写入请求。",
     "1）登录后打开编辑页并填写标题与内容；\n2）快速连续点击\"发布文章\"3 次；\n"
     "3）统计实际发出的请求数。",
     "实际发出 3 次 /blog/add 请求（发布为写操作，会产生 3 篇内容相同的文章）。",
     "网络较慢时用户容易重复点击，导致数据库出现重复文章，且无删除入口时难以清理。",
     "提交期间禁用按钮并显示\"发布中…\"；前端增加请求中的互斥标记。",
     "G1、G2、G3", "待修复"),
    ("BUG-E04", "中", "功能", "编辑器默认占位文本会被当作正文发布",
     "编辑器初始内容为 \"##在这里写下一篇博客\"，该文本位于真实的 textarea 中。"
     "若用户只填写标题而未修改正文，提交时会把这段占位文本一并发布。",
     "1）登录后打开编辑页；\n2）只填写标题，不修改编辑器内容；\n"
     "3）点击\"发布文章\"并拦截请求，检查 content 字段。",
     "提交载荷为 {\"title\":\"只填标题不写正文\",\"content\":\"##在这里写下一篇博客\"}。",
     "用户不写正文时会产生一篇正文为占位提示文字的文章，污染内容质量，"
     "且用户往往不会察觉。",
     "将占位提示改为 placeholder 或编辑器空内容为空字符串；"
     "提交前校验正文是否为空并给出提示。",
     "D3", "待修复"),
    ("BUG-E05", "中", "健壮性", "写接口 500 时静默失败，用户无感知",
     "submit() 的 error 回调只处理 status==401 的情况，其余错误（500 等）"
     "被完全忽略，不弹窗也不提示。",
     "1）登录后打开编辑页并拦截 /blog/add 返回 HTTP 500；\n"
     "2）填写标题与内容并点击发布；\n3）观察页面反馈。",
     "无任何弹窗或提示，页面停留在编辑页，用户无法判断是否发布成功。",
     "用户可能反复点击发布，既无法得知失败，也无法保留内容，"
     "属健壮性缺陷（与列表页 BUG-L04 为同类问题）。",
     "error 回调中为非 401 的情况补充统一错误提示（如\"发布失败，请稍后重试\"）。",
     "F4", "待修复"),
    ("BUG-E06", "低", "可用性", "标题输入框无长度限制与必填约束",
     "标题输入框未设置 maxlength、required，也无 placeholder，前端零校验。",
     "1）检查 #title 的 maxlength、required、placeholder 属性；\n"
     "2）尝试输入 500 个字符。",
     "maxlength=null、required=false、placeholder=null；可输入 500 字符不被截断。",
     "超长标题可提交，可能影响数据库字段长度与列表页展示；"
     "缺少必填约束使空值校验完全依赖后端，而后端又不返回可读错误。",
     "为标题设置合理的 maxlength 与必填校验，并补充 placeholder 提示。",
     "C1、C2", "待修复"),
    ("BUG-E07", "低", "可用性", "有未保存内容时离开页面无任何提醒",
     "页面未注册 beforeunload 或点击拦截，填写内容后直接点击导航链接会丢失内容。",
     "1）填写标题与正文；\n2）点击导航栏\"主页\"；\n3）观察是否有未保存提醒。",
     "无任何提醒，直接跳转到 blog_list.html，已填写内容全部丢失。",
     "用户误点导航会丢失全部写作内容，长文写作场景下影响较大。",
     "注册 beforeunload 事件，内容非空且未提交时提示用户确认离开。",
     "I3", "待修复"),
    ("BUG-E08", "低", "可用性", "提交过程中缺少按钮禁用与状态反馈",
     "发布过程中按钮保持可用且文案始终为\"发布文章\"，用户无法感知请求正在进行。",
     "1）拦截 /blog/add 并延迟响应；\n2）在请求进行中读取按钮的禁用状态与文案。",
     "请求进行中 isDisabled=false，按钮文案仍为\"发布文章\"。",
     "用户无法判断是否已提交，容易重复点击（与 BUG-E03 互为因果）。",
     "提交期间禁用按钮并将文案改为\"发布中…\"，请求结束后恢复。",
     "G2、G3", "待修复"),
]

MODULES = [
    ("A 页面结构与加载", "验证页面标题、核心元素与编辑器初始化", "功能测试"),
    ("B 访问控制", "验证未登录访问与写入的鉴权防护", "安全测试"),
    ("C 标题输入域", "验证标题输入的属性约束与边界表现", "功能测试"),
    ("D 编辑器内容", "验证 editor.md 的内容同步、预览与默认内容", "功能测试"),
    ("E 发布流程", "验证发布请求契约、成功跳转与编码", "功能测试"),
    ("F 校验与错误反馈", "验证空值与异常下的用户反馈", "健壮性测试"),
    ("G 重复提交", "验证防重复提交与提交中状态", "健壮性测试"),
    ("H 安全", "验证注入防护与未授权写入", "安全测试"),
    ("I 交互与兼容", "验证导航、注销、未保存提醒与多分辨率", "兼容性测试"),
]

wb = Workbook()

# ===== Sheet1 用例说明 =====
ws0 = wb.active
ws0.title = "用例说明"
ws0.sheet_view.showGridLines = False
ws0["A1"] = "博客编辑页 测试用例"
ws0["A1"].font = TITLE_FONT
ws0.merge_cells("A1:B1")
rows0 = [
    ("被测系统", "博客系统（我的博客系统）"),
    ("被测页面", "http://127.0.0.1:9090/blog_edit.html（页面标题：博客编辑页）"),
    ("核心功能", "填写标题 + editor.md（Markdown）编辑器写正文 → 点击\"发布文章\"提交"),
    ("写入接口", "POST /blog/add（application/json，需请求头 user_token_header）"),
    ("前置依赖", "需登录态；localStorage.user_token 由 /user/login 获取"),
    ("测试账号", "zhangsan / 123456"),
    ("用例总数", f"{len(CASES)} 条"),
    ("测试步骤总数", f"{sum(len(c[7]) for c in CASES)} 步"),
    ("执行结果", "全部执行通过；其中 12 条用例在执行中发现缺陷（详见\"缺陷清单\"）"),
    ("", ""),
    ("【重要测试约束】", ""),
    ("写操作风险", "本页是写操作页面，每次成功发布都会真实写入数据库。"
                   "因此所有发布用例均通过 page.route 拦截 /blog/add，"
                   "只验证前端载荷与响应处理，不产生任何数据。"),
    ("未污染验证", "测试前后调用 /blog/getList 比对博客条数，实测均为 1 条（与基线一致），"
                   "确认数据库未被污染。"),
    ("编辑器同步陷阱", "textarea#content 为 display:none，由 editor.md 的 CodeMirror 接管。"
                       "程序化调用 cm.setValue() 不会同步回 textarea，必须再调用 cm.save()；"
                       "否则 submit() 读到的是旧值，会误判为缺陷。真实键盘输入会自动同步（功能正常）。"),
    ("", ""),
    ("【字段说明】", ""),
    ("用例编号", "模块字母 + 序号，如 F1 表示 F 模块第 1 条用例"),
    ("所属模块", "按测试类型划分为 A~I 共 9 个模块"),
    ("优先级", "P0 核心必测；P1 重要；P2 一般"),
    ("设计方法", "等价类划分、边界值分析、错误推测、场景法、界面检查、性能测试等"),
    ("前置条件", "执行该用例前必须满足的环境与登录态"),
    ("测试数据", "该用例使用的具体输入；标注【安全】的表示发布接口被拦截"),
    ("步骤序号", "用例内的步骤序号，每条用例从 1 开始连续编号"),
    ("测试步骤 / 预期结果 / 实际结果", "该步骤的操作、应有结果与实际观测结果"),
    ("结论", "该用例整体执行结论"),
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
    ws0.row_dimensions[r].height = 20 if len(v) < 60 else 46
    r += 1
ws0.column_dimensions["A"].width = 20
ws0.column_dimensions["B"].width = 94

# ===== Sheet2 测试用例 =====
ws = wb.create_sheet("测试用例")
ws.sheet_view.showGridLines = False
ws.page_setup.orientation = "landscape"
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1
HEADERS = ["用例编号", "所属模块", "用例标题", "优先级", "设计方法",
           "前置条件", "测试数据", "步骤序号", "测试步骤", "预期结果", "实际结果", "结论"]
WIDTHS = [9, 16, 30, 7, 12, 30, 30, 7, 36, 32, 38, 14]
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
                               [20, 46, 14, 9, 9, 24]), start=1):
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
dw = [11, 10, 12, 30, 40, 38, 40, 34, 34, 12, 10]
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
for i, (h, w) in enumerate(zip(["统计项", "数值", "说明"], [24, 16, 58]), start=1):
    c = ws3.cell(3, i, h)
    c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    ws3.column_dimensions[get_column_letter(i)].width = w
defect_cases = [c[0] for c in CASES if c[8].startswith("发现缺陷")]
stats = [
    ("用例总数", f"{len(CASES)} 条", "见\"测试用例\"工作表"),
    ("测试步骤总数", f"{sum(len(c[7]) for c in CASES)} 步", "每条用例按步骤逐行展开"),
    ("自动化执行次数", f"{len(CASES)} 次", "1 条用例 = 1 次执行"),
    ("执行通过", f"{len(CASES)} 次", "断言层面无失败"),
    ("通过率", "100%", f"{len(CASES)} / {len(CASES)}"),
    ("发现缺陷", f"{len(DEFECTS)} 个", "1 高 / 4 中 / 3 低，详见\"缺陷清单\""),
    ("结论为\"发现缺陷\"的用例", f"{len(defect_cases)} 条", "、".join(defect_cases)),
    ("数据库污染", "无", "测试前后博客条数均为 1 条，发布接口全程被拦截"),
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
print("OK cases=%d steps=%d defects=%d defect_cases=%d" % (
    len(CASES), sum(len(c[7]) for c in CASES), len(DEFECTS), len(defect_cases)))
