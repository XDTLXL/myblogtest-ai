# 博客系统自动化测试（Playwright）

针对测试环境 `http://127.0.0.1:9090` 的 Playwright 自动化测试，目前覆盖两个页面：

| 页面 | 用例数 | 脚本 | 文档 |
|---|---|---|---|
| 登录页 `blog_login.html` | 40 | `tests/blog_login.spec.ts` | [测试用例](博客登录页_测试用例.xlsx) / [测试报告](博客登录页_测试报告.docx) |
| 列表页 `blog_list.html` | 34 | `tests/blog_list.spec.ts` | [测试用例](博客列表页_测试用例.xlsx) / [测试报告](博客列表页_测试报告.docx) |

## 目录结构

```
playwright.config.ts          配置（baseURL、报告器、login/list 两个 project）
pages/LoginPage.ts            登录页 Page Object
pages/ListPage.ts             列表页 Page Object
tests/blog_login.spec.ts      登录页 40 条用例
tests/blog_list.spec.ts       列表页 34 条用例
run-tests.cmd                 一键执行（登录页）
run-tests-list.cmd            一键执行（列表页）
build_*.py                    文档生成脚本（Excel / Word）
blog_*_test_plan.md           测试规划
summarize-findings.js         从 JSON 报告提取实测结论
```

## 环境准备

```powershell
# 1. 依赖（使用工作区内 npm 缓存）
npm install --cache .\.npm-cache

# 2. 浏览器缓存目录（关键，否则报 Executable doesn't exist）
$env:PLAYWRIGHT_BROWSERS_PATH = "C:\Users\XDTLXL\AppData\Local\ms-playwright"
```

Playwright 固定为 **1.63.0**，与本地已缓存的 Chromium 1243 精确匹配，无需重新下载浏览器。

## 运行

### 一键脚本（推荐，无需配置）

```cmd
run-tests.cmd            登录页用例
run-tests-list.cmd       列表页用例
```

两个脚本都会自动探测浏览器目录、检查被测环境、首次运行自动装依赖，
并以正确退出码结束（通过=0，失败=1）。

透传参数给 Playwright：

```cmd
run-tests-list.cmd --headed          有头模式
run-tests-list.cmd --ui              交互式 UI，可单条点选
run-tests-list.cmd -g "F1"           只跑 F1 用例
run-tests-list.cmd --repeat-each=5   重复 5 轮查不稳定用例
```

### 命令行手动执行

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "C:\Users\XDTLXL\AppData\Local\ms-playwright"

npx playwright test                      # 全部 74 条（登录页 + 列表页）
npx playwright test --project=login      # 只跑登录页
npx playwright test --project=list       # 只跑列表页
npx playwright test -g "D1"              # 按用例编号筛选
npm run show-report                      # 打开 HTML 报告
```

## 可覆盖的环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `BASE_URL` | `http://127.0.0.1:9090` | 被测地址前缀 |
| `LOGIN_USERNAME` | `zhangsan` | 有效测试账号 |
| `LOGIN_PASSWORD` | `123456` | 有效测试密码 |
| `PLAYWRIGHT_BROWSERS_PATH` | 系统默认 | 浏览器缓存目录 |

## 列表页关键机制（实测确认）

1. **鉴权请求头是 `user_token_header`**，由 `common.js` 的 `$(document).ajaxSend` 自动注入；
   头名写成 `user_token` 会返回 401。用 `fetch` 直接调用接口不会触发该注入，需手动带头。
2. 列表接口 `GET /blog/getList` 返回 401 时，前端 `error` 回调会跳转登录页 ——
   这是 `blog_list.html` 的登录守卫实现方式。
3. `GET /user/getUserInfo` 的响应体包含 `password` 字段（密码哈希），属信息泄露。
4. 列表用字符串拼接 + `html()` 渲染，`title`/`content`/`createTime` 均未转义，
   存在存储型 XSS。

## 在加载本机执行时遇到的坑（已解决）

1. **响应体读不到**：登录成功会立即跳转，跳转后响应体任何时机都读不到；
   改用 `page.route` 在路由层取回 JSON，并等 `fulfill` 完成后再解除拦截。
2. **原生 `alert` 阻塞**：失败提示是同步 `alert()`，必须先注册 dialog 监听再点击提交。
3. **FAIL 也是 HTTP 200**：断言一律看响应体 `code`，不能看状态码。
4. **`-g` 与文件路径冲突**：`playwright test <file> -g "X"` 会把 X 当成文件路径；
   改用 `--project=login|list` 限定范围，`-g` 保持自由。
5. **共享环境不支持并发压测**：同时跑两个 Playwright 进程会造成环境资源竞争，
   出现偶发超时；请串行执行。

## 已发现缺陷汇总

**登录页（6 个）**：`blog_edit.html` 缺登录守卫（高）、用户枚举（中）、无暴力破解防护（中）、
AJAX 静默失败、回车不可提交、文案不规范（低）。

**列表页（7 个）**：存储型 XSS（高）、`getUserInfo` 泄露密码哈希（高）、
计数硬编码不一致（中）、FAIL/500 静默无提示（中）、不支持分页（中）、
空态无占位文案（低）、头像硬编码（低）。

详见各页面的测试报告与 Excel 用例表中对应的缺陷清单工作表。

