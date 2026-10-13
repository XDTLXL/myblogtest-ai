import { Page, Locator, expect, APIRequestContext } from '@playwright/test';

/** 测试账号，可用环境变量覆盖 */
export const CREDENTIALS = {
  username: process.env.LOGIN_USERNAME || 'zhangsan',
  password: process.env.LOGIN_PASSWORD || '123456',
};

export const ROUTES = {
  login: '/blog_login.html',
  list: '/blog_list.html',
  edit: '/blog_edit.html',
  detail: '/blog_detail.html',
  listApi: '/blog/getList',
  userInfoApi: '/user/getUserInfo',
  loginApi: '/user/login',
};

export const ORIGIN = process.env.BASE_URL || 'http://127.0.0.1:9090';

/** 鉴权请求头名称（实测：common.js 通过 ajaxSend 注入该头） */
export const TOKEN_HEADER = 'user_token_header';

export const SELECTORS = {
  navHome: '.nav a[href="blog_list.html"]',
  navEdit: '.nav a[href="blog_edit.html"]',
  navLogout: '.nav a[onclick="logout()"]',
  card: '.left .card',
  cardName: '.left .card h3',
  cardAvatar: '.left .card img',
  cardLink: '.left .card a',
  cardRows: '.left .card .row',
  right: '.container .right',
  blog: '.container .right .blog',
  blogTitle: '.container .right .blog .title',
  blogDate: '.container .right .blog .date',
  blogDesc: '.container .right .blog .desc',
  blogDetail: '.container .right .blog .detail',
};

/** 博客列表项结构（实测字段） */
export interface BlogItem {
  id: number;
  title: string;
  content: string;
  userId: number;
  deleteFlag: number;
  createTime: string;
  updateTime?: string;
  loginUser: boolean;
}

/** 构造一条博客数据，便于用例覆盖指定字段 */
export function makeBlog(overrides: Partial<BlogItem> = {}): BlogItem {
  return {
    id: 32213,
    title: '博客标题',
    content: '博客内容',
    userId: 3,
    deleteFlag: 0,
    createTime: '2025-03-18 11:41',
    loginUser: false,
    ...overrides,
  };
}

/** 列表页 Page Object */
export class ListPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // ---------- 定位器 ----------
  get right(): Locator { return this.page.locator(SELECTORS.right); }
  get blogs(): Locator { return this.page.locator(SELECTORS.blog); }
  get cardName(): Locator { return this.page.locator(SELECTORS.cardName); }
  get cardAvatar(): Locator { return this.page.locator(SELECTORS.cardAvatar); }
  get cardLink(): Locator { return this.page.locator(SELECTORS.cardLink); }
  get logoutLink(): Locator { return this.page.locator(SELECTORS.navLogout); }

  // ---------- 登录态 ----------
  /** 通过界面完成登录并落到列表页 */
  async login(): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.page.fill('#username', CREDENTIALS.username);
    await this.page.fill('#password', CREDENTIALS.password);
    await this.page.click('#submit');
    await this.page.waitForURL(`**${ROUTES.list}`, { timeout: 15_000 });
  }

  /** 直接向 localStorage 写入 token（可传入伪造值） */
  async setToken(token: string): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.page.evaluate((t) => localStorage.setItem('user_token', t), token);
  }

  async clearToken(): Promise<void> {
    await this.page.evaluate(() => localStorage.clear());
  }

  async token(): Promise<string | null> {
    return this.page.evaluate(() => localStorage.getItem('user_token'));
  }

  /** 获取真实 token（用于接口层校验） */
  async realToken(): Promise<string> {
    const api = await this.page.request.post(ROUTES.loginApi, {
      form: { username: CREDENTIALS.username, password: CREDENTIALS.password },
    });
    const body = await api.json();
    return body.data as string;
  }

  // ---------- 页面操作 ----------
  /** 打开列表页并等待列表渲染完成（或按期望等待跳转） */
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.list);
  }

  /** 等待列表渲染出至少一条博客 */
  async waitForList(): Promise<void> {
    await this.blogs.first().waitFor({ state: 'visible', timeout: 10_000 });
  }

  async blogCount(): Promise<number> {
    return this.blogs.count();
  }

  async titles(): Promise<string[]> {
    return this.blogs.locator('.title').allInnerTexts();
  }

  async dates(): Promise<string[]> {
    return this.blogs.locator('.date').allInnerTexts();
  }

  async descs(): Promise<string[]> {
    return this.blogs.locator('.desc').allInnerTexts();
  }

  async detailHrefs(): Promise<(string | null)[]> {
    return this.blogs.locator('.detail').evaluateAll(
      (els) => els.map((e) => e.getAttribute('href')),
    );
  }

  /** 注销并等待跳转 */
  async logout(): Promise<void> {
    await this.logoutLink.click();
    await this.page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });
  }

  /** 拦截 getList，返回指定数据 */
  async mockList(data: unknown, code = 'SUCCESS', status = 200): Promise<void> {
    await this.page.route(`**${ROUTES.listApi}`, (route) =>
      route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({ code, errMsg: code === 'SUCCESS' ? '' : '服务器开小差了', data }),
      }),
    );
  }

  /** 拦截 getUserInfo */
  async mockUserInfo(data: unknown, code = 'SUCCESS', status = 200): Promise<void> {
    await this.page.route(`**${ROUTES.userInfoApi}`, (route) =>
      route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({ code, errMsg: code === 'SUCCESS' ? '' : '获取用户信息失败', data }),
      }),
    );
  }

  /** 注册一次性 alert 监听 */
  expectAlert(): Promise<string> {
    return new Promise<string>((resolve) => {
      this.page.once('dialog', async (d) => {
        const msg = d.message();
        await d.dismiss();
        resolve(msg);
      });
    });
  }

  /** 记录页面跳转链路 */
  trackNavigations(): string[] {
    const navs: string[] = [];
    this.page.on('framenavigated', (f) => {
      if (f === this.page.mainFrame()) navs.push(f.url());
    });
    return navs;
  }
}

/** 以指定 token 直接请求列表接口（接口层鉴权校验） */
export async function getListApi(
  request: APIRequestContext,
  token: string | null,
  headerName: string = TOKEN_HEADER,
): Promise<{ status: number; body: any }> {
  const headers: Record<string, string> = {};
  if (token !== null) headers[headerName] = token;
  const res = await request.get(ROUTES.listApi, { headers });
  const text = await res.text();
  let body: any;
  try {
    body = JSON.parse(text);
  } catch {
    body = text;
  }
  return { status: res.status(), body };
}

/** 以指定 token 请求用户信息接口 */
export async function getUserInfoApi(
  request: APIRequestContext,
  token: string | null,
): Promise<{ status: number; body: any }> {
  const headers: Record<string, string> = {};
  if (token !== null) headers[TOKEN_HEADER] = token;
  const res = await request.get(ROUTES.userInfoApi, { headers });
  const text = await res.text();
  let body: any;
  try {
    body = JSON.parse(text);
  } catch {
    body = text;
  }
  return { status: res.status(), body };
}
