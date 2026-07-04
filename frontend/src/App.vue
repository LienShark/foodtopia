<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import {
  clearToken,
  createSurpriseBag,
  getCurrentMerchantUser,
  getPublicSurpriseBag,
  getToken,
  listMerchantSurpriseBags,
  listPublicMerchantSurpriseBags,
  listPublicSurpriseBags,
  loginEmail,
  loginLine,
  registerMerchant,
  setToken,
  type DescriptionMode,
  type MerchantUserRead,
  type PublicSurpriseBagRead,
  type SurpriseBagCreate,
  type SurpriseBagRead,
} from "./api";

type ViewName = "public" | "merchant" | "register";

const activeView = ref<ViewName>("public");
const busy = ref(false);
const emailLoginBusy = ref(false);
const lineLoginBusy = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const currentUser = ref<MerchantUserRead | null>(null);
const merchantBags = ref<SurpriseBagRead[]>([]);
const publicBags = ref<PublicSurpriseBagRead[]>([]);
const selectedBag = ref<PublicSurpriseBagRead | null>(null);

const emailLoginForm = reactive({
  email: "",
  password: "",
});

const lineLoginForm = reactive({
  line_user_id: "",
});

const registerForm = reactive({
  approval_code: "FOODTOPIA2026",
  merchant: {
    name: "",
    google_place_id: "",
    address: "",
    lat: 24.786,
    lng: 120.999,
    phone: "",
    business_type: "breakfast",
  },
  owner: {
    name: "",
    phone: "",
    email: "",
    password: "",
    line_user_id: "",
  },
});

const bagForm = reactive<SurpriseBagCreate>({
  title: "",
  category: "breakfast",
  description: "",
  description_mode: "hidden",
  price: 79,
  original_value: 120,
  quantity: 5,
  pickup_start_at: "",
  pickup_end_at: "",
  allergens: [],
  dietary_flags: [],
  storage_note: "",
});

const bagTextFields = reactive({
  allergens: "",
  dietary_flags: "",
});

const publicFilters = reactive({
  sort: "new" as "new" | "popular",
  category: "",
});

const isLoggedIn = computed(() => Boolean(currentUser.value));

function parseList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function cleanOptional(value: string): string | null {
  return value.trim() || null;
}

function formatDate(value?: string | null): string {
  if (!value) {
    return "未設定";
  }

  return new Intl.DateTimeFormat("zh-TW", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function remainingQuantity(bag: SurpriseBagRead): number {
  return Math.max(bag.quantity - bag.quantity_sold - bag.quantity_reserved, 0);
}

async function runAction(
  action: () => Promise<void>,
  success?: string,
  loading?: string,
): Promise<void> {
  busy.value = true;
  errorMessage.value = "";
  successMessage.value = loading ?? "";

  try {
    await action();
    if (success) {
      successMessage.value = success;
    }
  } catch (error) {
    successMessage.value = "";
    errorMessage.value = error instanceof Error ? error.message : "操作失敗";
  } finally {
    busy.value = false;
  }
}

async function loadCurrentUser(): Promise<void> {
  if (!getToken()) {
    currentUser.value = null;
    return;
  }

  currentUser.value = await getCurrentMerchantUser();
}

async function loadMerchantBags(): Promise<void> {
  if (!currentUser.value) {
    merchantBags.value = [];
    return;
  }

  merchantBags.value = await listMerchantSurpriseBags();
}

async function loadPublicBags(): Promise<void> {
  publicBags.value = await listPublicSurpriseBags({
    sort: publicFilters.sort,
    category: publicFilters.category || undefined,
  });
}

async function handleEmailLogin(): Promise<void> {
  emailLoginBusy.value = true;
  await runAction(async () => {
    const token = await loginEmail(emailLoginForm.email, emailLoginForm.password);
    setToken(token.access_token);
    await loadCurrentUser();
    await loadMerchantBags();
    activeView.value = "merchant";
  }, "登入成功", "正在送出 Email 登入...");
  emailLoginBusy.value = false;
}

async function handleLineLogin(): Promise<void> {
  lineLoginBusy.value = true;
  await runAction(async () => {
    const token = await loginLine(lineLoginForm.line_user_id);
    setToken(token.access_token);
    await loadCurrentUser();
    await loadMerchantBags();
    activeView.value = "merchant";
  }, "登入成功", "正在送出 LINE 登入...");
  lineLoginBusy.value = false;
}

function handleLogout(): void {
  clearToken();
  currentUser.value = null;
  merchantBags.value = [];
  successMessage.value = "已登出";
}

async function handleRegister(): Promise<void> {
  await runAction(async () => {
    await registerMerchant({
      approval_code: registerForm.approval_code,
      merchant: {
        ...registerForm.merchant,
        phone: cleanOptional(registerForm.merchant.phone),
      },
      owner: {
        name: registerForm.owner.name,
        phone: cleanOptional(registerForm.owner.phone),
        email: cleanOptional(registerForm.owner.email),
        password: cleanOptional(registerForm.owner.password),
        line_user_id: cleanOptional(registerForm.owner.line_user_id),
      },
    });
    activeView.value = "merchant";
  }, "註冊成功，請登入");
}

async function handleCreateBag(): Promise<void> {
  await runAction(async () => {
    await createSurpriseBag({
      ...bagForm,
      description: cleanOptional(bagForm.description ?? ""),
      original_value: bagForm.original_value || null,
      pickup_start_at: cleanOptional(bagForm.pickup_start_at ?? ""),
      pickup_end_at: cleanOptional(bagForm.pickup_end_at ?? ""),
      allergens: parseList(bagTextFields.allergens),
      dietary_flags: parseList(bagTextFields.dietary_flags),
      storage_note: cleanOptional(bagForm.storage_note ?? ""),
    });

    bagForm.title = "";
    bagForm.description = "";
    bagTextFields.allergens = "";
    bagTextFields.dietary_flags = "";
    await loadMerchantBags();
    await loadPublicBags();
  }, "福袋已新增");
}

async function handleSelectPublicBag(bagId: string): Promise<void> {
  await runAction(async () => {
    selectedBag.value = await getPublicSurpriseBag(bagId);
  });
}

async function handleShowMerchantBags(merchantId: string): Promise<void> {
  await runAction(async () => {
    publicBags.value = await listPublicMerchantSurpriseBags(merchantId);
    selectedBag.value = null;
    activeView.value = "public";
  });
}

onMounted(async () => {
  try {
    await loadPublicBags();
    await loadCurrentUser();
    await loadMerchantBags();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "初始資料載入失敗";
  }
});
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Foodtopia</p>
        <h1>商家 MVP 控制台</h1>
      </div>

      <div class="topbar-actions">
        <nav class="tabs" aria-label="主要頁面">
          <button :class="{ active: activeView === 'public' }" @click="activeView = 'public'">
            公開福袋
          </button>
          <button :class="{ active: activeView === 'merchant' }" @click="activeView = 'merchant'">
            商家登入 / 後台
          </button>
          <button :class="{ active: activeView === 'register' }" @click="activeView = 'register'">
            商家註冊
          </button>
        </nav>

        <button v-if="!currentUser" type="button" @click="activeView = 'merchant'">
          商家登入
        </button>
        <button v-else class="ghost" type="button" @click="handleLogout">
          登出
        </button>
      </div>
    </header>

    <section v-if="errorMessage" class="notice error">{{ errorMessage }}</section>
    <section v-if="successMessage" class="notice success">{{ successMessage }}</section>

    <section v-if="activeView === 'merchant'" class="layout two-column">
      <div class="panel">
        <div class="section-heading">
          <h2>商家登入</h2>
          <button v-if="isLoggedIn" class="ghost" type="button" @click="handleLogout">
            登出
          </button>
        </div>

        <div v-if="currentUser" class="account-summary">
          <strong>{{ currentUser.name }}</strong>
          <span>{{ currentUser.email || currentUser.line_user_id || "未提供登入識別" }}</span>
          <span>{{ currentUser.role }} · {{ currentUser.merchant_id }}</span>
        </div>

        <form v-else class="form-grid" @submit.prevent="handleEmailLogin">
          <label>
            Email
            <input v-model="emailLoginForm.email" type="email" autocomplete="email" required />
          </label>
          <label>
            Password
            <input
              v-model="emailLoginForm.password"
              type="password"
              autocomplete="current-password"
              required
            />
          </label>
          <button :disabled="emailLoginBusy" type="submit">
            {{ emailLoginBusy ? "登入中..." : "Email 登入" }}
          </button>
        </form>

        <form v-if="!currentUser" class="form-grid compact" @submit.prevent="handleLineLogin">
          <label>
            LINE user id
            <input v-model="lineLoginForm.line_user_id" type="text" />
          </label>
          <button :disabled="lineLoginBusy" type="submit">
            {{ lineLoginBusy ? "登入中..." : "LINE 登入" }}
          </button>
        </form>
      </div>

      <div class="panel">
        <div class="section-heading">
          <h2>新增福袋</h2>
        </div>

        <form class="form-grid" @submit.prevent="handleCreateBag">
          <label>
            名稱
            <input v-model="bagForm.title" type="text" required />
          </label>
          <label>
            分類
            <input v-model="bagForm.category" type="text" required />
          </label>
          <label>
            售價
            <input v-model.number="bagForm.price" min="1" type="number" required />
          </label>
          <label>
            原價
            <input v-model.number="bagForm.original_value" min="1" type="number" />
          </label>
          <label>
            數量
            <input v-model.number="bagForm.quantity" min="1" type="number" required />
          </label>
          <label>
            揭露程度
            <select v-model="bagForm.description_mode">
              <option value="hidden">hidden</option>
              <option value="partial">partial</option>
              <option value="full">full</option>
            </select>
          </label>
          <label class="span-2">
            描述
            <textarea v-model="bagForm.description" rows="3"></textarea>
          </label>
          <label>
            取貨開始
            <input v-model="bagForm.pickup_start_at" type="datetime-local" />
          </label>
          <label>
            取貨結束
            <input v-model="bagForm.pickup_end_at" type="datetime-local" />
          </label>
          <label>
            過敏原
            <input v-model="bagTextFields.allergens" type="text" placeholder="milk, peanut" />
          </label>
          <label>
            飲食標籤
            <input v-model="bagTextFields.dietary_flags" type="text" placeholder="vegetarian" />
          </label>
          <label class="span-2">
            保存備註
            <input v-model="bagForm.storage_note" type="text" />
          </label>
          <button :disabled="busy || !currentUser" type="submit">新增福袋</button>
        </form>
      </div>

      <div class="panel wide">
        <div class="section-heading">
          <h2>我的福袋</h2>
          <button :disabled="busy || !currentUser" class="ghost" type="button" @click="loadMerchantBags">
            重新整理
          </button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>名稱</th>
                <th>狀態</th>
                <th>價格</th>
                <th>剩餘</th>
                <th>取貨時間</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="bag in merchantBags" :key="bag.id">
                <td>
                  <strong>{{ bag.title }}</strong>
                  <span>{{ bag.category }}</span>
                </td>
                <td>{{ bag.status }}</td>
                <td>{{ bag.price }}</td>
                <td>{{ remainingQuantity(bag) }} / {{ bag.quantity }}</td>
                <td>{{ formatDate(bag.pickup_start_at) }} - {{ formatDate(bag.pickup_end_at) }}</td>
              </tr>
              <tr v-if="merchantBags.length === 0">
                <td colspan="5">尚無資料</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section v-if="activeView === 'register'" class="layout">
      <div class="panel">
        <div class="section-heading">
          <h2>商家註冊</h2>
        </div>

        <form class="form-grid" @submit.prevent="handleRegister">
          <label>
            店名
            <input v-model="registerForm.merchant.name" type="text" required />
          </label>
          <label>
            Google place id
            <input v-model="registerForm.merchant.google_place_id" type="text" required />
          </label>
          <label class="span-2">
            地址
            <input v-model="registerForm.merchant.address" type="text" required />
          </label>
          <label>
            緯度
            <input v-model.number="registerForm.merchant.lat" type="number" step="0.000001" required />
          </label>
          <label>
            經度
            <input v-model.number="registerForm.merchant.lng" type="number" step="0.000001" required />
          </label>
          <label>
            店家電話
            <input v-model="registerForm.merchant.phone" type="text" />
          </label>
          <label>
            業態
            <input v-model="registerForm.merchant.business_type" type="text" required />
          </label>
          <label>
            負責人
            <input v-model="registerForm.owner.name" type="text" required />
          </label>
          <label>
            負責人電話
            <input v-model="registerForm.owner.phone" type="text" />
          </label>
          <label>
            Email
            <input v-model="registerForm.owner.email" type="email" />
          </label>
          <label>
            Password
            <input v-model="registerForm.owner.password" type="password" />
          </label>
          <label>
            LINE user id
            <input v-model="registerForm.owner.line_user_id" type="text" />
          </label>
          <label>
            審核碼
            <input v-model="registerForm.approval_code" type="text" required />
          </label>
          <button :disabled="busy" type="submit">送出註冊</button>
        </form>
      </div>
    </section>

    <section v-if="activeView === 'public'" class="layout">
      <div class="panel">
        <div class="section-heading">
          <h2>公開福袋</h2>
        </div>

        <div class="filters">
          <label>
            排序
            <select v-model="publicFilters.sort" @change="loadPublicBags">
              <option value="new">新品</option>
              <option value="popular">熱門</option>
            </select>
          </label>
          <label>
            分類
            <input v-model="publicFilters.category" type="text" @keyup.enter="loadPublicBags" />
          </label>
          <button :disabled="busy" type="button" @click="loadPublicBags">搜尋</button>
        </div>

        <div class="bag-grid">
          <article v-for="bag in publicBags" :key="bag.id" class="bag-card">
            <div>
              <span class="merchant-name">{{ bag.merchant_name }}</span>
              <h3>{{ bag.title }}</h3>
              <p>{{ bag.description || "內容由商家保密" }}</p>
            </div>
            <dl>
              <div>
                <dt>售價</dt>
                <dd>{{ bag.price }}</dd>
              </div>
              <div>
                <dt>剩餘</dt>
                <dd>{{ bag.available_quantity }}</dd>
              </div>
              <div>
                <dt>取貨</dt>
                <dd>{{ formatDate(bag.pickup_start_at) }}</dd>
              </div>
            </dl>
            <div class="card-actions">
              <button type="button" @click="handleSelectPublicBag(bag.id)">查看</button>
              <button class="ghost" type="button" @click="handleShowMerchantBags(bag.merchant_id)">
                店家
              </button>
            </div>
          </article>
        </div>
      </div>

      <aside v-if="selectedBag" class="panel detail-panel">
        <div class="section-heading">
          <h2>{{ selectedBag.title }}</h2>
          <button class="ghost" type="button" @click="selectedBag = null">關閉</button>
        </div>
        <p class="merchant-name">{{ selectedBag.merchant_name }}</p>
        <p>{{ selectedBag.description || "內容由商家保密" }}</p>
        <div class="detail-list">
          <span>價格：{{ selectedBag.price }}</span>
          <span>原價：{{ selectedBag.original_value || "未設定" }}</span>
          <span>剩餘：{{ selectedBag.available_quantity }}</span>
          <span>取貨：{{ formatDate(selectedBag.pickup_start_at) }} - {{ formatDate(selectedBag.pickup_end_at) }}</span>
          <span>過敏原：{{ selectedBag.allergens.join(", ") || "未標示" }}</span>
          <span>標籤：{{ selectedBag.dietary_flags.join(", ") || "未標示" }}</span>
        </div>
      </aside>
    </section>
  </main>
</template>
