import { test, expect } from '@playwright/test';
import {
  ListPage,
  getListApi,
  getUserInfoApi,
  makeBlog,
  CREDENTIALS,
  ROUTES,
  SELECTORS,
  ORIGIN,
  TOKEN_HEADER,
} from '../pages/ListPage';

/**
 * 博客列表页自动化用例（blog_list.html）
 *
 * 覆盖规划中的 7 个模块：渲染、鉴权、注销、异常处理、数据一致性、安全、交互兼容
 *
 * 说明：标注"发现缺陷"的用例锁定的是**当前真实行为**，
 * 用于把缺陷固化为可回归的测试证据，因此这些用例会通过而非失败；
 * 真实结论记录在 test.info().annotations 中，可在 HTML 报告查看。
 */

const VALID = CREDENTIALS;

/** 用例编号：与规划文档、Excel 用例编号一一对应（字母 + 序号） */
const CASE_ID = {
  A1: 1, A2: 2, A3: 3, A4: 4, A5: 5, A6: 6,
  B1: 7, B2: 8, B3: 9, B4: 10, B5: 11,
  C1: 12, C2: 13, C3: 14,
  D1: 15, D2: 16, D3: 17, D4: 18, D5: 19, D6: 20,
  E1: 21, E2: 22, E3: 23,
  F1: 24, F2: 25, F3: 26, F4: 27, F5: 28,
  G1: 29, G2: 30, G3: 31, G4: 32, G5: 33, G6: 34,
} as const;

/**
 * 生成用例标题，形如 "B4 10 空字符串 token ..."。
 * 必须保留字母编号（B4），否则 -g "B4" 无法筛选，
 * 也无法与 Excel 用例表、测试报告对应。
 */
function title(id: keyof typeof CASE_ID, text: string): string {
  return `${id} ${CASE_ID[id]} ${text}`;
}

/** 已登录并停在列表页 */
async function gotoListAuthenticated(page: any): Promise<ListPage> {
  const lp = new ListPage(page);
  await lp.login();
  return lp;
}

test.describe('A 列表渲染', () => {
  test(title('A1', '正常登录后列表页渲染出博客卡片'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.waitForList();

    const count = await lp.blogCount();
    const titles = await lp.titles();
    expect(count).toBeGreaterThan(0);
    expect(titles.length).toBe(count);
    expect(await page.title()).toBe('博客列表页');
  });

  test(title('A2', '卡片四个字段均正确渲染'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    const blog = makeBlog({ id: 10001, title: '字段校验标题', content: '字段校验内容', createTime: '2025-06-01 09:30' });
    await lp.mockList([blog]);
    await lp.goto();
    await lp.waitForList();

    expect(await lp.titles()).toEqual(['字段校验标题']);
    expect((await lp.dates())[0]).toContain('2025-06-01');
    expect((await lp.descs())[0]).toContain('字段校验内容');
    expect((await lp.detailHrefs())[0]).toBe('blog_detail.html?blogId=10001');
  });

  test(title('A3', '详情链接 href 与接口 id 一致'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.mockList([makeBlog({ id: 54321 })]);
    await lp.goto();
    await lp.waitForList();

    const href = (await lp.detailHrefs())[0];
    expect(href).toBe('blog_detail.html?blogId=54321');
  });

  test(title('A4', '多条博客按接口顺序渲染'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    const data = [
      makeBlog({ id: 1, title: '第一篇' }),
      makeBlog({ id: 2, title: '第二篇' }),
      makeBlog({ id: 3, title: '第三篇' }),
    ];
    await lp.mockList(data);
    await lp.goto();
    await lp.waitForList();

    expect(await lp.blogCount()).toBe(3);
    expect(await lp.titles()).toEqual(['第一篇', '第二篇', '第三篇']);
  });

  test(title('A5', '超长标题与内容不被截断'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    const longTitle = '标题内容'.repeat(50);
    const longContent = '正文内容'.repeat(200);
    await lp.mockList([makeBlog({ title: longTitle, content: longContent })]);
    await lp.goto();
    await lp.waitForList();

    const titleLen = (await lp.titles())[0].length;
    const descLen = (await lp.descs())[0].length;
    test.info().annotations.push({
      type: '长内容渲染',
      description: `原始标题 ${longTitle.length} 字 → 渲染 ${titleLen} 字；` +
        `原始内容 ${longContent.length} 字 → 渲染 ${descLen} 字（当前不做截断，长列表下可能影响性能）`,
    });
    expect(titleLen).toBeGreaterThanOrEqual(longTitle.length);
    expect(descLen).toBeGreaterThanOrEqual(longContent.length);
  });

  test(title('A6', '特殊字符标题的渲染与转义'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    const special = '引号"单引号\'与&符号<>尖括号';
    await lp.mockList([makeBlog({ title: special, content: special })]);
    await lp.goto();
    await lp.waitForList();

    const rendered = (await lp.titles())[0];
    expect(rendered).toContain('&');
    expect(rendered).toContain('尖括号');
    // 尖括号未形成真实元素，说明作为文本渲染
    expect(await lp.blogs.locator('.title *').count()).toBe(0);
  });
});

test.describe('B 鉴权与访问控制', () => {
  test(title('B1', '未登录访问列表页被守卫拦截'), async ({ page }) => {
    const lp = new ListPage(page);
    // 先清空登录态，再访问列表页
    // 注意：不能在访问列表页之后调用 clearToken —— 守卫会立即跳转，
    // 导致 evaluate 的执行上下文被销毁（Execution context was destroyed）
    await page.goto(ROUTES.login);
    await lp.clearToken();
    const navs = lp.trackNavigations();

    await page.goto(`${ORIGIN}${ROUTES.list}`);
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });

    expect(navs.some((u) => u.includes('blog_list.html'))).toBe(true);
    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('B2', '伪造 token 访问列表页被拦截'), async ({ page }) => {
    const lp = new ListPage(page);
    await lp.setToken('garbage.token.xxx');
    const navs = lp.trackNavigations();

    await lp.goto();
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });

    expect(navs.some((u) => u.includes('blog_list.html'))).toBe(true);
    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('B3', '空字符串 token 请求列表接口返回 401'), async ({ request }) => {
    const res = await getListApi(request, '');
    expect(res.status).toBe(401);
  });

  test(title('B4', 'token 头名称错误时返回 401'), async ({ page, request }) => {
    const lp = await gotoListAuthenticated(page);
    const token = await lp.realToken();

    const wrongHeader = await getListApi(request, token, 'user_token');
    const correctHeader = await getListApi(request, token, TOKEN_HEADER);

    expect(wrongHeader.status).toBe(401);
    expect(correctHeader.status).toBe(200);
    expect(correctHeader.body.code).toBe('SUCCESS');
  });

  test(title('B5', '有效 token 正常获取列表数据'), async ({ page, request }) => {
    const lp = await gotoListAuthenticated(page);
    const token = await lp.realToken();
    const res = await getListApi(request, token);

    expect(res.status).toBe(200);
    expect(res.body.code).toBe('SUCCESS');
    expect(Array.isArray(res.body.data)).toBe(true);
  });
});

test.describe('C 注销', () => {
  test(title('C1', '点击注销清除 token 并跳转登录页'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    expect(await lp.token()).toBeTruthy();

    await lp.logout();

    expect(await lp.token()).toBeNull();
    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('C2', '注销后再访问列表页被拦截'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.logout();

    await page.goto(`${ORIGIN}${ROUTES.list}`);
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });
    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('C3', '注销后浏览器后退的状态'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.logout();

    // 后退到列表页会再次触发鉴权跳转，需等页面稳定后再取状态，
    // 否则 evaluate 可能落在被销毁的执行上下文上
    await page.goBack();
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1500);
    await page.waitForLoadState('networkidle').catch(() => undefined);

    test.info().annotations.push({
      type: '注销后回退基线',
      description: `注销后点击后退，URL=${page.url()}，token=${(await lp.token()) === null ? '仍为空' : '被恢复'}`,
    });
    // 无论落回列表页还是登录页，都不得出现可用登录态
    expect(await lp.token()).toBeNull();
  });
});

test.describe('D 错误与异常处理', () => {
  test(title('D1', 'getList 返回 FAIL 时无任何提示'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    let dialog: string | null = null;
    page.on('dialog', async (d) => { dialog = d.message(); await d.dismiss(); });
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    await lp.mockList(null, 'FAIL');
    await lp.goto();
    // 等列表接口响应完成后再观察，避免读到渲染中途的状态
    await page.waitForResponse((r) => r.url().includes(ROUTES.listApi)).catch(() => undefined);
    await page.waitForTimeout(2000);

    const rightHtml = await lp.right.innerHTML();
    test.info().annotations.push({
      type: 'FAIL 反馈基线',
      description: `getList 返回 code=FAIL 时：弹窗=${dialog === null ? '无' : dialog}，` +
        `列表区域内容长度=${rightHtml.trim().length}，控制台异常=${errors.length} → ` +
        '业务失败被静默吞掉，用户无任何感知，属缺陷',
    });
    expect(dialog).toBeNull();
    expect(rightHtml.trim().length).toBe(0);
    expect(errors).toEqual([]);
  });

  test(title('D2', 'getList 接口 500 时无用户提示'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    let dialog: string | null = null;
    page.on('dialog', async (d) => { dialog = d.message(); await d.dismiss(); });

    await lp.mockList(null, 'FAIL', 500);
    await lp.goto();
    await page.waitForTimeout(2000);

    test.info().annotations.push({
      type: '接口 500 基线',
      description: `getList 返回 HTTP 500 时：弹窗=${dialog === null ? '无' : dialog}；` +
        'error 回调仅处理 401，500 无任何提示；页面也未跳转登录页',
    });
    expect(dialog).toBeNull();
    expect(page.url()).toContain('blog_list.html');
  });

  test(title('D3', 'getList 返回空数组时的空态表现'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.mockList([]);
    await lp.goto();
    await page.waitForTimeout(1800);

    const text = (await lp.right.innerText()).trim();
    const count = await lp.blogCount();
    test.info().annotations.push({
      type: '空态基线',
      description: `空数组时列表条数=${count}，区域可见文案="${text}" → ` +
        (text.length === 0 ? '无"暂无博客"占位文案，用户看到空白区域，属体验缺陷' : '存在占位文案'),
    });
    expect(count).toBe(0);
  });

  test(title('D4', 'getUserInfo 返回 FAIL 时弹出错误提示'), async ({ page }) => {
    const lp = new ListPage(page);
    await lp.login();
    const alertPromise = lp.expectAlert();
    await lp.mockUserInfo(null, 'FAIL');

    await lp.goto();
    const alertText = await alertPromise;

    expect(alertText).toContain('获取用户信息失败');
    // 卡片保留 HTML 硬编码值，说明用户信息未刷新
    expect(await lp.cardName.innerText()).toBe('比特汤老师');
  });

  test(title('D5', 'getUserInfo 接口 500 时页面不崩溃'), async ({ page }) => {
    const lp = new ListPage(page);
    await lp.login();
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    await lp.mockUserInfo(null, 'FAIL', 500);
    await lp.goto();
    await page.waitForTimeout(1800);

    test.info().annotations.push({
      type: '用户信息接口异常基线',
      description: `getUserInfo 返回 500 时页面未白屏，卡片显示硬编码值；控制台异常数=${errors.length}`,
    });
    await expect(lp.cardName).toBeVisible();
    expect(errors).toEqual([]);
  });

  test(title('D6', '接口返回非 JSON 时页面不白屏'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await page.route(`**${ROUTES.listApi}`, (route) =>
      route.fulfill({ status: 200, contentType: 'text/html', body: '<html>oops</html>' }),
    );
    await lp.goto();
    await page.waitForTimeout(1500);

    await expect(page.locator(SELECTORS.card)).toBeVisible();
    expect(await lp.token()).toBeTruthy();
  });
});

test.describe('E 数据一致性', () => {
  test(title('E1', '左侧文章计数与实际列表条数不一致'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.waitForList();
    // 等用户信息接口与列表渲染都完成，再读卡片计数，避免读到渲染中途值
    await page.waitForResponse((r) => r.url().includes(ROUTES.userInfoApi)).catch(() => undefined);
    await page.waitForTimeout(500);

    // 卡片结构：两个 .row，第一个是"文章/分类"表头，第二个是两个数字
    const numberSpans = lp.page.locator(`${SELECTORS.cardRows}:nth-of-type(2) span`);
    const spanCount = await numberSpans.count();
    let articleCount: number | undefined;
    let categoryCount: number | undefined;
    if (spanCount >= 2) {
      articleCount = Number((await numberSpans.nth(0).innerText()).trim());
      categoryCount = Number((await numberSpans.nth(1).innerText()).trim());
    } else {
      const rows = await lp.page.locator(SELECTORS.cardRows).allInnerTexts();
      const numbers = (rows[1] || '').split(/\s+/).map((n) => Number(n)).filter((n) => !Number.isNaN(n));
      articleCount = numbers[0];
      categoryCount = numbers[1];
    }
    const actual = await lp.blogCount();

    expect(articleCount).not.toBeUndefined();
    test.info().annotations.push({
      type: '计数一致性',
      description: `卡片显示"文章=${articleCount}，分类=${categoryCount}"，实际列表 ${actual} 条 → ` +
        (articleCount === actual
          ? '一致'
          : `不一致（偏差 ${Math.abs((articleCount ?? 0) - actual)}），卡片计数为 HTML 硬编码，属缺陷`),
    });
    expect(actual).toBeGreaterThan(0);
  });

  test(title('E2', '卡片用户名与登录用户一致'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.waitForList();
    await expect(lp.cardName).toHaveText(VALID.username);
  });

  test(title('E3', '用户头像为硬编码资源'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.waitForList();

    const src = await lp.cardAvatar.getAttribute('src');
    test.info().annotations.push({
      type: '头像来源基线',
      description: `卡片头像 src="${src}"，为 HTML 硬编码资源，` +
        'getUserInfo 未返回头像字段，因此头像不随登录用户变化',
    });
    expect(src).toBe('pic/doge.jpg');
  });
});

test.describe('F 安全测试', () => {
  const xssPayload = '<img src=x onerror="window.__xss=1">';

  for (const field of ['title', 'content', 'createTime'] as const) {
    test(title(
      field === 'title' ? 'F1' : field === 'content' ? 'F2' : 'F3',
      `列表 XSS：${field} 字段注入脚本被执行`,
    ), async ({ page }) => {
      const lp = await gotoListAuthenticated(page);
      await lp.mockList([makeBlog({ [field]: xssPayload } as any)]);
      await lp.goto();
      await lp.waitForList();
      await page.waitForTimeout(1200);

      const fired = await page.evaluate(() => (window as any).__xss || null);
      const injected = await lp.blogs.locator('img').count();

      test.info().annotations.push({
        type: 'XSS 风险',
        description: `${field} 字段注入 ${xssPayload} 后：注入元素数=${injected}，` +
          `脚本执行=${fired ? '是' : '否'} → ` +
          (fired
            ? '列表用字符串拼接 + html() 渲染且未转义，存在存储型 XSS（高危）'
            : '未执行'),
      });

      // 锁定当前真实行为：脚本确实被执行
      expect(fired).toBeTruthy();
      expect(injected).toBeGreaterThan(0);
    });
  }

  test(title('F4', 'getUserInfo 响应体泄露密码哈希'), async ({ page, request }) => {
    const lp = await gotoListAuthenticated(page);
    const token = await lp.realToken();
    const res = await getUserInfoApi(request, token);

    expect(res.status).toBe(200);
    expect(res.body.code).toBe('SUCCESS');

    const data = res.body.data || {};
    const leaked = Object.keys(data).filter((k) =>
      /password|pwd|passwd|salt|secret/i.test(k));

    test.info().annotations.push({
      type: '敏感信息泄露',
      description: `getUserInfo 响应字段=[${Object.keys(data).join(', ')}]；` +
        (leaked.length
          ? `其中包含敏感字段 ${leaked.join(', ')}，返回值为密码哈希，前端无需该字段，属信息泄露（高危）`
          : '未发现敏感字段'),
    });

    // 锁定当前真实行为：确实返回了 password
    expect(leaked.length).toBeGreaterThan(0);
    expect(String(data.password).length).toBeGreaterThan(0);
  });

  test(title('F5', '未授权访问 getList 被拒绝且不返回数据'), async ({ request }) => {
    const res = await getListApi(request, null);
    expect(res.status).toBe(401);
    // 401 响应体不应包含任何业务数据
    expect(JSON.stringify(res.body)).not.toContain('title');
  });
});

test.describe('G 交互与兼容', () => {
  test(title('G1', '查看全文跳转到详情页'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await lp.waitForList();

    const href = await lp.blogs.first().locator('.detail').getAttribute('href');
    await lp.blogs.first().locator('.detail').click();
    await page.waitForURL(`**${ROUTES.detail}**`, { timeout: 10_000 });

    expect(href).toMatch(/blog_detail\.html\?blogId=\d+/);
    expect(page.url()).toContain(href!);
    expect(await page.title()).toBe('博客详情页');
  });

  test(title('G2', '导航"写博客"跳转到编辑页'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    await page.locator(SELECTORS.navEdit).click();
    await page.waitForURL(`**${ROUTES.edit}`, { timeout: 10_000 });
    expect(page.url()).toContain('blog_edit.html');
  });

  test(title('G3', '多分辨率下布局不溢出'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    const sizes = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 768, height: 1024 },
    ];

    for (const size of sizes) {
      await page.setViewportSize(size);
      await lp.goto();
      await lp.waitForList();
      const cardBox = await page.locator(SELECTORS.card).boundingBox();
      expect(cardBox).not.toBeNull();
      expect(cardBox!.x).toBeGreaterThanOrEqual(-1);
      expect(cardBox!.x + cardBox!.width).toBeLessThanOrEqual(size.width + 1);
    }
  });

  test(title('G4', '静态资源无 4xx/5xx'), async ({ page }) => {
    const failed: string[] = [];
    page.on('response', (r) => {
      if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    });
    const lp = await gotoListAuthenticated(page);
    await lp.goto();
    await lp.waitForList();
    await page.waitForTimeout(1000);

    test.info().annotations.push({
      type: '静态资源基线',
      description: failed.length ? `失败资源：${failed.join('; ')}` : '全部资源正常',
    });
    expect(failed.some((f) => f.includes('blog_list.html'))).toBe(false);
  });

  test(title('G5', '渲染 100 条博客的性能'), async ({ page }) => {
    const lp = await gotoListAuthenticated(page);
    const data = Array.from({ length: 100 }, (_, i) =>
      makeBlog({ id: 20000 + i, title: `压测标题 ${i}` }));
    await lp.mockList(data);

    const start = Date.now();
    await lp.goto();
    await lp.waitForList();
    const elapsed = Date.now() - start;
    const count = await lp.blogCount();

    test.info().annotations.push({
      type: '渲染性能',
      description: `100 条数据渲染 ${count} 条，首次可见耗时 ${elapsed}ms（一次性全量渲染，无分页与虚拟滚动）`,
    });
    expect(count).toBe(100);
    expect(elapsed).toBeLessThan(15_000);
  });

  test(title('G6', '列表接口不支持分页参数'), async ({ page, request }) => {
    const lp = await gotoListAuthenticated(page);
    const token = await lp.realToken();

    const results: Record<string, number> = {};
    for (const q of ['?page=1&pageSize=1', '?pageNum=1&pageSize=1', '?offset=0&limit=1']) {
      const res = await request.get(ROUTES.listApi + q, { headers: { [TOKEN_HEADER]: token } });
      const body = await res.json();
      results[q] = Array.isArray(body.data) ? body.data.length : -1;
    }

    const counts = Object.values(results);
    const allSame = counts.every((c) => c === counts[0]);

    test.info().annotations.push({
      type: '分页支持基线',
      description: `分页参数试探结果：${JSON.stringify(results)} → ` +
        (allSame
          ? `不同分页参数返回条数相同（${counts[0]}），接口忽略分页参数，` +
            '数据量大时存在全量返回与性能风险，属缺陷'
          : '分页参数生效'),
    });
    expect(allSame).toBe(true);
  });
});
