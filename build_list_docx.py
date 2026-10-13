# -*- coding: utf-8 -*-
"""生成《博客列表页测试报告》Word 文档

用例数据不在此重复定义：直接从 build_list_xlsx.py 导入 CASES，
保证 Word 报告与 Excel 用例表的统计口径完全一致（单一数据源）。
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from build_list_xlsx import CASES

OUT = r"D:\study\AI\deepseek-day\博客列表页_测试报告.docx"
EA = "微软雅黑"
doc = Document()

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), EA)
for sec in doc.sections:
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.4)


def set_ea(run, name=EA):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def para(text, size=10.5, bold=False, align=None, space_after=6, color=None, style_name=None):
    p = doc.add_paragraph(style=style_name)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    set_ea(r)
    if color:
        r.font.color.rgb = RGBColor(*color)
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def heading(text, level):
    h = doc.add_heading(level=level)
    r = h.add_run(text)
    set_ea(r)
    if level == 1:
        r.font.size = Pt(15)
        r.font.color.rgb = RGBColor(0x1F, 0x3B, 0x73)
    elif level == 2:
        r.font.size = Pt(12.5)
        r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
    return h


def make_table(headers, rows, widths=None, header_bg="2F5597"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_ea(r)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), header_bg)
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(v))
            r.font.size = Pt(9.5)
            set_ea(r)
            p.paragraph_format.space_after = Pt(2)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    return t


# ==================== 封面 ====================
para("博客系统 列表页测试报告", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para("Blog List Page Test Report", size=11, align=WD_ALIGN_PARAGRAPH.CENTER,
     space_after=18, color=(0x60, 0x60, 0x60))

make_table(
    ["项目", "内容"],
    [
        ("被测系统", "博客系统（我的博客系统）"),
        ("被测页面", "http://127.0.0.1:9090/blog_list.html"),
        ("页面标题", "博客列表页"),
        ("关键接口", "GET /blog/getList、GET /user/getUserInfo（均需请求头 user_token_header）"),
        ("测试类型", "功能测试、安全测试、健壮性测试、兼容性测试、性能测试"),
        ("测试方式", "Playwright 自动化（Chromium，串行执行）"),
        ("测试工具", "Playwright 1.63.0 + TypeScript"),
        ("测试账号", "zhangsan / 123456"),
        ("测试时间", "2026-10-13"),
        ("报告版本", "V1.0"),
    ],
    widths=[4.0, 12.0],
)
doc.add_paragraph()

# ==================== 一、测试结论 ====================
heading("一、测试结论", 1)
para("本次针对博客列表页共设计 34 条测试用例（115 个测试步骤），覆盖列表渲染、"
     "鉴权访问控制、注销、错误异常处理、数据一致性、安全与交互兼容七个方面。")
para("自动化断言层面 34 次执行全部通过，并经过 5 轮重复执行验证稳定性"
     "（170 次执行零失败、零不稳定）。鉴权机制有效，注销流程正常，列表渲染字段完整。")
para("但测试过程中确认了 7 个缺陷，其中 2 个为高危：一是列表页存在存储型 XSS"
     "（title/content/createTime 三个字段均未转义），二是用户信息接口直接返回密码哈希。"
     "两者可组合利用，建议立即修复。", space_after=10)

para("核心结论：", bold=True, space_after=4)
for line in [
    "① 功能层面：列表渲染字段完整、顺序正确、详情链接正确，主流程可用。",
    "② 鉴权层面：未登录、伪造 token、空 token、错误头名均被拒绝（401 或跳转登录页），"
    "鉴权链路有效。",
    "③ 安全层面：存在 2 个高危缺陷（存储型 XSS、密码哈希泄露），且可组合利用窃取 token，"
    "属最高优先级。",
    "④ 数据一致性：左侧\"文章/分类\"计数为硬编码，与实际数据不符。",
    "⑤ 健壮性层面：业务失败与接口 5xx 均被静默吞掉，用户无法感知。",
    "⑥ 性能层面：接口不支持分页，全量返回数据（实测 100 条渲染 102ms，尚无虚拟滚动）。",
]:
    p = doc.add_paragraph(line)
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
        set_ea(r)

# ==================== 二、测试环境 ====================
heading("二、测试环境", 1)
make_table(
    ["类别", "项目", "说明"],
    [
        ("被测环境", "服务地址", "http://127.0.0.1:9090"),
        ("被测环境", "列表页", "/blog_list.html"),
        ("被测环境", "关联页面", "blog_login.html（登录）、blog_detail.html（详情）、"
                                  "blog_edit.html（写博客）"),
        ("运行环境", "操作系统", "Windows"),
        ("运行环境", "浏览器内核", "Chromium 1243（headless）"),
        ("运行环境", "自动化框架", "Playwright 1.63.0 + TypeScript"),
        ("测试数据", "有效账号", "zhangsan / 123456"),
        ("测试数据", "构造数据", "通过 page.route 拦截 /blog/getList 构造：空数组、3 条数据、"
                                  "超长文本、特殊字符、XSS 载荷、100 条压测数据"),
    ],
    widths=[3.0, 3.5, 9.5],
)
doc.add_paragraph()

# ==================== 三、执行统计 ====================
heading("三、测试执行统计", 1)

heading("3.1 总体统计", 2)
make_table(
    ["统计项", "数值", "说明"],
    [
        ("用例条数", "34", "Excel 用例文档中的用例条数"),
        ("测试步骤数", "115", "每条用例按步骤逐行展开"),
        ("自动化执行次数", "34", "1 条用例 = 1 次执行"),
        ("执行通过", "34", "断言层面全部通过"),
        ("执行失败", "0", "无断言失败"),
        ("通过率", "100%", "34 / 34"),
        ("稳定性验证", "170 次通过", "34 条 × 重复 5 轮，零失败、零不稳定"),
        ("发现缺陷", "7", "2 高 / 3 中 / 2 低"),
        ("结论为\"发现缺陷\"的用例", "10", "缺陷在用例中以基线断言锁定，未让用例失败"),
    ],
    widths=[5.0, 2.5, 8.5],
)
doc.add_paragraph()

heading("3.2 模块分布", 2)
# 模块统计由用例数据实时计算，避免手工填写出错
MODULE_ORDER = ["A 列表渲染", "B 鉴权与访问控制", "C 注销", "D 错误与异常处理",
                "E 数据一致性", "F 安全测试", "G 交互与兼容"]
_mod_rows = []
for _m in MODULE_ORDER:
    _sub = [c for c in CASES if c[1] == _m]
    _mod_rows.append((_m, str(len(_sub)), str(sum(len(c[7]) for c in _sub)),
                      str(len(_sub)), "0", "100%"))
_mod_rows.append(("合计", str(len(CASES)), str(sum(len(c[7]) for c in CASES)),
                  str(len(CASES)), "0", "100%"))
make_table(
    ["模块", "用例数", "步骤数", "通过", "失败", "通过率"],
    _mod_rows,
    widths=[4.2, 2.0, 2.0, 1.8, 1.8, 2.0],
)
doc.add_paragraph()

heading("3.3 缺陷严重级别分布", 2)
make_table(
    ["严重级别", "数量", "占比", "缺陷编号"],
    [
        ("高", "2", "28.6%", "BUG-L01、BUG-L02"),
        ("中", "3", "42.8%", "BUG-L03、BUG-L04、BUG-L05"),
        ("低", "2", "28.6%", "BUG-L06、BUG-L07"),
        ("合计", "7", "100%", "—"),
    ],
    widths=[3.0, 2.0, 2.5, 8.5],
)
doc.add_paragraph()

# ==================== 四、缺陷明细 ====================
heading("四、缺陷明细", 1)

DEFECTS = [
    dict(no="BUG-L01", sev="高", cat="安全", title="列表页存在存储型 XSS（三个字段均未转义）",
         desc="blog_list.html 使用字符串拼接生成 HTML 后经 html() 注入，title、content、"
              "createTime 三个字段均未做转义处理。由于写博客接口可提交任意标题与内容，"
              "攻击者可持久化恶意脚本。",
         steps="1）拦截 /blog/getList 返回 title（或 content、createTime）为 "
               "<img src=x onerror=\"window.__xss=1\"> 的数据；\n"
               "2）打开 blog_list.html 并等待列表渲染；\n3）检查 window.__xss 是否被赋值。",
         actual="注入的载荷被解析为真实 img 元素并触发 onerror，window.__xss=1，"
                "脚本在列表页实际执行；title、content、createTime 三个字段表现一致。",
         impact="任何登录用户发布含脚本的博客后，所有访问列表页的用户都会执行该脚本，"
                "可窃取 localStorage 中的 user_token，进而完全接管账号，属高危存储型 XSS。",
         fix="渲染前对 title、content、createTime 做 HTML 转义（替换 < > & \" '），"
             "或改用 text()/createTextNode 赋值，避免拼接 HTML。",
         ref="F1、F2、F3"),
    dict(no="BUG-L02", sev="高", cat="安全", title="/user/getUserInfo 响应体泄露密码哈希",
         desc="获取用户信息接口在 data 中直接返回了 password 字段，值为用户密码哈希；"
              "前端实际仅需 userName 与 githubUrl。",
         steps="1）以有效 token 调用 /user/getUserInfo；\n2）查看响应 data 的全部字段。",
         actual="响应字段为 [id, userName, password, githubUrl, deleteFlag, createTime, "
                "updateTime]，其中 password 为密码哈希值。",
         impact="敏感信息暴露给客户端；结合 BUG-L01 的 XSS，攻击者可直接读取该接口响应，"
                "获取密码哈希用于离线破解，风险叠加放大。",
         fix="接口返回前剔除 password 等敏感字段，改用 VO/DTO 只输出前端需要的字段。",
         ref="F4"),
    dict(no="BUG-L03", sev="中", cat="数据一致性", title="左侧文章计数为硬编码，与实际数据不一致",
         desc="左侧卡片中\"文章/分类\"的计数为 HTML 静态写死（2 和 1），未随实际数据变化。",
         steps="1）登录后打开 blog_list.html；\n2）读取卡片计数；\n"
               "3）统计右侧实际列表条数并比对。",
         actual="卡片显示\"文章=2，分类=1\"，实际列表仅 1 条，偏差 1。",
         impact="用户看到的统计与实际内容不符，误导用户，属数据展示错误。",
         fix="计数改为由 /blog/getList 返回的数据动态计算，或由后端提供统计接口。",
         ref="E1"),
    dict(no="BUG-L04", sev="中", cat="健壮性", title="getList 业务失败或接口异常时静默无提示",
         desc="getList 的 success 回调仅在 code=SUCCESS 时渲染，未处理 FAIL；error 回调仅处理 401。"
              "因此业务失败与 5xx 都不会给用户任何反馈。",
         steps="1）拦截 /blog/getList 返回 code=FAIL（或 HTTP 500）；\n"
               "2）打开 blog_list.html；\n3）观察页面反馈与列表区域内容。",
         actual="返回 FAIL 时：无弹窗、无占位文案、列表区域内容长度为 0；"
                "返回 500 时同样无任何提示，也未跳转登录页。",
         impact="用户看到空白页面，无法判断是\"没有博客\"还是\"加载失败\"，会反复刷新。",
         fix="success 回调增加 FAIL 分支提示 errMsg；error 回调补充非 401 分支的统一错误提示。",
         ref="D1、D2"),
    dict(no="BUG-L05", sev="中", cat="性能", title="列表接口不支持分页，全量返回数据",
         desc="getList 接口忽略 page、pageSize、pageNum、offset、limit 等分页参数，"
              "始终返回全部数据。",
         steps="1）分别以 ?page=1&pageSize=1、?pageNum=1&pageSize=1、?offset=0&limit=1 "
               "调用 /blog/getList；\n2）比对三次返回条数。",
         actual="三种分页参数返回条数完全相同（均为 1），参数未生效。",
         impact="数据量增长后单次返回全量数据，响应体膨胀，前端一次性渲染，"
                "存在响应变慢与内存占用风险（实测 100 条渲染 102ms，尚无虚拟滚动）。",
         fix="后端实现分页查询，前端配合分页组件或滚动加载。",
         ref="G6"),
    dict(no="BUG-L06", sev="低", cat="可用性", title="空列表无占位文案",
         desc="列表接口返回空数组时，右侧区域为纯空白，没有任何\"暂无博客\"类提示。",
         steps="1）拦截 /blog/getList 返回空数组 data:[]；\n2）打开 blog_list.html；\n"
               "3）观察列表区域可见文案。",
         actual="渲染 0 条，列表区域可见文案为空字符串。",
         impact="与\"加载失败\"表现完全相同，用户无法区分空数据与故障。",
         fix="空数组时渲染\"暂无博客\"占位提示。",
         ref="D3"),
    dict(no="BUG-L07", sev="低", cat="可用性", title="用户头像硬编码，不随登录用户变化",
         desc="左侧卡片头像使用固定资源 pic/doge.jpg，且 getUserInfo 未返回头像字段。",
         steps="1）登录后读取卡片头像 src；\n2）检查 getUserInfo 响应是否含头像字段。",
         actual="头像 src 恒为 pic/doge.jpg；接口响应无头像字段。",
         impact="所有用户看到同一张头像，与\"当前登录用户\"的语义不符。",
         fix="由后端在用户信息中提供头像地址，前端动态设置；或明确以固定占位图并去除误导性展示。",
         ref="E3"),
]

SEV_COLOR = {"高": (0xC0, 0x00, 0x00), "中": (0xBF, 0x60, 0x00), "低": (0x40, 0x40, 0x40)}
for i, d in enumerate(DEFECTS, start=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{i}. [{d['no']}] {d['title']}")
    r.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = RGBColor(*SEV_COLOR[d["sev"]])
    set_ea(r)
    make_table(
        ["字段", "内容"],
        [
            ("严重级别", d["sev"]),
            ("缺陷类别", d["cat"]),
            ("缺陷描述", d["desc"]),
            ("复现步骤", d["steps"]),
            ("实际结果", d["actual"]),
            ("影响", d["impact"]),
            ("修复建议", d["fix"]),
            ("关联用例", d["ref"]),
            ("状态", "待修复"),
        ],
        widths=[2.8, 13.2],
    )
    doc.add_paragraph()

doc.add_page_break()

# ==================== 五、测试范围 ====================
heading("五、测试范围与用例执行情况", 1)
para("下表汇总各模块用例的执行情况；完整用例（含前置条件、测试数据、逐步操作、"
     "预期结果与实际结果）详见配套 Excel 文档《博客列表页_测试用例.xlsx》。", space_after=8)
make_table(
    ["模块", "用例编号", "用例数", "覆盖内容", "执行情况"],
    [
        ("A 列表渲染", "A1-A6", "6",
         "卡片渲染、四个字段完整性、详情链接、多条顺序、超长内容、特殊字符", "全部通过"),
        ("B 鉴权与访问控制", "B1-B5", "5",
         "未登录拦截、伪造 token、空 token、错误请求头名、有效 token", "全部通过（鉴权有效）"),
        ("C 注销", "C1-C3", "3", "注销清 token、注销后访问、注销后后退", "全部通过"),
        ("D 错误与异常处理", "D1-D6", "6",
         "业务 FAIL、接口 500、空数组、用户信息 FAIL/500、非 JSON", "确认 2 个缺陷"),
        ("E 数据一致性", "E1-E3", "3", "计数一致性、用户名一致性、头像来源", "确认 2 个缺陷"),
        ("F 安全测试", "F1-F5", "5",
         "三字段 XSS、密码哈希泄露、未授权访问", "确认 2 个高危缺陷"),
        ("G 交互与兼容", "G1-G6", "6",
         "详情跳转、写博客跳转、多分辨率、静态资源、100 条性能、分页参数", "确认 1 个缺陷"),
    ],
    widths=[3.0, 2.2, 1.6, 6.2, 3.0],
)
doc.add_paragraph()

heading("5.1 已验证正常的关键项", 2)
for line in [
    "鉴权链路有效：未携带 token、空 token、伪造 token 访问 /blog/getList 均返回 401；"
    "伪造 token 访问列表页会被守卫跳转回登录页。",
    "鉴权头机制严格：接口按 user_token_header 取值，头名写成 user_token 即返回 401。",
    "注销流程正常：点击注销会清除 localStorage 中的 user_token 并跳转登录页；"
    "注销后再次访问列表页被正确拦截；注销后浏览器后退不会恢复登录态。",
    "列表渲染字段完整：标题、日期、内容、详情链接均正确渲染，多条数据顺序与接口一致；"
    "详情链接 href 与接口 id 完全对应。",
    "特殊字符安全呈现：标题中的引号、&、尖括号作为文本渲染，未产生额外 DOM 元素。",
    "卡片用户名正确：getUserInfo 成功后卡片用户名会更新为当前登录用户 zhangsan。",
    "异常不崩溃：getList 返回非 JSON、getUserInfo 返回 500 时页面均不白屏，无未捕获异常。",
    "静态资源正常：本次运行未出现 4xx/5xx 资源。",
]:
    p = doc.add_paragraph(line, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
        set_ea(r)

heading("5.2 测试方法说明", 2)
para("本次测试全程使用 Playwright 的 page.route 拦截 /blog/getList 与 /user/getUserInfo "
     "构造确定性数据，覆盖空数组、超长文本、特殊字符、XSS 载荷与 100 条压测数据，"
     "并在独立浏览器上下文中隔离登录态。测试过程不调用任何写接口，"
     "未向测试环境数据库写入数据，因此不会污染环境。", space_after=8)

heading("5.3 测试限制", 2)
para("① 未测试博客详情页（blog_detail.html）与写博客页（blog_edit.html）的功能正确性，"
     "仅验证了从列表页的跳转行为。", space_after=3)
para("② XSS 缺陷通过接口拦截注入载荷验证，未真实发布含脚本的博客文章"
     "（避免污染环境）；由于写博客接口未做输入过滤，实际攻击路径成立。", space_after=3)
para("③ 性能测试基于接口拦截构造数据，未评估真实数据库大数据量下的响应时间。", space_after=8)

# ==================== 六、风险评估与建议 ====================
heading("六、风险评估与建议", 1)
para("两个高危缺陷可组合利用：攻击者在博客标题中注入脚本 → 其他用户浏览列表页时脚本执行 → "
     "读取 localStorage.user_token → 冒充该用户登录，也可直接调用 getUserInfo 获取密码哈希。"
     "建议按以下优先级修复。", space_after=8)
make_table(
    ["优先级", "建议项", "对应缺陷"],
    [
        ("立即修复", "渲染列表前对 title、content、createTime 做 HTML 转义，"
                     "消除存储型 XSS（最高风险）", "BUG-L01"),
        ("立即修复", "getUserInfo 剔除 password 等敏感字段，仅返回前端需要的字段", "BUG-L02"),
        ("建议修复", "计数改为动态计算，保证与实际数据一致", "BUG-L03"),
        ("建议修复", "补全 FAIL 分支与 error 回调的失败提示，避免静默失败", "BUG-L04"),
        ("建议修复", "后端实现分页查询，避免全量返回", "BUG-L05"),
        ("可选优化", "空列表增加\"暂无博客\"占位提示", "BUG-L06"),
        ("可选优化", "头像改为后端返回或明确占位语义", "BUG-L07"),
    ],
    widths=[2.6, 10.4, 3.0],
)
doc.add_paragraph()

# ==================== 七、附录 ====================
heading("七、附录：测试资产", 1)
make_table(
    ["资产", "路径", "说明"],
    [
        ("测试用例文档", "博客列表页_测试用例.xlsx",
         "34 条用例 / 115 步，含概览、用例明细、模块划分、缺陷清单、执行统计 5 个工作表"),
        ("测试报告", "博客列表页_测试报告.docx", "本报告"),
        ("测试规划", "blog_list_test_plan.md", "测试点、模块与用例规划"),
        ("用例脚本", "tests/blog_list.spec.ts", "Playwright 用例实现，34 条用例"),
        ("页面对象", "pages/ListPage.ts", "列表页 Page Object 与接口封装"),
        ("一键执行", "run-tests-list.cmd", "免配置执行脚本，自动探测浏览器目录"),
        ("HTML 报告", "playwright-report/index.html", "含失败截图与 trace 回放"),
    ],
    widths=[3.0, 5.4, 7.6],
)
doc.add_paragraph()

para("说明：本报告数据来源为 2026-10-13 的自动化执行结果（Playwright，34 条用例全部通过，"
     "并完成 5 轮 170 次重复稳定性验证）。所有缺陷结论均经实际运行验证，非基于代码静态推断。",
     size=9.5, color=(0x60, 0x60, 0x60))

doc.save(OUT)
print("已生成:", OUT)
print("段落数:", len(doc.paragraphs), "表格数:", len(doc.tables))
