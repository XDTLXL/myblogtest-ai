# -*- coding: utf-8 -*-
"""生成《博客登录页测试报告》Word 文档"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\study\AI\deepseek-day\博客登录页_测试报告.docx"
EA = "微软雅黑"

doc = Document()

# ---------------- 全局字体与页边距 ----------------
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


# ==================== 封面标题 ====================
para("博客系统 登录页测试报告", size=22, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para("Blog Login Page Test Report", size=11,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18,
     color=(0x60, 0x60, 0x60))

make_table(
    ["项目", "内容"],
    [
        ("被测系统", "博客系统（我的博客系统）"),
        ("被测页面", "http://127.0.0.1:9090/blog_login.html"),
        ("页面标题", "博客登陆页"),
        ("核心接口", "POST /user/login"),
        ("测试类型", "功能测试、边界测试、安全测试、兼容性测试"),
        ("测试方式", "Playwright 自动化（Chromium，无头模式，串行执行）"),
        ("测试工具", "Playwright 1.63.0 + TypeScript；openpyxl / python-docx 生成报告"),
        ("测试账号", "zhangsan / 123456"),
        ("测试时间", "2026-10-13"),
        ("报告版本", "V1.0"),
    ],
    widths=[4.0, 12.0],
)
doc.add_paragraph()

# ==================== 一、测试结论 ====================
heading("一、测试结论", 1)
para("本次针对博客系统登录页共设计 36 条测试用例（自动化执行 40 次，其中 SQL 注入为"
     "参数化用例，1 条用例含 5 个载荷），覆盖正常登录、异常提示、输入边界、安全防护、"
     "前端健壮性与 UI 兼容六个方面。")
para("自动化断言层面 40 次执行全部通过，登录主流程功能正确、SQL 注入防护有效、"
     "XSS 无回显风险。但测试过程中确认了 6 个缺陷，其中 1 个高危、2 个中危，"
     "集中在越权访问与账号安全防护方面，建议修复后再上线。", space_after=10)

para("核心结论：", bold=True, space_after=4)
for line in [
    "① 功能层面：登录主流程可用，成功/失败分支、token 写入与跳转行为均正确。",
    "② 安全层面：存在 1 个高危缺陷（写操作页面缺少登录守卫）、2 个中危缺陷"
    "（用户枚举、暴力破解无限流），需优先修复。",
    "③ 健壮性层面：接口异常时前端静默失败、回车键无法提交，影响用户体验。",
    "④ 覆盖盲区：测试账号密码为纯数字，密码大小写敏感性无法完整验证。",
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
        ("被测环境", "登录页", "/blog_login.html"),
        ("被测环境", "关联页面", "blog_list.html（有登录守卫）、blog_edit.html（无登录守卫）"),
        ("运行环境", "操作系统", "Windows"),
        ("运行环境", "浏览器内核", "Chromium 1243（headless）"),
        ("运行环境", "自动化框架", "Playwright 1.63.0 + TypeScript"),
        ("测试数据", "有效账号", "zhangsan / 123456"),
        ("测试数据", "异常数据", "空值、纯空格、超长字符串、特殊字符、中文/emoji、"
                                "SQL 注入载荷 5 种、XSS 载荷 2 种"),
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
        ("用例条数", "36", "Excel 用例文档中的用例行数"),
        ("自动化执行次数", "40", "D1 SQL 注入参数化为 5 次执行"),
        ("执行通过", "40", "断言层面全部通过"),
        ("执行失败", "0", "无断言失败"),
        ("通过率", "100%", "40 / 40"),
        ("发现缺陷", "6", "1 高 / 2 中 / 3 低"),
        ("用例结论为\"发现缺陷\"", "8", "缺陷在用例中以基线断言锁定，未让用例失败"),
    ],
    widths=[5.0, 2.5, 8.5],
)
doc.add_paragraph()

heading("3.2 模块分布", 2)
make_table(
    ["模块", "用例数", "执行次数", "通过", "失败", "通过率"],
    [
        ("A 正常登录", "4", "4", "4", "0", "100%"),
        ("B 异常登录与错误提示", "8", "8", "8", "0", "100%"),
        ("C 输入域校验与边界", "6", "6", "6", "0", "100%"),
        ("D 安全测试", "8", "13", "13", "0", "100%"),
        ("E 交互与前端健壮性", "5", "5", "5", "0", "100%"),
        ("F UI 展示与兼容", "5", "5", "5", "0", "100%"),
        ("合计", "36", "40", "40", "0", "100%"),
    ],
    widths=[4.2, 2.0, 2.2, 1.8, 1.8, 2.0],
)
doc.add_paragraph()

heading("3.3 缺陷严重级别分布", 2)
make_table(
    ["严重级别", "数量", "占比", "缺陷编号"],
    [
        ("高", "1", "16.7%", "BUG-01"),
        ("中", "2", "33.3%", "BUG-02、BUG-03"),
        ("低", "3", "50.0%", "BUG-04、BUG-05、BUG-06"),
        ("合计", "6", "100%", "—"),
    ],
    widths=[3.0, 2.0, 2.5, 8.5],
)
doc.add_paragraph()

# ==================== 四、缺陷明细 ====================
heading("四、缺陷明细", 1)

DEFECTS = [
    dict(
        no="BUG-01", sev="高", cat="安全", title="blog_edit.html 缺少登录守卫",
        desc="未登录状态下可直接打开写博客页面，页面未做任何登录态校验。"
             "对比同一系统的 blog_list.html 具备守卫（会跳回登录页），两者行为不一致。",
        steps="1）清空 localStorage 登录态；"
              "2）直接访问 http://127.0.0.1:9090/blog_edit.html；"
              "3）观察页面是否正常打开。",
        actual="跳转链路实测：blog_list.html → blog_login.html（守卫生效）；"
               "blog_edit.html 无任何跳转，页面直接打开（守卫缺失）。",
        impact="未授权用户可访问写操作页面，存在越权访问风险。",
        fix="为 blog_edit.html 增加与 blog_list.html 一致的登录态校验，"
            "未登录时跳转至登录页。",
        ref="D8、F3",
    ),
    dict(
        no="BUG-02", sev="中", cat="安全", title="登录失败提示存在用户枚举",
        desc="账号不存在与密码错误返回的提示文案不同，攻击者可据此区分账号是否存在。",
        steps="1）用不存在的账号 no_such_user_8888 登录，记录提示；"
              "2）用已存在账号 zhangsan + 错误密码登录，记录提示；3）对比两者。",
        actual="不存在账号返回\"用户不存在\"；密码错误返回\"密码错误\"，两者可明确区分。",
        impact="可批量探测系统内有效账号，为撞库攻击提供前提。",
        fix="两种情况统一返回模糊提示，例如\"账号或密码错误\"。",
        ref="D4",
    ),
    dict(
        no="BUG-03", sev="中", cat="安全", title="缺少登录失败次数限制",
        desc="连续多次错误登录未触发任何限流、锁定或验证码机制。",
        steps="1）连续 5 次用错误密码调用 /user/login 接口；2）记录每次响应状态码。",
        actual="5 次失败均返回 HTTP 200 与 code=FAIL，无限流、无锁定、无验证码。",
        impact="可被暴力破解或撞库，系统无任何阻断能力。",
        fix="增加失败次数限制、图形验证码或账号临时锁定策略。",
        ref="D6",
    ),
    dict(
        no="BUG-04", sev="低", cat="健壮性", title="AJAX 缺少 error 回调导致异常静默失败",
        desc="登录接口异常时前端不给用户任何反馈。",
        steps="1）拦截 /user/login 并返回 HTTP 500；2）提交登录表单；3）观察页面反馈。",
        actual="页面无任何提示、无 loading 状态、无错误信息，用户完全无感知；"
               "但未出现未捕获异常导致的白屏。",
        impact="网络或服务端异常时用户会误以为点击无效而反复点击。",
        fix="为 $.ajax 增加 error 回调，提示\"网络异常，请稍后重试\"。",
        ref="E4",
    ),
    dict(
        no="BUG-05", sev="低", cat="可用性", title="回车键无法提交表单",
        desc="页面没有 form 元素，也没有键盘事件监听，回车键无效。",
        steps="1）填写用户名与密码；2）在密码框按 Enter；3）观察是否发起登录请求。",
        actual="未发起任何登录请求，页面无任何反应。",
        impact="违反用户对登录表单的常规预期，降低操作效率。",
        fix="将表单包裹在 form 元素中，或监听 keydown 回车事件触发提交。",
        ref="E2",
    ),
    dict(
        no="BUG-06", sev="低", cat="文案与规范", title="标题文案不规范且输入框缺少必填约束",
        desc="登录框标题使用\"登陆\"，且两个输入框均未设置 required 属性。",
        steps="1）查看登录对话框标题文案；"
              "2）检查 #username 与 #password 的 required 属性值。",
        actual="标题为\"登陆\"（规范用词应为\"登录\"）；两个输入框 required 均为 false；"
               "页面不存在 form 元素。",
        impact="文案不规范；缺少前端必填校验，空值校验完全依赖服务端。",
        fix="修正文案为\"登录\"；为输入框补充 required 属性或前端校验提示。",
        ref="F1",
    ),
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

    t = make_table(
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

# ==================== 五、测试范围与用例 ====================
heading("五、测试范围与用例执行情况", 1)
para("下列表格汇总各模块用例的执行情况，完整用例（含前置条件、测试步骤、预期结果、"
     "实测结果）详见配套 Excel 文档《博客登录页_测试用例.xlsx》。", space_after=8)

CASE_ROWS = [
    ("A 正常登录", "A1-A4", "4", "登录成功、token 写入 localStorage、跳转列表页、"
                                 "登录态延续、重复登录覆盖 token", "全部通过"),
    ("B 异常登录", "B1-B8", "8", "用户名密码空值三种组合、用户不存在、密码错误、"
                                 "密码大小写、密码/用户名首尾空格", "全部通过"),
    ("C 输入边界", "C1-C6", "6", "超长输入、特殊字符、中文与 emoji、纯空格、"
                                 "清空重输、密码掩码", "全部通过"),
    ("D 安全测试", "D1-D8", "8", "SQL 注入 5 种载荷、XSS 载荷、errMsg 回显、用户枚举、"
                                 "无凭据签发、暴力破解、越权访问两个页面",
     "断言通过，确认 3 个安全缺陷"),
    ("E 交互健壮性", "E1-E5", "5", "连点提交、回车提交、Tab 焦点顺序、"
                                   "接口 500、接口返回非 JSON", "断言通过，确认 2 个缺陷"),
    ("F UI 与兼容", "F1-F5", "5", "标题文案与必填标识、四种分辨率、导航跳转、"
                                  "静态资源、浏览器后退", "断言通过，确认 1 个缺陷"),
]
make_table(
    ["模块", "用例编号", "用例数", "覆盖内容", "执行情况"],
    CASE_ROWS,
    widths=[2.8, 2.2, 1.6, 6.4, 3.0],
)
doc.add_paragraph()

heading("5.1 已验证正常的关键项", 2)
for line in [
    "登录主流程：正确账号密码登录成功，返回 code=SUCCESS，token 正确写入 localStorage，"
    "并跳转至 blog_list.html。",
    "SQL 注入防护：5 种注入载荷（' or '1'='1、' or 1=1 --、admin'--、\" or \"\"=\"、"
    "'; DROP TABLE user; --）全部登录失败，均未签发 token，接口未返回 5xx。",
    "XSS 防护：注入 <script> 与 <img onerror> 载荷后，服务端 errMsg 未回显用户输入，"
    "脚本未被执行，无 XSS 回显风险。",
    "越权基础防护：未登录访问 blog_list.html 会被守卫正确拦截并弹回登录页。",
    "防重复提交：并发点击提交 3 次，实测仅发出 1 次登录请求，未出现重复提交。",
    "异常响应健壮性：接口返回非 JSON 内容时页面不白屏，仍停留在登录页。",
    "边界输入：超长输入、特殊字符、中文与 emoji 均未导致接口 5xx 或前端 JS 异常。",
]:
    p = doc.add_paragraph(line, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
        set_ea(r)

heading("5.2 未能覆盖的场景", 2)
para("密码大小写敏感性（用例 B6）无法完整验证：测试账号密码为 123456，"
     "属于纯数字，toUpperCase() 不改变其值，因此无法通过大小写变形判断服务端是否"
     "区分大小写。已改用含字母的错误密码验证失败路径（大写、小写两种形式均返回 FAIL），"
     "但真正的大小写敏感性仍需补充一个含字母密码的测试账号后才能覆盖。", space_after=8)

# ==================== 六、风险与建议 ====================
heading("六、风险评估与建议", 1)
make_table(
    ["优先级", "建议项", "对应缺陷"],
    [
        ("必须修复", "为 blog_edit.html 补充登录守卫，消除越权访问风险", "BUG-01"),
        ("必须修复", "统一登录失败提示文案，消除用户枚举风险", "BUG-02"),
        ("建议修复", "增加登录失败次数限制或验证码，防暴力破解", "BUG-03"),
        ("建议修复", "补充 AJAX error 回调，异常时给用户明确提示", "BUG-04"),
        ("可选优化", "支持回车键提交表单", "BUG-05"),
        ("可选优化", "修正\"登陆\"文案为\"登录\"，补充输入框必填约束", "BUG-06"),
        ("测试补充", "提供含字母密码的测试账号，补齐大小写敏感性用例", "B6"),
    ],
    widths=[2.6, 10.4, 3.0],
)
doc.add_paragraph()

# ==================== 七、附录 ====================
heading("七、附录：测试资产", 1)
make_table(
    ["资产", "路径", "说明"],
    [
        ("测试用例文档", "博客登录页_测试用例.xlsx",
         "36 条用例，含概览、用例明细、缺陷清单、分布统计 4 个工作表"),
        ("测试报告", "博客登录页_测试报告.docx", "本报告"),
        ("测试规划", "blog_login_test_plan.md", "测试点与测试模块规划"),
        ("用例脚本", "tests/blog_login.spec.ts", "Playwright 用例实现，40 次执行"),
        ("页面对象", "pages/LoginPage.ts", "登录页 Page Object 与接口封装"),
        ("配置文件", "playwright.config.ts", "baseURL、报告器、截图与 trace 配置"),
        ("一键执行", "run-tests.cmd", "免配置执行脚本，自动探测浏览器目录"),
        ("HTML 报告", "playwright-report/index.html", "含失败截图与 trace 回放"),
    ],
    widths=[3.0, 5.4, 7.6],
)
doc.add_paragraph()

para("说明：本报告数据来源为 2026-10-13 的自动化执行结果"
     "（playwright test，40 次执行全部通过），缺陷结论均经实际运行验证，"
     "非基于代码静态推断。",
     size=9.5, color=(0x60, 0x60, 0x60))

doc.save(OUT)
print("已生成:", OUT)
print("段落数:", len(doc.paragraphs), "表格数:", len(doc.tables))
