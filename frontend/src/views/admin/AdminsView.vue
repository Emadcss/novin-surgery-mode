<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Icon from '../../components/Icon.vue'
import ModalDialog from '../../components/ModalDialog.vue'
import { api, ApiError } from '../../lib/api'
import { normDigits } from '../../lib/fa'
import type { AdminUser } from '../../lib/types'
import { useAuth } from '../../stores/auth'

const auth = useAuth()
const list = ref<AdminUser[]>([])
const form = ref<{ id: number | null; name: string; pin: string } | null>(null)
const err = ref(''); const delId = ref<number | null>(null)
const load = async () => { list.value = await api.admins() }
onMounted(load)

async function save() {
  const f = form.value
  if (!f) return
  const pin = normDigits(f.pin)
  if (f.name.trim().length < 2) { err.value = 'نام را وارد کنید.'; return }
  if (!f.id && pin.length !== 4) { err.value = 'رمز باید چهار رقم باشد.'; return }
  if (f.id && pin && pin.length !== 4) { err.value = 'رمز باید چهار رقم باشد.'; return }
  try {
    if (f.id) await api.updateAdmin(f.id, { name: f.name.trim(), ...(pin ? { pin } : {}) })
    else await api.createAdmin({ name: f.name.trim(), pin })
    form.value = null; await load()
  } catch (e) { err.value = e instanceof ApiError ? e.message : 'ذخیره انجام نشد' }
}
async function remove(a: AdminUser) { try { await api.deleteAdmin(a.id); delId.value = null; await load() } catch (e) { err.value = e instanceof ApiError ? e.message : '' } }
</script>
<template>
  <div class="adm-bar"><p>هر ادمین با رمز چهار رقمی خودش وارد می‌شود.</p><button type="button" class="btn pri sm" @click="form = { id: null, name: '', pin: '' }; err = ''"><Icon name="plus" />افزودن ادمین</button></div>
  <div class="box"><div class="rows">
    <div v-for="a in list" :key="a.id" class="row-i adm-r">
      <span class="avatar">{{ a.name[0] ?? '؟' }}</span>
      <div style="min-width: 0"><div class="nm">{{ a.name }} <span v-if="a.id === auth.admin?.id" class="chip">شما</span></div><div class="sub">رمز: ••••</div></div>
      <div class="dc-act">
        <button type="button" class="mini" @click="form = { id: a.id, name: a.name, pin: '' }; err = ''"><Icon name="edit" />ویرایش</button>
        <template v-if="a.id !== auth.admin?.id && list.length > 1">
          <template v-if="delId === a.id"><button type="button" class="mini bad" @click="remove(a)">تأیید حذف</button><button type="button" class="mini" @click="delId = null">انصراف</button></template>
          <button v-else type="button" class="mini bad" aria-label="حذف" @click="delId = a.id"><Icon name="trash" /></button>
        </template>
      </div>
    </div>
  </div></div>
  <ModalDialog v-if="form">
    <div class="form">
      <h2>{{ form.id ? 'ویرایش ادمین' : 'افزودن ادمین' }}</h2>
      <label class="fl"><span>نام</span><input v-model="form.name" class="inp" autocomplete="off" /></label>
      <label class="fl"><span>رمز چهار رقمی{{ form.id ? ' (برای حفظ رمز فعلی خالی بگذارید)' : '' }}</span><input v-model="form.pin" class="inp" inputmode="numeric" maxlength="4" dir="ltr" autocomplete="off" /></label>
      <div class="msg bad">{{ err }}</div>
      <div class="row"><button type="button" class="btn sec" @click="form = null">انصراف</button><button type="button" class="btn pri" style="max-width: none" @click="save">ذخیره</button></div>
    </div>
  </ModalDialog>
</template>
