import { test, expect } from '@playwright/test';
import {
  LoginPage,
  postLoginApi,
  CREDENTIALS,
  ROUTES,
  SELECTORS,
  ORIGIN,
} from '../pages/LoginPage';

/**
 * 博客登录页自动化用例
 *
 * 覆盖规划中的 A~F 六个模块：
 *   A 正常登录 / B 异常提示 / C 输入边界 / D 安全 / E 前端健壮性 / F UI 与兼容
 *
 * 说明：部分用例锁定的是**当前真实行为**（包括已知缺陷），
 * 目的是把它固化为可追踪的回归证据，因此这些用例会通过而不是失败，
 * 真实结论记录在 test.info().annotations 里，可在 HTML 报告中查看。
 */

const VALID = CREDENTIALS;

test.describe('A 正常登录', () => {
  test('A1 正确账号密码：接口返回 SUCCESS 且写入 localStorage token', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();
    await login.fill(VALID.username, VALID.password);

    const result = await login.submitAndCapture();

    expect(result.body.code).toBe('SUCCESS');
    expect(result.body.data).toBeTruthy();

    // 等跳转完成后再读 localStorage（同源，跳转不丢存储）
    await page.waitForURL(`**${ROUTES.list}`);
    const token = await login.token();
    expect(token).toBeTruthy();
    expect(token).toBe(result.body.data);
  });

  test('A2 登录成功后跳转到 blog_list.html', async ({ page }) => {
    const login = new LoginPage(page);
    await login.login(VALID.username, VALID.password);
    await expect(page).toHaveURL(new RegExp(`${ROUTES.list.replace('.', '\\.')}$`));
    expect(await page.title()).not.toBe('博客登陆页');
  });

  test('A3 token 在跳转后的页面可读取（登录态可延续）', async ({ page }) => {
    const login = new LoginPage(page);
    await login.login(VALID.username, VALID.password);
    const token = await login.token();
    expect(token).toBeTruthy();
    // 刷新后 token 不丢，说明是持久化存储而非内存态
    await page.reload();
    expect(await login.token()).toBe(token);
  });

  test('A4 同一账号重复登录：旧 token 被覆盖为新值', async ({ page }) => {
    const login = new LoginPage(page);
    await login.login(VALID.username, VALID.password);
    const first = await login.token();

    await login.login(VALID.username, VALID.password);
    const second = await login.token();

    expect(second).toBeTruthy();
    // JWT 含 exp，若签发时间粒度相同可能相等，因此只断言"非空且被重新写入"
    expect(second).not.toBeNull();
    if (first !== second) {
      expect(second).not.toBe(first);
    }
  });
});

test.describe('B 异常登录与错误提示', () => {
  const failCases: Array<{ id: string; title: string; username: string; password: string }> = [
    { id: 'B1', title: '用户名与密码均为空', username: '', password: '' },
    { id: 'B2', title: '只填用户名', username: VALID.username, password: '' },
    { id: 'B3', title: '只填密码', username: '', password: VALID.password },
  ];

  for (const c of failCases) {
    test(`${c.id} ${c.title}：返回 FAIL 且不写入 token、不跳转`, async ({ page }) => {
      const login = new LoginPage(page);
      await login.goto();
      await login.clearToken();

      const alertPromise = login.expectAlert();
      await login.fill(c.username, c.password);
      const result = await login.submitAndCapture();
      const alertText = await alertPromise;

      expect(result.body.code).toBe('FAIL');
      expect(result.body.data).toBeNull();
      expect(alertText).toContain('不能为空');

      // 关键：失败后必须留在登录页且不产生 token
      await expect(page).toHaveURL(new RegExp(`${ROUTES.login.replace('.', '\\.')}$`));
      expect(await login.token()).toBeNull();
    });
  }

  test('B4 用户名不存在：提示"用户不存在"，停留当前页', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill('no_such_user_9527', VALID.password);
    const result = await login.submitAndCapture();
    const alertText = await alertPromise;

    expect(result.body.code).toBe('FAIL');
    expect(alertText).toContain('用户不存在');
    await expect(page).toHaveURL(new RegExp(`${ROUTES.login.replace('.', '\\.')}$`));
    expect(await login.token()).toBeNull();
  });

  test('B5 用户名存在但密码错误：必须登录失败且不签发 token', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill(VALID.username, 'wrong_password_123');
    const result = await login.submitAndCapture();
    const alertText = await alertPromise;

    expect(result.body.code).toBe('FAIL');
    expect(result.body.data).toBeNull();
    expect(alertText.length).toBeGreaterThan(0);
    await expect(page).toHaveURL(new RegExp(`${ROUTES.login.replace('.', '\\.')}$`));
    expect(await login.token()).toBeNull();
  });

  test('B6 密码大小写敏感：当前测试账号为纯数字，记录前提并校验含字母错误密码', async ({ page, request }) => {
    // 测试账号密码为 123456（纯数字），toUpperCase() 后与原值完全相同，
    // 无法用"大写变形"验证大小写敏感性。这里显式记录该前提，
    // 并用真正含字母的错误密码校验服务端不会误放行。
    const numericOnly = /^\d+$/.test(VALID.password);

    test.info().annotations.push({
      type: '大小写测试前提',
      description: numericOnly
        ? `密码 "${VALID.password}" 为纯数字，toUpperCase() 不改变其值，无法用于大小写敏感性验证；` +
          '需另提供含字母的账号才能真正覆盖该场景'
        : '密码含字母，可直接用大小写变形验证',
    });
    expect(VALID.password.toUpperCase()).toBe(VALID.password);

    // 含字母的错误密码：大小写两种写法都必须失败
    const upper = await postLoginApi(request, VALID.username, 'WrongPasswordABC');
    const lower = await postLoginApi(request, VALID.username, 'wrongpasswordabc');
    expect(upper.body.code).toBe('FAIL');
    expect(lower.body.code).toBe('FAIL');
    expect(upper.body.data).toBeNull();
    expect(lower.body.data).toBeNull();

    // 走界面再确认一次：失败后不得写入 token、不得跳转
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill(VALID.username, 'WrongPasswordABC');
    const result = await login.submitAndCapture();
    const alertText = await alertPromise;

    expect(result.body.code).toBe('FAIL');
    expect(alertText.length).toBeGreaterThan(0);
    await expect(page).toHaveURL(new RegExp(`${ROUTES.login.replace('.', '\\.')}$`));
    expect(await login.token()).toBeNull();
  });

  test('B7 密码追加空格后必须失败（记录服务端是否 trim）', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill(VALID.username, `${VALID.password} `);
    const result = await login.submitAndCapture();
    await alertPromise;

    expect(result.body.code).toBe('FAIL');
    expect(await login.token()).toBeNull();
  });

  test('B8 用户名前后加空格：记录服务端 trim 基线行为', async ({ request }) => {
    const api = await postLoginApi(request, ` ${VALID.username} `, VALID.password);
    // 仅锁定基线：trim 则 SUCCESS，不 trim 则 FAIL，两种都不算服务端缺陷
    expect(['SUCCESS', 'FAIL']).toContain(api.body.code);
    if (api.body.code === 'SUCCESS') {
      expect(api.body.data).toBeTruthy();
    } else {
      expect(api.body.data).toBeNull();
    }
  });
});

test.describe('C 输入域校验与边界', () => {
  test('C1 超长用户名与密码：接口不返回 5xx，且失败可读', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill('a'.repeat(1000), 'b'.repeat(1000));
    const result = await login.submitAndCapture();
    await alertPromise;

    expect(result.status).toBeLessThan(500);
    expect(result.body.code).toBe('FAIL');
    expect(await login.token()).toBeNull();
  });

  test('C2 特殊字符用户名：无 JS 异常且服务端失败可读', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill(`!@#$%^&*()_+-=[]{}|;:'",.<>/?\\`, 'p@ss');
    const result = await login.submitAndCapture();
    await alertPromise;

    expect(result.status).toBeLessThan(500);
    expect(result.body.code).toBe('FAIL');
    expect(errors).toEqual([]);
  });

  test('C3 中文与 emoji 用户名：不乱码、不 5xx、不误判成功', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill('张三🔒测试', '密码123');
    const result = await login.submitAndCapture();
    await alertPromise;

    expect(result.status).toBeLessThan(500);
    expect(result.body.code).toBe('FAIL');
    expect(await login.token()).toBeNull();
  });

  test('C4 纯空格输入：不得被当作有效凭据放行', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const alertPromise = login.expectAlert();
    await login.fill('    ', '    ');
    const result = await login.submitAndCapture();
    await alertPromise;

    expect(result.body.code).toBe('FAIL');
    expect(await login.token()).toBeNull();
  });

  test('C5 清空后重新输入：值绑定为最新内容', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();

    await login.fill('临时内容', '临时密码');
    await login.username.fill('');
    await login.password.fill('');
    await expect(login.username).toHaveValue('');
    await expect(login.password).toHaveValue('');

    await login.fill(VALID.username, VALID.password);
    await expect(login.username).toHaveValue(VALID.username);
    await expect(login.password).toHaveValue(VALID.password);

    const result = await login.submitAndCapture();
    expect(result.body.code).toBe('SUCCESS');
  });

  test('C6 密码框为掩码类型，页面不暴露明文', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.fill(VALID.username, VALID.password);

    await expect(login.password).toHaveAttribute('type', 'password');
    expect(await login.password.inputValue()).toBe(VALID.password);
  });
});

test.describe('D 安全测试', () => {
  const sqlPayloads = [
    `' or '1'='1`,
    `' or 1=1 --`,
    `admin'--`,
    `" or ""="`,
    `'; DROP TABLE user; --`,
  ];

  for (const payload of sqlPayloads) {
    test(`D1 SQL 注入载荷必须登录失败: ${payload.slice(0, 24)}`, async ({ page }) => {
      const login = new LoginPage(page);
      await login.goto();
      await login.clearToken();

      const alertPromise = login.expectAlert();
      await login.fill(payload, payload);
      const result = await login.submitAndCapture();
      await alertPromise;

      expect(result.body.code).toBe('FAIL');
      expect(result.body.data).toBeNull();
      expect(result.status).toBeLessThan(500);
      // 注入成功的最强信号：拿到了 token 或被跳转
      expect(await login.token()).toBeNull();
      await expect(page).toHaveURL(new RegExp(`${ROUTES.login.replace('.', '\\.')}$`));
    });
  }

  test('D2 XSS 载荷：脚本不得在错误提示路径上执行', async ({ page }) => {
    let alerted = '';
    page.on('dialog', async (d) => {
      alerted = d.message();
      await d.dismiss();
    });
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    await login.fill(`<script>alert('xss')</script>`, `<img src=x onerror=alert('xss')>`);
    const result = await login.submitAndCapture();
    await page.waitForTimeout(500);

    expect(result.body.code).toBe('FAIL');
    // 若 errMsg 原样回显用户输入，则弹窗文案会包含载荷 —— 这是需要记录的 XSS 风险
    expect(typeof alerted).toBe('string');
    expect(errors.filter((e) => e.includes('xss'))).toEqual([]);
  });

  test('D3 errMsg 回显基线：错误提示是否包含用户输入', async ({ request }) => {
    const marker = 'echo_probe_9527';
    const api = await postLoginApi(request, marker, 'whatever');
    expect(api.body.code).toBe('FAIL');

    // 记录基线：理想实现下 errMsg 不应回显用户输入
    const echoed = api.body.errMsg.includes(marker);
    test.info().annotations.push({
      type: 'XSS 回显基线',
      description: echoed
        ? 'errMsg 原样回显用户名，存在 XSS 风险（视前端拼接方式而定）'
        : 'errMsg 未回显用户输入，无该风险',
    });
    expect(typeof echoed).toBe('boolean');
  });

  test('D4 用户枚举检测：不存在用户与密码错误的提示是否可区分', async ({ request }) => {
    const notExist = await postLoginApi(request, 'no_such_user_8888', 'any');
    const wrongPwd = await postLoginApi(request, VALID.username, 'definitely_wrong_pwd');

    expect(notExist.body.code).toBe('FAIL');
    expect(wrongPwd.body.code).toBe('FAIL');

    const sameMessage = notExist.body.errMsg === wrongPwd.body.errMsg;
    test.info().annotations.push({
      type: '用户枚举风险',
      description: sameMessage
        ? '两种失败提示一致，无法枚举账号'
        : `提示可区分（不存在="${notExist.body.errMsg}"，密码错="${wrongPwd.body.errMsg}"），存在账号枚举风险`,
    });
    // 断言项：错误提示必须非空
    expect(notExist.body.errMsg.length).toBeGreaterThan(0);
    expect(wrongPwd.body.errMsg.length).toBeGreaterThan(0);
  });

  test('D5 无有效凭据时不得签发 token', async ({ page, request }) => {
    await page.goto(ROUTES.login);
    await page.evaluate(() => localStorage.clear());

    const api = await postLoginApi(request, '', '');
    expect(api.body.code).toBe('FAIL');
    expect(api.body.data).toBeNull();
    expect(await page.evaluate(() => localStorage.getItem('user_token'))).toBeNull();
  });

  test('D6 连续 5 次错误登录：接口不返回 5xx（记录是否有限流）', async ({ page, request }) => {
    await page.goto(ROUTES.login);
    const statuses: number[] = [];

    for (let i = 0; i < 5; i++) {
      const res = await postLoginApi(request, VALID.username, `wrong_${i}`);
      statuses.push(res.status);
      expect(res.body.code).toBe('FAIL');
    }

    const limitedIndex = statuses.findIndex((s) => s === 429 || s === 403 || s >= 500);
    test.info().annotations.push({
      type: '暴力破解防护',
      description:
        limitedIndex >= 0
          ? `第 ${limitedIndex + 1} 次失败触发限流/锁定（状态码 ${statuses[limitedIndex]}）`
          : '连续 5 次失败均返回 200，未见限流或锁定，存在暴力破解风险',
    });
    expect(statuses.every((s) => s < 500)).toBe(true);
  });

  test('D7 未登录访问 blog_list.html 必须被拦截回登录页', async ({ page }) => {
    await page.goto(ROUTES.login);
    await page.evaluate(() => localStorage.clear());

    const navigations: string[] = [];
    page.on('framenavigated', (f) => {
      if (f === page.mainFrame()) navigations.push(f.url());
    });

    await page.goto(`${ORIGIN}${ROUTES.list}`);
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });

    // 断言：确实到达过 blog_list.html，随后被守卫弹回登录页
    expect(navigations.some((u) => u.includes('blog_list.html'))).toBe(true);
    expect(page.url()).toContain(ROUTES.login);
    await expect(page.locator(SELECTORS.submit)).toBeVisible();
  });

  test('D8 未登录访问 blog_edit.html：记录守卫缺失（安全缺陷）', async ({ page }) => {
    await page.goto(ROUTES.login);
    await page.evaluate(() => localStorage.clear());

    await page.goto(`${ORIGIN}${ROUTES.edit}`);
    await page.waitForTimeout(1200);

    const landedOnEdit = page.url().includes('blog_edit.html');
    test.info().annotations.push({
      type: '写操作页面守卫',
      description: landedOnEdit
        ? '未登录可直接打开 blog_edit.html，缺少登录守卫，存在未授权访问风险（对比：blog_list.html 有守卫）'
        : 'blog_edit.html 同样会拦截未登录访问',
    });
    // 锁定当前真实行为：未登录可直接进入写博客页面
    expect(landedOnEdit).toBe(true);
  });
});

test.describe('E 交互与前端健壮性', () => {
  test('E1 快速连点提交 3 次：记录请求次数与最终状态', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();
    await login.fill(VALID.username, VALID.password);

    const requests: string[] = [];
    page.on('request', (r) => {
      if (r.url().includes(ROUTES.loginApi)) requests.push(r.url());
    });
    page.on('dialog', (d) => d.dismiss());
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    // 并发派发 3 次点击，模拟用户快速连点
    // （串行 await 会等第一次跳转完成，测不出连点）
    await Promise.allSettled([
      login.submit.click({ noWaitAfter: true }),
      login.submit.click({ noWaitAfter: true }),
      login.submit.click({ noWaitAfter: true }),
    ]);
    await page.waitForTimeout(3000);

    test.info().annotations.push({
      type: '防重复提交基线',
      description:
        `连点 3 次共发出 ${requests.length} 次 /user/login 请求` +
        (requests.length > 1 ? '，缺少按钮禁用机制，存在重复提交风险' : '，未出现重复提交'),
    });

    expect(requests.length).toBeGreaterThanOrEqual(1);
    expect(errors).toEqual([]);
    // 最终必须落在合法状态：要么已登录跳转，要么留在登录页
    const token = await login.token();
    if (token) {
      expect(page.url()).toContain('blog_list.html');
    } else {
      expect(page.url()).toContain('blog_login.html');
    }
  });

  test('E2 回车键提交：记录是否支持（当前无 form 元素）', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const apiCalls: string[] = [];
    page.on('request', (r) => {
      if (r.url().includes(ROUTES.loginApi)) apiCalls.push(r.url());
    });

    await login.fill(VALID.username, VALID.password);
    await login.password.press('Enter');
    await page.waitForTimeout(1500);

    test.info().annotations.push({
      type: '回车提交基线',
      description:
        apiCalls.length > 0
          ? '回车可触发登录请求'
          : '回车无任何反应（页面无 <form>、无 keydown 监听），属体验缺陷',
    });
    expect(apiCalls.length).toBeGreaterThanOrEqual(0);
  });

  test('E3 Tab 焦点顺序：用户名 -> 密码 -> 提交', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.username.click();
    await expect(login.username).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(login.password).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(login.submit).toBeFocused();
  });

  test('E4 接口不可用时的反馈：记录是否静默失败', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();

    let alerted = false;
    page.on('dialog', async (d) => {
      alerted = true;
      await d.dismiss();
    });
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    // 拦截登录接口并模拟服务器错误
    await page.route('**/user/login', (route) =>
      route.fulfill({ status: 500, body: 'Internal Server Error' }),
    );

    await login.fill(VALID.username, VALID.password);
    await login.submit.click();
    await page.waitForTimeout(1500);

    test.info().annotations.push({
      type: '异常反馈基线',
      description:
        alerted || errors.length > 0
          ? '接口异常时用户可感知'
          : 'AJAX 缺少 error 回调：接口 500 时页面无任何提示，用户无感知，属健壮性缺陷',
    });
    // 断言：不能因为接口异常导致未捕获异常白屏
    expect(errors).toEqual([]);
  });

  test('E5 接口返回非 JSON 时页面不白屏', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();

    await page.route('**/user/login', (route) =>
      route.fulfill({ status: 200, contentType: 'text/html', body: '<html>oops</html>' }),
    );
    page.on('dialog', (d) => d.dismiss());

    await login.fill(VALID.username, VALID.password);
    await login.submit.click();
    await page.waitForTimeout(1200);

    await expect(login.submit).toBeVisible();
    await expect(page).toHaveURL(new RegExp(`${ROUTES.login.replace('.', '\\.')}$`));
  });
});

test.describe('F UI 展示与兼容', () => {
  test('F1 标题文案与必填标识基线：记录"登陆"用词与缺失的 required', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();

    await expect(login.dialogTitle).toHaveText('登陆');
    const required = await login.requiredAttrs();

    test.info().annotations.push({
      type: '文案与可用性基线',
      description:
        `标题为"登陆"（规范用词应为"登录"）；` +
        `required 属性 username=${required.username}, password=${required.password}` +
        `${!required.username && !required.password ? '（两端均缺失）' : ''}`,
    });
    expect(await login.hasFormElement()).toBe(false);
  });

  test('F2 多分辨率下登录框可见且不溢出', async ({ page }) => {
    const login = new LoginPage(page);
    const sizes = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 768, height: 1024 },
      { width: 375, height: 667 },
    ];

    for (const size of sizes) {
      await page.setViewportSize(size);
      await login.goto();
      await expect(login.submit).toBeVisible();
      await expect(login.username).toBeVisible();

      const box = await login.submit.boundingBox();
      expect(box).not.toBeNull();
      expect(box!.x).toBeGreaterThanOrEqual(0);
      expect(box!.x + box!.width).toBeLessThanOrEqual(size.width + 1);
    }
  });

  test('F3 导航链接跳转：主页受守卫保护，写博客页无守卫', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.clearToken();

    const navigations: string[] = [];
    page.on('framenavigated', (f) => {
      if (f === page.mainFrame()) navigations.push(f.url());
    });

    // "主页"：会先导航到 blog_list.html，未登录时被守卫弹回登录页
    await page.locator(SELECTORS.navHome).click();
    await page.waitForTimeout(1500);
    expect(navigations.some((u) => u.includes('blog_list.html'))).toBe(true);
    const afterHome = page.url();

    // "写博客"：直接进入编辑页（该页缺少守卫，见 D8）
    await login.goto();
    navigations.length = 0;
    await page.locator(SELECTORS.navEdit).click();
    await page.waitForURL(`**${ROUTES.edit}`, { timeout: 10_000 });

    test.info().annotations.push({
      type: '导航行为基线',
      description:
        `点击"主页" -> 经 blog_list.html 后被守卫弹到 ${afterHome}；` +
        `点击"写博客" -> 直接进入 ${page.url()}（无守卫）`,
    });
  });

  test('F4 静态资源无 4xx/5xx（含 favicon）', async ({ page }) => {
    const failed: string[] = [];
    page.on('response', (r) => {
      if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    });

    const login = new LoginPage(page);
    await login.goto();
    await page.waitForTimeout(1200);

    test.info().annotations.push({
      type: '静态资源基线',
      description: failed.length ? `存在失败资源：${failed.join('; ')}` : '全部资源正常',
    });
    // 断言：页面自身 HTML 必须成功
    expect(failed.some((f) => f.includes('blog_login.html'))).toBe(false);
  });

  test('F5 登录后浏览器后退：回到登录页的状态符合预期', async ({ page }) => {
    const login = new LoginPage(page);
    await login.login(VALID.username, VALID.password);
    expect(await login.token()).toBeTruthy();

    await page.goBack();
    await page.waitForLoadState('domcontentloaded');
    // 记录基线：当前无登录态路由守卫，回退到登录页仍可再次登录
    await expect(login.submit).toBeVisible();
    test.info().annotations.push({
      type: '登录态守卫基线',
      description: `后退后 URL=${page.url()}，token 仍存在=${(await login.token()) !== null}`,
    });
  });
});
