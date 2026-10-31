<script setup lang="ts">
import Icon from './Icon.vue'
defineProps<{ goLabel: string }>()
defineEmits<{ key: [k: string] }>()
// چیدمان استاندارد فارسی؛ «ض» سمت چپ ردیف اول (مثل کیبورد واقعی)
const ROWS = [
  ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'چ'],
  ['ش', 'س', 'ی', 'ب', 'ل', 'ا', 'ت', 'ن', 'م', 'ک', 'گ'],
  ['ظ', 'ط', 'ز', 'ر', 'ذ', 'د', 'پ', 'و', 'ئ', 'ژ'],
]
</script>
<template>
  <div class="kb" role="group" aria-label="کیبورد فارسی">
    <template v-for="(row, ri) in ROWS" :key="ri">
      <span v-if="ri === 1" class="key sp1" />
      <button v-for="c in row" :key="c" type="button" class="key" @click="$emit('key', 'ch:' + c)">{{ c }}</button>
      <span v-if="ri === 1" class="key sp1" />
    </template>
    <button type="button" class="key fn w4" aria-label="حذف" @click="$emit('key', 'bk')"><Icon name="bk" /></button>
    <button type="button" class="key fn w3" @click="$emit('key', 'ch:آ')">آ</button>
    <button type="button" class="key fn w4" @click="$emit('key', 'zwnj')">نیم‌فاصله</button>
    <button type="button" class="key w11" aria-label="فاصله" @click="$emit('key', 'space')" />
    <button type="button" class="key fn go w6" @click="$emit('key', 'go')">{{ goLabel }}</button>
  </div>
</template>
