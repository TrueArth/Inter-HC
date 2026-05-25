<template>
  <div class="grid grid-cols-12 gap-6">
    <div class="col-span-12">
      <Card>
        <template #header>
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Leitos do Setor</h2>
            <div class="flex space-x-2">
               <input v-model="setorInput" type="number" class="border rounded p-1" placeholder="Cód. Setor"/>
               <Button @click="carregar" variant="primary" :loading="leitoStore.loading">Buscar</Button>
            </div>
          </div>
        </template>
        
        <table class="min-w-full divide-y divide-gray-200 mt-4">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quarto</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Situação</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="leito in leitoStore.leitos" :key="leito.lto_id">
              <td class="px-6 py-4">{{ leito.lto_id }}</td>
              <td class="px-6 py-4">{{ leito.qrt_numero }}</td>
              <td class="px-6 py-4">{{ leito.ind_situacao }}</td>
            </tr>
          </tbody>
        </table>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useLeitoStore } from '../stores/leito';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';

const leitoStore = useLeitoStore();
const setorInput = ref(1);

const carregar = async () => {
  await leitoStore.buscarLeitosDoSetor(setorInput.value);
};
</script>