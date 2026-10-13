# 博客登录页自动化测试（Playwright）

针对测试环境登录页 `http://127.0.0.1:9090/blog_login.html` 的 Playwright 自动化脚本。

## 目录结构

```
playwright.config.ts          配置文件（baseURL、报告器、截图/trace）
pages/LoginPage.ts            登录页 Page Object + 接口调用封装
tests/blog_login.spec.ts      40 条用例，覆盖 A~F 六个模块
summarize-findings.js         从 JSON 报告提取"实测结论基线"
blog_login_test_plan.md       测试规划
```

## 环境准备

```powershell
# 1. 依赖（使用工作区内的 npm 缓存，避免写入全局缓存）
npm install --cache .\.npm-cache

# 2. 浏览器：本机已有 Playwright 浏览器缓存，指向它即可
$env:PLAYWRIGHT_BROWSERS_PATH = "C:\Users\XDTLXL\AppData\Local\ms-playwright"

# 3. 被测环境需已启动
#    http://127.0.0.1:9090
```

> 安装的 Playwright 版本固定为 **1.63.0**，因为它与本地已缓存的
> Chromium 1243 / headless-shell 1243 完全匹配，无需重新下载浏览器。

## 运行

### 方式一：一键脚本（推荐，无需任何配置）

双击 `run-tests.cmd`，或在该目录打开终端执行：

```cmd
run-tests.cmd
```

脚本会自动完成：设置浏览器目录 → 检查被测环境是否可访问 →
首次运行自动装依赖 → 执行测试 → 打印结果并以正确退出码结束。

可透传参数给 Playwright：

```cmd
run-tests.cmd --headed            有头模式，能看到浏览器操作过程
run-tests.cmd --ui                打开交互式 UI，可单条点选运行
run-tests.cmd -g "D1"             只跑标题含 D1 的用例
run-tests.cmd --repeat-each=2     全部用例跑两遍（查偶发失败）
```

退出码：`0` 全部通过，`1` 存在失败，可直接用于 CI。

### 方式二：命令行手动执行

```powershell
# 关键：必须先指向浏览器缓存目录，否则报 "Executable doesn't exist"
$env:PLAYWRIGHT_BROWSERS_PATH = "C:\Users\XDTLXL\AppData\Local\ms-playwright"

npm test                 # 全量 40 条
npx playwright test -g "D1"     # 只跑 SQL 注入用例
npm run test:report      # 跑完并输出"实测结论基线"摘要
npm run show-report      # 打开 HTML 报告（含截图与 trace）
```

## 可覆盖的环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `BASE_URL` | `http://127.0.0.1:9090` | 被测地址前缀 |
| `LOGIN_USERNAME` | `zhangsan` | 有效测试账号 |
| `LOGIN_PASSWORD` | `123456` | 有效测试密码 |
| `PLAYWRIGHT_BROWSERS_PATH` | 系统默认 | 浏览器缓存目录 |

## 用例模块

| 模块 | 内容 | 用例数 |
|---|---|---|
| A 正常登录 | 接口返回、token 落库、跳转、登录态延续、重复登录 | 4 |
| B 异常登录 | 空值三种组合、用户不存在、密码错误、大小写、空格 | 8 |
| C 输入边界 | 超长、特殊字符、中文 emoji、纯空格、清空重输、掩码 | 6 |
| D 安全 | SQL 注入 ×5、XSS、错误回显、用户枚举、无凭据、暴力破解、越权访问 | 10 |
| E 健壮性 | 连点、回车、Tab 顺序、接口 500、非 JSON 响应 | 5 |
| F UI 兼容 | 文案/必填、多分辨率、导航跳转、静态资源、后退 | 5 |

## 脚本实现要点

登录页有几个坑，脚本里已经处理：

1. **响应体读不到**：登录成功会立即 `location.href` 跳转，跳转后
   `Network.getResponseBody` 一律失效（在哪个时机读都一样）。
   因此 `submitAndCapture()` 用 `page.route` 在路由层拦截并取回 JSON。
2. **原生 `alert` 阻塞**：失败提示是同步 `alert()`。必须先
   `expectAlert()` 注册 dialog 监听再点提交，否则页面 JS 会被挂起。
3. **FAIL 也是 HTTP 200**：断言一律看响应体 `code` 字段，不能看状态码。
4. **连点测试不能串行 await**：串行会等第一次跳转完成，测不出连点，
   需并发派发点击。

## 实测结论（40/40 通过）

**已确认的缺陷**

| 编号 | 缺陷 | 证据 |
|---|---|---|
| D8 | `blog_edit.html` 缺少登录守卫，未登录可直接打开 | 对比 `blog_list.html` 有守卫会弹回登录页 |
| D4 | 用户枚举：密码错误返回"密码错误"，账号不存在返回"用户不存在" | 两种提示可区分，可批量探测账号 |
| D6 | 无登录失败次数限制 | 连续 5 次失败均返回 200，无限流/锁定 |
| F1 | 标题"登陆"用词不规范；输入框缺 `required` | 两端 `required=false` |
| E2 | 回车键无法提交 | 页面无 `<form>`、无 keydown 监听 |
| E4 | AJAX 缺 `error` 回调，接口 500 时用户无感知 | 拦截接口返回 500 后无任何提示 |

**已验证为正常**

| 编号 | 结论 |
|---|---|
| D1 | 5 种 SQL 注入载荷全部失败，未签发 token |
| D3 | `errMsg` 未回显用户输入，无 XSS 回显风险 |
| E1 | 连点 3 次实测仅发出 1 次请求，未出现重复提交 |
| F4 | 静态资源全部正常（本次无 favicon 报错） |

**无法覆盖的场景**

- B6 密码大小写敏感性：测试账号密码 `123456` 为纯数字，`toUpperCase()`
  不改变其值，**无法验证**。需另提供含字母的账号密码。

## 已知限制

- 用例串行执行（`workers: 1`），因为登录会写 `localStorage` 并触发跳转，
  并行会产生相互干扰。
- 部分用例锁定的是"当前真实行为基线"（见脚本中 `test.info().annotations`），
  目的是让缺陷变化在回归时暴露出来，因此这些用例当前是通过状态。
