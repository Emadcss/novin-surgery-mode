<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ApiError, api } from '../../lib/api'
import { TEXT_DEFAULTS, TEXT_DEFS, TEXT_GROUPS, TEXT_MAX } from '../../lib/texts'
import type { Theme } from '../../lib/types'
import { useTexts } from '../../stores/texts'
import { useTheme } from '../../stores/theme'

const t = useTheme()
const tx = useTexts()
const err = ref('')
const opts: [Theme, string][] = [['light', 'روشن'], ['dark', 'تیره'], ['auto', 'خودکار (طبق تنظیم دستگاه)']]
async function pick(v: Theme) {
  err.value = ''
  try { await t.set(v) } catch (e) { err.value = e instanceof ApiError ? e.message : 'ذخیره انجام نشد' }
}

// ----- متن‌های کیوسک -----
const effective = (key: string) => tx.over[key] ?? TEXT_DEFAULTS[key] ?? ''
const draft = reactive<Record<string, string>>(Object.fromEntries(TEXT_DEFS.map((d) => [d.key, effective(d.key)])))
const changed = computed(() => TEXT_DEFS.filter((d) => draft[d.key]!.trim() !== effective(d.key)))
const customized = (key: string) => draft[key]!.trim() !== TEXT_DEFAULTS[key]
const saving = ref(false)
const tErr = ref('')
const saved = ref(false)
const cat = ref<string>(TEXT_GROUPS[0])

async function saveTexts() {
  tErr.value = ''; saved.value = false; saving.value = true
  try {
    const body: Record<string, string | null> = {}
    for (const d of changed.value) {
      const v = draft[d.key]!.trim()
      body[d.key] = v === d.def ? null : v
    }
    const res = await api.setTexts(body)
    tx.set(res.texts)
    for (const d of TEXT_DEFS) draft[d.key] = effective(d.key)
    saved.value = true
  } catch (e) {
    tErr.value = e instanceof ApiError ? e.message : 'ذخیره انجام نشد'
  } finally { saving.value = false }
}
function reset(key: string) { draft[key] = TEXT_DEFAULTS[key] ?? '' }
</script>
<template>
  <div class="box">
    <h2>ظاهر کیوسک</h2>
    <div class="segs"><button v-for="[v, l] in opts" :key="v" type="button" class="seg" :class="{ on: t.theme === v }" @click="pick(v)">{{ l }}</button></div>
    <p class="theme-note">در محیط کلینیک که نور محیط زیاد است، حالت «روشن» توصیه می‌شود و به‌صورت پیش‌فرض فعال است. حالت تیره فقط در صورت انتخاب شما فعال می‌شود و برای همه‌ی کیوسک‌ها اعمال می‌گردد.</p>
    <div class="msg bad">{{ err }}</div>
  </div>

  <div class="box texts">
    <h2>متن‌های کیوسک</h2>
    <p class="theme-note">عنوان‌ها، راهنماها و پیام‌هایی که بیمار روی کیوسک می‌بیند را اینجا ویرایش کنید. اگر متنی را پاک کنید یا «بازنشانی» بزنید، متن پیش‌فرض برمی‌گردد. در پیام‌های دارای <code dir="ltr">{name}</code>، نام و نام‌خانوادگی بیمار جایگزین می‌شود. تغییرها با باز شدن مجدد کیوسک اعمال می‌شود.</p>
    <div class="segs"><button v-for="g in TEXT_GROUPS" :key="g" type="button" class="seg" :class="{ on: cat === g }" @click="cat = g">{{ g }}</button></div>
    <div class="t-list">
      <label v-for="d in TEXT_DEFS.filter((x) => x.group === cat)" :key="d.key" class="t-item">
        <span class="t-lbl">{{ d.label }}<button v-if="customized(d.key)" type="button" class="mini" @click.prevent="reset(d.key)">بازنشانی</button></span>
        <textarea v-if="d.long" v-model="draft[d.key]" class="inp" rows="2" :maxlength="TEXT_MAX" :placeholder="d.def" />
        <input v-else v-model="draft[d.key]" class="inp" type="text" :maxlength="TEXT_MAX" :placeholder="d.def || 'بدون متن'" />
        <small v-if="d.vars" class="sub">متغیر قابل استفاده: <code dir="ltr">{{ d.vars.map((v) => '{' + v + '}').join(' ') }}</code></small>
      </label>
    </div>
    <div class="t-bar">
      <button type="button" class="btn pri sm" :disabled="!changed.length || saving" @click="saveTexts">{{ saving ? 'در حال ذخیره…' : `ذخیره‌ی تغییرها${changed.length ? ' (' + changed.length + ')' : ''}` }}</button>
      <span v-if="saved && !changed.length" class="msg good">ذخیره شد.</span>
    </div>
    <div class="msg bad">{{ tErr }}</div>
  </div>
</template>
