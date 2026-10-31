<script setup lang="ts">
import { onMounted, ref } from 'vue'
import DoctorAvatar from '../../components/DoctorAvatar.vue'
import Icon from '../../components/Icon.vue'
import ModalDialog from '../../components/ModalDialog.vue'
import { api, ApiError } from '../../lib/api'
import { fa } from '../../lib/fa'
import { CATS } from '../../lib/labels'
import type { Category, Doctor } from '../../lib/types'

const list = ref<Doctor[]>([])
const delId = ref<number | null>(null)
interface Form { id: number | null; name: string; role: string; category: Category; does_injection: boolean; is_active: boolean; photo_url: string | null; file: File | null; previewUrl: string | null; removePhoto: boolean }
const form = ref<Form | null>(null)
const err = ref(''); const busy = ref(false)

const load = async () => { list.value = await api.doctors() }
onMounted(load)

function openForm(d?: Doctor) {
  err.value = ''
  form.value = d
    ? { id: d.id, name: d.name, role: d.role, category: d.category, does_injection: d.does_injection, is_active: d.is_active, photo_url: d.photo_url, file: null, previewUrl: null, removePhoto: false }
    : { id: null, name: '', role: '', category: 'eye', does_injection: true, is_active: true, photo_url: null, file: null, previewUrl: null, removePhoto: false }
}
function pick(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !form.value) return
  if (form.value.previewUrl) URL.revokeObjectURL(form.value.previewUrl)
  form.value.file = file; form.value.previewUrl = URL.createObjectURL(file); form.value.removePhoto = false
}
function clearPhoto() { if (!form.value) return; form.value.file = null; form.value.previewUrl = null; form.value.removePhoto = true }
function setCat(c: Category) { if (!form.value) return; form.value.category = c; form.value.does_injection = c === 'eye' }

async function save() {
  const f = form.value
  if (!f) return
  if (f.name.trim().length < 3) { err.value = 'نام پزشک را وارد کنید.'; return }
  busy.value = true; err.value = ''
  try {
    const body = { name: f.name.trim(), role: f.role.trim(), category: f.category, does_injection: f.category === 'eye' && f.does_injection, is_active: f.is_active }
    const d = f.id ? await api.updateDoctor(f.id, body) : await api.createDoctor(body)
    if (f.file) await api.uploadPhoto(d.id, f.file)
    else if (f.removePhoto && f.photo_url) await api.deletePhoto(d.id)
    form.value = null; await load()
  } catch (e) { err.value = e instanceof ApiError ? e.message : 'ذخیره انجام نشد' } finally { busy.value = false }
}
async function toggle(d: Doctor) { await api.updateDoctor(d.id, { is_active: !d.is_active }); await load() }
async function remove(d: Doctor) { await api.deleteDoctor(d.id); delId.value = null; await load() }
</script>
<template>
  <div class="adm-bar"><p>فقط پزشکان فعال در کیوسک نمایش داده می‌شوند.</p><button type="button" class="btn pri sm" @click="openForm()"><Icon name="plus" />افزودن پزشک</button></div>
  <div class="dcards">
    <div v-for="d in list" :key="d.id" class="dc" :class="{ off: !d.is_active }">
      <div class="dc-top"><DoctorAvatar :name="d.name" :photo="d.photo_url" cls="lg" /><div style="min-width: 0"><b>{{ d.name }}</b><small>{{ d.role || '—' }}</small></div></div>
      <div class="tags">
        <span class="chip">{{ CATS[d.category].name }}</span>
        <span v-if="d.category === 'eye'" class="chip" :class="{ warn: !d.does_injection }">{{ d.does_injection ? 'تزریق چشمی دارد' : 'بدون تزریق' }}</span>
        <span class="chip" :class="d.is_active ? 'good' : 'off'">{{ d.is_active ? 'فعال' : 'غیرفعال' }}</span>
      </div>
      <small class="sub">امروز {{ fa(d.today_count) }} · کل {{ fa(d.total_count) }} نوبت</small>
      <div class="dc-act">
        <button type="button" class="mini" @click="openForm(d)"><Icon name="edit" />ویرایش</button>
        <button type="button" class="mini" @click="toggle(d)">{{ d.is_active ? 'غیرفعال کردن' : 'فعال کردن' }}</button>
        <template v-if="delId === d.id"><button type="button" class="mini bad" @click="remove(d)">تأیید حذف</button><button type="button" class="mini" @click="delId = null">انصراف</button></template>
        <button v-else type="button" class="mini bad" aria-label="حذف" @click="delId = d.id"><Icon name="trash" /></button>
      </div>
    </div>
    <div v-if="!list.length" class="empty">هنوز پزشکی تعریف نشده است.</div>
  </div>

  <ModalDialog v-if="form">
    <div class="form">
      <h2>{{ form.id ? 'ویرایش پزشک' : 'افزودن پزشک' }}</h2>
      <div class="ph-row">
        <img v-if="form.previewUrl" class="avatar xl ph" :src="form.previewUrl" alt="" />
        <DoctorAvatar v-else :name="form.name || '؟'" :photo="form.removePhoto ? null : form.photo_url" cls="xl" />
        <div class="ph-btns">
          <div class="dc-act">
            <label class="mini" for="photoIn"><Icon name="img" />{{ form.photo_url || form.previewUrl ? 'تغییر عکس' : 'انتخاب عکس' }}</label>
            <button v-if="(form.photo_url && !form.removePhoto) || form.previewUrl" type="button" class="mini bad" @click="clearPhoto">حذف عکس</button>
          </div>
          <input id="photoIn" type="file" accept="image/*" class="vh" @change="pick" />
          <small>عکس واضح و نزدیک از صورت پزشک پیشنهاد می‌شود. تصویر به‌صورت مربع برش می‌خورد.</small>
        </div>
      </div>
      <label class="fl"><span>نام و عنوان</span><input v-model="form.name" class="inp" placeholder="مثلاً دکتر ..." autocomplete="off" /></label>
      <label class="fl"><span>تخصص یا توضیح کوتاه</span><input v-model="form.role" class="inp" placeholder="مثلاً جراح آب مروارید" autocomplete="off" /></label>
      <div class="fl"><span>نوع جراحی</span><div class="segs"><button v-for="(c, k) in CATS" :key="k" type="button" class="seg" :class="{ on: form.category === k }" @click="setCat(k as Category)">{{ c.name }}</button></div></div>
      <div v-if="form.category === 'eye'" class="sw-row"><div><b>تزریق چشمی انجام می‌دهد</b><small>اگر خاموش شود، این پزشک هنگام انتخاب «تزریق چشمی» در کیوسک نمایش داده نمی‌شود.</small></div>
        <button type="button" class="sw" :class="{ on: form.does_injection }" role="switch" :aria-checked="form.does_injection" aria-label="تزریق" @click="form.does_injection = !form.does_injection"><i /></button></div>
      <div class="sw-row"><div><b>فعال</b><small>پزشک غیرفعال در کیوسک نمایش داده نمی‌شود.</small></div>
        <button type="button" class="sw" :class="{ on: form.is_active }" role="switch" :aria-checked="form.is_active" aria-label="فعال" @click="form.is_active = !form.is_active"><i /></button></div>
      <div class="msg bad">{{ err }}</div>
      <div class="row"><button type="button" class="btn sec" @click="form = null">انصراف</button><button type="button" class="btn pri" style="max-width: none" :disabled="busy" @click="save">ذخیره</button></div>
    </div>
  </ModalDialog>
</template>
