# 博客列表页 测试规划（blog_list.html）

- 被测页面：http://127.0.0.1:9090/blog_list.html
- 页面标题：博客列表页
- 前置依赖：需登录态（`localStorage.user_token`），未登录会被守卫弹回登录页
- 实测账号：zhangsan / 123456

## 一、页面结构与功能盘点

页面为左右两栏布局：左侧展示博主信息卡片，右侧由 JS 动态渲染博客列表。

| 区域 | 元素 | 关键属性 | 说明 |
|---|---|---|---|
| 导航栏 | logo + 主页 + 写博客 + **注销** | `a[onclick="logout()"]` | 注销会清除 token 并跳登录页 |
| 左侧博主卡片 | 头像 + `h3` 用户名 + GitHub 链接 + 计数行 | `.left .card` | 由 `/user/getUserInfo` 动态填充 |
| 左侧计数 | "文章 / 分类" + 数字 | `.card .row` | 静态写死为 2 / 1 |
| 右侧列表容器 | 空 `div.right` | `.container .right` | 由 `/blog/getList` 渲染 |

页面脚本行为（实测确认）：

1. `common.js` 注册 `$(document).ajaxSend`，为**所有 jQuery 请求**加 `user_token_header` 头。
2. 页面加载即发起 `GET /blog/getList`；`code=SUCCESS` 时用**字符串拼接**生成博客卡片 HTML 并 `html()` 注入。
3. `error` 回调中仅当 `status==401` 时跳转登录页。
4. 调用 `getUserInfo("/user/getUserInfo")` 填充左侧卡片；FAIL 时 `alert(errMsg)`。

## 二、接口清单与实测响应

| 接口 | 方法 | 鉴权 | 实测响应 |
|---|---|---|---|
| `/blog/getList` | GET | 需 `user_token_header` | `{"code":"SUCCESS","data":[{"id":32213,"title":"博客标题","content":"博客内容","userId":3,"deleteFlag":0,"createTime":"2025-03-18 11:41","loginUser":false}]}` |
| `/user/getUserInfo` | GET | 需 token | `{"code":"SUCCESS","data":{"id":3,"userName":"zhangsan","password":"4a352a...","githubUrl":"https://gitee.com/..."}}` |

鉴权行为实测：

| 场景 | 结果 |
|---|---|
| 正确 `user_token_header` | 200 SUCCESS |
| 头部名写成 `user_token` | 401 |
| 值为空串 / `"null"` / 伪造串 | 401 |
| 完全不带 token | 401，前端 `error` 回调跳转登录页 |

> **重点**：无 token 与伪造 token 访问列表页，均会被正确拦截并跳回登录页，鉴权链路有效。
> 但 `/user/getUserInfo` 的响应体**直接返回了用户密码哈希**，属严重信息泄露。

## 三、测试模块与用例规划

### 模块 L（列表页）用例设计

#### 模块 A：列表渲染（P0/P1）
| 编号 | 场景 | 预期 |
|---|---|---|
| A1 | 正常登录后进入列表页 | 标题为"博客列表页"，右侧渲染出博客卡片，条数与接口 `data` 长度一致 |
| A2 | 卡片字段完整性 | 标题、日期、内容、详情链接四个字段均渲染 |
| A3 | 详情链接正确性 | `href` 为 `blog_detail.html?blogId=<id>`，且 id 与接口一致 |
| A4 | 多条博客渲染 | N 条数据渲染 N 个 `.blog`，标题顺序与接口返回一致 |
| A5 | 长内容展示 | 记录是否截断（截图与长度对比） |
| A6 | 特殊字符标题（`<>&"'`） | 记录是否转义、是否乱码 |

#### 模块 B：鉴权与访问控制（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| B1 | 未登录访问列表页 | 被守卫拦截，跳转 `blog_login.html` |
| B2 | 伪造 token | 401 → 跳转登录页 |
| B3 | 空 token | 401 → 跳转登录页 |
| B4 | token 头名写错 | 401（验证鉴权严格依赖 `user_token_header`） |
| B5 | 正常 token | 200 且成功渲染 |

#### 模块 C：注销（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| C1 | 点击注销 | 清除 `user_token`，跳转登录页 |
| C2 | 注销后再访问列表页 | 被守卫拦截 |
| C3 | 注销后浏览器后退 | 记录状态（缓存页是否可回看） |

#### 模块 D：错误与异常处理（P1）
| 编号 | 场景 | 预期 |
|---|---|---|
| D1 | `getList` 返回 `code=FAIL` | **实测：无任何提示，列表静默空白 → 缺陷** |
| D2 | `getList` 接口 500 | 记录是否有提示（`error` 回调只处理 401） |
| D3 | `getList` 返回空数组 | 记录空态表现（当前为空区域，无占位文案） |
| D4 | `getUserInfo` 返回 FAIL | 弹出 `errMsg`，卡片保留硬编码值 |
| D5 | `getUserInfo` 接口 500 | 记录表现 |
| D6 | 接口返回非 JSON | 页面不白屏 |

#### 模块 E：数据一致性（P1）
| 编号 | 场景 | 预期 |
|---|---|---|
| E1 | 左侧计数与实际条数 | **实测：卡片写死 2/1，实际列表 1 条 → 不一致，缺陷** |
| E2 | 卡片用户名与登录用户 | 实测会更新为 `zhangsan`，与登录用户一致 |
| E3 | 卡片头像与真实用户 | 头像为硬编码 `pic/doge.jpg`，非用户头像 |

#### 模块 F：安全（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| F1 | 列表 XSS：`title` 注入 | **实测：注入的 `<img onerror>` 被解析并执行脚本 → 高危存储型 XSS** |
| F2 | 列表 XSS：`content` 注入 | **实测：同样执行 → 高危** |
| F3 | 列表 XSS：`createTime` 注入 | **实测：同样执行 → 高危** |
| F4 | `getUserInfo` 敏感字段泄露 | **实测：响应体含 `password` 哈希 → 信息泄露** |
| F5 | 未授权访问 `getList` | 401（防护有效） |

#### 模块 G：交互与兼容（P1/P2）
| 编号 | 场景 | 预期 |
|---|---|---|
| G1 | "查看全文"跳转详情页 | 跳转 `blog_detail.html?blogId=32213` |
| G2 | 导航"写博客" | 跳转 `blog_edit.html` |
| G3 | 多分辨率布局 | 卡片与列表不重叠、不溢出 |
| G4 | 静态资源 | 无 4xx/5xx |
| G5 | 大量数据（100 条） | 记录渲染耗时与是否卡顿 |
| G6 | 列表分页参数 | **实测：`page/pageSize` 等参数被忽略，始终返回全部 → 缺陷** |

## 四、已确认缺陷候选（侦察阶段实测确认）

| 编号 | 级别 | 缺陷 | 证据 |
|---|---|---|---|
| BUG-L01 | **高** | 列表页存储型 XSS（title/content/createTime 三字段均未转义） | 注入 `<img src=x onerror=...>` 后脚本实际执行 |
| BUG-L02 | **高** | `/user/getUserInfo` 响应体返回密码哈希 | 响应含 `"password":"4a352a..."` |
| BUG-L03 | 中 | 左侧"文章/分类"计数为硬编码，与实际数据不一致 | 卡片显示 2 篇，实际 1 篇 |
| BUG-L04 | 中 | `getList` 返回 FAIL 时静默无提示 | 无弹窗、无文案、无控制台报错，列表空白 |
| BUG-L05 | 中 | 列表接口不支持分页 | `page/pageSize/offset/limit` 均被忽略 |
| BUG-L06 | 低 | 空列表无占位文案 | 空数组时右侧为纯空白 |
| BUG-L07 | 低 | 用户头像硬编码，不随登录用户变化 | 始终为 `pic/doge.jpg` |

## 五、执行策略

- 使用 Playwright 拦截接口（`page.route`）构造确定性数据，避免污染测试环境数据库
- **不向生产/测试库写入任何数据**（不调用 `/blog/add`）
- 鉴权类用例使用独立 `context`，避免 token 串扰
- XSS 用例通过拦截 `getList` 注入载荷，验证前端渲染是否转义

## 六、交付物

1. `tests/blog_list.spec.ts` — 自动化用例
2. `pages/ListPage.ts` — Page Object
3. `博客列表页_测试用例.xlsx` — 规范测试用例（步骤级）
4. `博客列表页_测试报告.docx` — 测试报告
5. `run-tests-list.cmd` — 一键手动执行脚本
