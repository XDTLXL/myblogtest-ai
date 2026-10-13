import { Page, Locator, APIRequestContext } from '@playwright/test';

export const CREDENTIALS = {
  username: process.env.LOGIN_USERNAME || 'zhangsan',
  password: process.env.LOGIN_PASSWORD || '123456',
};

export const ROUTES = {
  login: '/blog_login.html',
  list: '/blog_list.html',
  edit: '/blog_edit.html',
  update: '/blog_update.html',
  detail: '/blog_detail.html',
  detailApi: '/blog/getBlogDetail',
  authorApi: '/user/getAuthorInfo',
  deleteApi: '/blog/delete',
  updateApi: '/blog/update',
  addApi: '/blog/add',
  listApi: '/blog/getList',
  loginApi: '/user/login',
};

export const ORIGIN = process.env.BASE_URL || 'http://127.0.0.1:9090';
export const TOKEN_HEADER = 'user_token_header';

/** 环境中已有的示例博客 id（仅用于只读验证，不做任何修改） */
export const SAMPLE_BLOG_ID = Number(process.env.SAMPLE_BLOG_ID || 32213);

/** 测试博客标题标记，用于识别与清理 */
export const MARKER = '__E2E_DETAIL__';

export const SELECTORS = {
  navHome: '.nav a[href="blog_list.html"]',
  navEdit: '.nav a[href="blog_edit.html"]',
  navLogout: '.nav a[onclick="logout()"]',
  card: '.left .card',
  cardName: '.left .card h3',
  cardAvatar: '.left .card img',
  cardLink: '.left .card a',
  cardRows: '.left .card .row',
  contentTitle: '.content .title',
  contentDate: '.content .date',
  contentDetail: '.content .detail',
  operating: '.content .operating',
  editBtn: '.content .operating button:has-text("编辑")',
  deleteBtn: '.content .operating button:has-text("删除")',
};

/** 详情接口返回的数据结构（实测） */
export interface BlogDetail {
  id: number;
  title: string;
  content: string;
  userId: number;
  deleteFlag: number;
  createTime: string;
  updateTime?: string;
  loginUser: boolean;
}

/** 详情页 Page Object */
export class DetailPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  get titleText(): Locator { return this.page.locator(SELECTORS.contentTitle); }
  get dateText(): Locator { return this.page.locator(SELECTORS.contentDate); }
  get detail(): Locator { return this.page.locator(SELECTORS.contentDetail); }
  get operating(): Locator { return this.page.locator(SELECTORS.operating); }
  get editButton(): Locator { return this.page.locator(SELECTORS.editBtn); }
  get deleteButton(): Locator { return this.page.locator(SELECTORS.deleteBtn); }

  // ---------- 登录态 ----------
  async login(username = CREDENTIALS.username, password = CREDENTIALS.password): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.page.fill('#username', username);
    await this.page.fill('#password', password);
    await this.page.click('#submit');
    await this.page.waitForURL(`**${ROUTES.list}`, { timeout: 15_000 });
  }

  async token(): Promise<string | null> {
    return this.page.evaluate(() => localStorage.getItem('user_token'));
  }

  async setToken(token: string): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.page.evaluate((t) => localStorage.setItem('user_token', t), token);
  }

  async clearToken(): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.page.evaluate(() => localStorage.clear());
  }

  // ---------- 页面 ----------
  /** 打开详情页（不可用 goto 后再读 token，守卫会跳转） */
  async open(blogId: number | string): Promise<void> {
    await this.page.goto(`${ROUTES.detail}?blogId=${blogId}`);
    await this.page.waitForTimeout(1200);
  }

  async openRaw(query: string): Promise<void> {
    await this.page.goto(`${ROUTES.detail}${query}`);
    await this.page.waitForTimeout(1800);
  }

  async waitForDetail(): Promise<void> {
    await this.page.waitForFunction(
      () => {
        const el = document.querySelector('.content .title');
        return !!el && (el as HTMLElement).innerText.trim().length > 0;
      },
      { timeout: 10_000 },
    );
  }

  /** 读取当前渲染出的操作按钮文案 */
  async operationButtons(): Promise<string[]> {
    return this.page.locator(`${SELECTORS.operating} button`).allInnerTexts();
  }

  /** 读取卡片计数行 */
  async cardCounts(): Promise<string[]> {
    return this.page.locator(SELECTORS.cardRows).allInnerTexts();
  }

  /** 注册一次性确认框监听，返回 Promise<文案>；accept 决定是否确认 */
  handleDialog(accept: boolean): Promise<string> {
    return new Promise<string>((resolve) => {
      this.page.once('dialog', async (d) => {
        const msg = d.message();
        if (accept) await d.accept();
        else await d.dismiss();
        resolve(msg);
      });
    });
  }

  /** 收集所有弹窗文案（自动关闭） */
  collectDialogs(): string[] {
    const msgs: string[] = [];
    this.page.on('dialog', async (d) => {
      msgs.push(d.message());
      await d.dismiss();
    });
    return msgs;
  }

  // ---------- 接口层 ----------
  async getDetail(request: APIRequestContext, blogId: number | string, token: string | null): Promise<{ status: number; body: any }> {
    const headers: Record<string, string> = {};
    if (token !== null) headers[TOKEN_HEADER] = token;
    const res = await request.get(`${ROUTES.detailApi}?blogId=${blogId}`, { headers });
    const text = await res.text();
    let body: any;
    try { body = JSON.parse(text); } catch { body = text; }
    return { status: res.status(), body };
  }

  async getAuthor(request: APIRequestContext, blogId: number | string, token: string | null): Promise<{ status: number; body: any }> {
    const headers: Record<string, string> = {};
    if (token !== null) headers[TOKEN_HEADER] = token;
    const res = await request.get(`${ROUTES.authorApi}?blogId=${blogId}`, { headers });
    const text = await res.text();
    let body: any;
    try { body = JSON.parse(text); } catch { body = text; }
    return { status: res.status(), body };
  }

  async listBlogs(request: APIRequestContext, token: string): Promise<any[]> {
    const res = await request.get(ROUTES.listApi, { headers: { [TOKEN_HEADER]: token } });
    const body = await res.json();
    return Array.isArray(body.data) ? body.data : [];
  }

  // ---------- 测试数据管理（务必清理） ----------
  /** 创建专属测试博客，返回其 id */
  async createTestBlog(request: APIRequestContext, token: string, suffix = ''): Promise<number> {
    const res = await request.post(ROUTES.addApi, {
      headers: { 'Content-Type': 'application/json', [TOKEN_HEADER]: token },
      data: JSON.stringify({ title: `${MARKER}${suffix} 标题`, content: `${MARKER}${suffix} 正文` }),
    });
    expectOk(await res.json());
    await this.page.waitForTimeout(600);

    const blogs = await this.listBlogs(request, token);
    const found = blogs.find((b) => String(b.title).includes(`${MARKER}${suffix}`));
    if (!found) throw new Error('测试博客创建后未在列表中找到');
    return found.id;
  }

  /** 删除指定博客（用于清理），忽略失败 */
  async deleteBlog(request: APIRequestContext, token: string, blogId: number): Promise<void> {
    try {
      await request.post(`${ROUTES.deleteApi}?blogId=${blogId}`, {
        headers: { [TOKEN_HEADER]: token },
      });
      await this.page.waitForTimeout(400);
    } catch {
      /* 清理失败不掩盖原始断言 */
    }
  }

  /** 删除所有带测试标记的博客，保证环境干净 */
  async cleanupTestBlogs(request: APIRequestContext, token: string): Promise<number> {
    const blogs = await this.listBlogs(request, token);
    const mine = blogs.filter((b) => String(b.title).includes(MARKER));
    for (const b of mine) {
      await this.deleteBlog(request, token, b.id);
    }
    return mine.length;
  }
}

function expectOk(body: any): void {
  if (!body || body.code !== 'SUCCESS' || body.data !== true) {
    throw new Error(`创建测试博客失败: ${JSON.stringify(body)}`);
  }
}
