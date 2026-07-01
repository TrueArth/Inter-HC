<template>
  <div class="space-y-6" v-if="authStore.isAdmin">
    <!-- Header Area -->
    <div class="flex justify-between items-center bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <UserGroupIcon v-if="abaAtiva === 'usuarios'" class="h-8 w-8 text-blue-600" />
          <QueueListIcon v-else-if="abaAtiva === 'especialidades'" class="h-8 w-8 text-blue-600" />
          <ClipboardDocumentListIcon v-else-if="abaAtiva === 'sintomas'" class="h-8 w-8 text-blue-600" />
          <UserIcon v-else-if="abaAtiva === 'pacientes'" class="h-8 w-8 text-blue-600" />
          <ChartBarIcon v-else class="h-8 w-8 text-blue-600" />
          {{ 
            abaAtiva === 'usuarios' ? 'Gestão de Usuários' : 
            abaAtiva === 'especialidades' ? 'Gerenciar Especialidades' :
            abaAtiva === 'sintomas' ? 'Gerenciar Sintomas & Regras' :
            abaAtiva === 'pacientes' ? 'Pacientes (AGHU)' :
            'Estatísticas de Regulação' 
          }}
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          {{ 
            abaAtiva === 'usuarios' ? 'Crie novos usuários e gerencie perfis de acesso localmente.' : 
            abaAtiva === 'especialidades' ? 'Cadastre e remova especialidades médicas no catálogo.' :
            abaAtiva === 'sintomas' ? 'Crie sintomas e defina regras de gravidade específicas por especialidade.' :
            abaAtiva === 'pacientes' ? 'Visualize a lista de pacientes cadastrados na base do AGHU.' :
            'Acompanhe indicadores clínicos e auditoria de solicitações.' 
          }}
        </p>
      </div>
      <div>
        <Button v-if="abaAtiva === 'usuarios'" variant="primary" @click="abrirModalCriar">
          <template #icon>
            <UserPlusIcon class="h-5 w-5" />
          </template>
          Novo Usuário
        </Button>
        <Button v-if="abaAtiva === 'especialidades'" variant="primary" @click="abrirModalCriarEsp">
          Nova Especialidade
        </Button>
        <Button v-if="abaAtiva === 'sintomas'" variant="primary" @click="abrirModalCriarSint">
          Novo Sintoma
        </Button>
        <Button v-if="abaAtiva === 'estatisticas'" variant="default" @click="carregarEstatisticas" :loading="loadingStats">
          Atualizar Dados
        </Button>
      </div>
    </div>

    <!-- Tab Selector -->
    <div class="flex gap-6 border-b border-gray-200 font-sans">
      <button 
        @click="alterarAba('usuarios')" 
        :class="abaAtiva === 'usuarios' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Gerenciar Usuários
      </button>
      <button 
        @click="alterarAba('especialidades')" 
        :class="abaAtiva === 'especialidades' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Gerenciar Especialidades
      </button>
      <button 
        @click="alterarAba('sintomas')" 
        :class="abaAtiva === 'sintomas' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Gerenciar Sintomas & Regras
      </button>
      <button 
        @click="alterarAba('pacientes')" 
        :class="abaAtiva === 'pacientes' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Pacientes (AGHU)
      </button>
      <button 
        @click="alterarAba('estatisticas')" 
        :class="abaAtiva === 'estatisticas' ? 'border-b-2 border-blue-600 text-blue-600 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="pb-3 px-2 transition text-sm font-semibold focus:outline-none"
      >
        Estatísticas de Regulação
      </button>
    </div>

    <!-- Tab 1: Gerenciar Usuários -->
    <div v-show="abaAtiva === 'usuarios'" class="space-y-6">
      <!-- Users Table Card -->
      <Card>
        <template #header>
          <div class="pb-2">
            <h2 class="text-lg font-semibold text-gray-700">Usuários Ativos no Sistema</h2>
            <p class="text-xs text-gray-400">Lista de credenciais locais cadastradas e seus cargos associados.</p>
          </div>
        </template>

        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <p class="text-sm text-gray-500 mt-2">Carregando usuários...</p>
        </div>

        <div v-else-if="users.length === 0" class="text-center py-12">
          <UserGroupIcon class="h-12 w-12 text-gray-300 mx-auto" />
          <p class="text-sm text-gray-500 mt-2">Nenhum usuário local cadastrado.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 mt-2">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Username</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nome Completo</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">E-mail</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Perfil / Cargo</th>
                <th class="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50/50 transition">
                <td class="px-6 py-4 text-sm font-semibold text-gray-900 font-mono">@{{ u.username }}</td>
                <td class="px-6 py-4 text-sm text-gray-600">{{ u.display_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ u.email || 'N/A' }}</td>
                <td class="px-6 py-4 text-sm">
                  <span :class="roleClass(u.role)" class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider">
                    {{ roleLabel(u.role) }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-center flex justify-center gap-2">
                  <button 
                    @click="abrirModalEditar(u)" 
                    class="p-2 rounded text-blue-600 hover:bg-blue-50 transition" 
                    title="Editar Usuário"
                  >
                    <PencilSquareIcon class="h-5 w-5" />
                  </button>
                  <button 
                    v-if="u.username !== 'admin'"
                    @click="confirmarInativar(u)" 
                    class="p-2 rounded text-red-600 hover:bg-red-50 transition" 
                    title="Desativar Usuário"
                  >
                    <TrashIcon class="h-5 w-5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- Tab 3: Gerenciar Especialidades -->
    <div v-show="abaAtiva === 'especialidades'" class="space-y-6">
      <Card>
        <template #header>
          <div class="pb-2">
            <h2 class="text-lg font-semibold text-gray-700">Especialidades Cadastradas</h2>
            <p class="text-xs text-gray-400">Lista de especialidades médicas disponíveis no catálogo de interconsultas.</p>
          </div>
        </template>
        
        <div v-if="loadingCatalog" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <p class="text-sm text-gray-500 mt-2">Carregando especialidades...</p>
        </div>
        
        <div v-else-if="especialidades.length === 0" class="text-center py-12">
          <p class="text-sm text-gray-500">Nenhuma especialidade cadastrada.</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 mt-2">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nome da Especialidade</th>
                <th class="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr v-for="esp in especialidades" :key="esp.id" class="hover:bg-gray-50/50 transition">
                <td class="px-6 py-4 text-sm font-semibold text-gray-900 font-mono">#{{ esp.id }}</td>
                <td class="px-6 py-4 text-sm text-gray-600">{{ esp.nome }}</td>
                <td class="px-6 py-4 text-sm text-center flex justify-center gap-2">
                  <button 
                    @click="confirmarInativarEsp(esp)" 
                    class="p-2 rounded text-red-600 hover:bg-red-50 transition" 
                    title="Remover Especialidade"
                  >
                    <TrashIcon class="h-5 w-5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- Tab 4: Gerenciar Sintomas & Regras -->
    <div v-show="abaAtiva === 'sintomas'" class="space-y-6">
      
      <!-- Filtro de Especialidades no Topo (Estilo Central de Marcação) -->
      <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h4 class="text-sm font-bold text-gray-800">Filtrar Catálogo por Especialidade</h4>
            <p class="text-xs text-gray-400">Selecione uma especialidade para gerenciar seus sintomas e pontuações específicas</p>
          </div>
          <!-- Campo de busca rápida -->
          <div class="relative w-full sm:w-64">
            <input 
              type="text" 
              v-model="buscaSintoma" 
              placeholder="Buscar sintoma no catálogo..." 
              class="form-control text-xs py-1.5 px-3 bg-white w-full border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div class="flex flex-wrap gap-2 pt-1">
          <button
            v-for="esp in especialidades"
            :key="esp.id"
            type="button"
            class="px-4 py-2 text-xs font-bold rounded-lg transition duration-200 focus:outline-none flex items-center gap-2 border"
            :class="[
              especialidadeFiltro === esp.id 
                ? 'bg-blue-600 border-blue-600 text-white shadow-sm font-bold' 
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100 hover:text-gray-800 font-medium'
            ]"
            @click="especialidadeFiltro = (especialidadeFiltro === esp.id ? 'todas' : esp.id)"
          >
            {{ esp.nome }}
            <span 
              class="px-2 py-0.5 text-[10px] rounded-full font-extrabold transition-colors duration-200"
              :class="[
                especialidadeFiltro === esp.id 
                  ? 'bg-blue-700 text-white' 
                  : 'bg-gray-200 text-gray-700'
              ]"
            >
              {{ contarSintomasDaEspecialidade(esp.id) }}
            </span>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Lista de Sintomas -->
        <Card class="lg:col-span-2">
          <template #header>
            <div class="pb-2">
              <h2 class="text-lg font-semibold text-gray-700">Sintomas do Catálogo</h2>
              <p class="text-xs text-gray-400">
                Exibindo {{ sintomasFiltrados.length }} sintoma(s)
                <span v-if="especialidadeFiltro !== 'todas'">
                  de <strong class="text-blue-600">{{ obterNomeEspecialidade(especialidadeFiltro) }}</strong>
                </span>
              </p>
            </div>
          </template>
          
          <div v-if="loadingCatalog" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p class="text-sm text-gray-500 mt-2">Carregando sintomas...</p>
          </div>
          
          <div v-else-if="sintomasFiltrados.length === 0" class="text-center py-12">
            <p class="text-sm text-gray-500">Nenhum sintoma cadastrado ou encontrado nesta seleção.</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 mt-2">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Sintoma</th>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Pontuação</th>
                  <th class="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-for="sint in sintomasFiltrados" :key="sint.id" class="hover:bg-gray-50/50 transition">
                  <td class="px-6 py-4 text-sm font-semibold text-gray-900 font-mono">#{{ sint.id }}</td>
                  <td class="px-6 py-4 text-sm text-gray-600 font-medium">
                    <div>{{ sint.nome }}</div>
                    <div class="flex flex-wrap gap-1 mt-1">
                      <span 
                        v-for="esp in obterEspecialidadesSintoma(sint.id)" 
                        :key="esp.id" 
                        class="inline-flex items-center px-1.5 py-0.2 bg-gray-100 text-gray-600 text-[10px] rounded font-medium"
                      >
                        {{ esp.nome }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <span :class="scoreClass(obterPontuacaoExibicao(sint))" class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold uppercase">
                      {{ obterPontuacaoExibicao(sint) }} pts
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-center flex justify-center gap-2">
                    <button 
                      @click="confirmarInativarSint(sint)" 
                      class="p-2 rounded text-red-600 hover:bg-red-50 transition" 
                      title="Remover Sintoma"
                    >
                      <TrashIcon class="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>

        <!-- Regras de Override de Risco / Pontuação -->
        <div class="space-y-6">
          <!-- Nova Regra Card -->
          <Card>
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Definir Pontuação Específica</h3>
              <p class="text-xs text-gray-400 mt-0.5">Customize a pontuação de um sintoma para uma especialidade específica.</p>
            </template>
            
            <form @submit.prevent="salvarRegra" class="space-y-4 mt-2">
              <div class="form-group">
                <label class="form-label text-xs">Sintoma</label>
                <select v-model.number="novaRegra.sintoma_id" class="form-control text-sm" required>
                  <option v-for="s in sintomas" :key="s.id" :value="s.id">{{ s.nome }}</option>
                </select>
              </div>
              
              <div class="form-group">
                <label class="form-label text-xs">Especialidade Destino</label>
                <select v-model.number="novaRegra.especialidade_id" class="form-control text-sm" required>
                  <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nome }}</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label text-xs">Pontuação Específica</label>
                <input type="number" v-model.number="novaRegra.pontuacao" min="1" class="form-control text-sm" required />
              </div>

              <Button type="submit" variant="primary" class="w-full text-xs py-2" :loading="salvandoRegra">
                Salvar Regra
              </Button>
            </form>
          </Card>

          <!-- Regras Existentes -->
          <Card>
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Regras Customizadas</h3>
              <p class="text-xs text-gray-400 mt-0.5">Regras que sobrescrevem a pontuação padrão.</p>
            </template>
            
            <div v-if="regras.length === 0" class="text-center py-6 text-xs text-gray-400">
              Nenhuma regra customizada ativa.
            </div>
            
            <div v-else class="space-y-3 mt-2 max-h-80 overflow-y-auto pr-1">
              <div 
                v-for="reg in regras" 
                :key="reg.sintoma_id + '-' + reg.especialidade_id" 
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100 text-xs"
              >
                <div class="space-y-1 pr-2">
                  <p class="font-semibold text-gray-700">
                    {{ obterNomeSintoma(reg.sintoma_id) }}
                  </p>
                  <p class="text-gray-400 flex items-center gap-1">
                    ➔ para <span class="font-medium text-gray-600">{{ obterNomeEspecialidade(reg.especialidade_id) }}</span>
                  </p>
                  <span :class="scoreClass(reg.pontuacao)" class="inline-flex px-1.5 py-0.5 rounded text-[10px] font-bold uppercase mt-1">
                    {{ reg.pontuacao }} pts
                  </span>
                </div>
                <button 
                  @click="confirmarInativarRegra(reg)" 
                  class="p-1 text-red-500 hover:bg-red-50 rounded transition"
                  title="Remover Regra"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>

    <!-- Modal Criar Especialidade -->
    <Modal :show="mostrarModalCriarEsp" @close="mostrarModalCriarEsp = false">
      <template #header>Cadastrar Nova Especialidade</template>
      
      <form @submit.prevent="salvarNovaEspecialidade" class="space-y-4">
        <div class="form-group">
          <label class="form-label">Nome da Especialidade</label>
          <input 
            type="text" 
            v-model="novaEsp.nome" 
            class="form-control" 
            required 
            placeholder="Ex: Pneumologia"
          />
        </div>
        <p v-if="erroFormCatalog" class="text-xs text-red-500 font-semibold">{{ erroFormCatalog }}</p>
      </form>

      <template #footer>
        <Button variant="default" @click="mostrarModalCriarEsp = false">Cancelar</Button>
        <Button variant="primary" :loading="salvandoCatalog" @click="salvarNovaEspecialidade">Salvar</Button>
      </template>
    </Modal>

    <!-- Modal Criar Sintoma -->
    <Modal :show="mostrarModalCriarSint" @close="mostrarModalCriarSint = false">
      <template #header>Cadastrar Novo Sintoma</template>
      
      <form @submit.prevent="salvarNovoSintoma" class="space-y-4">
        <div class="form-group">
          <label class="form-label">Nome do Sintoma</label>
          <input 
            type="text" 
            v-model="novoSint.nome" 
            class="form-control" 
            required 
            placeholder="Ex: Tosse seca persistente"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">Pontuação Padrão</label>
          <input 
            type="number" 
            v-model.number="novoSint.pontuacao" 
            min="1" 
            class="form-control" 
            required 
            placeholder="Ex: 5"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Especialidade Vinculada</label>
          <select 
            v-model.number="novoSint.especialidade_id" 
            class="form-control bg-white cursor-pointer" 
            required
          >
            <option v-for="esp in especialidades" :key="esp.id" :value="esp.id">
              {{ esp.nome }}
            </option>
          </select>
        </div>
        <p v-if="erroFormCatalog" class="text-xs text-red-500 font-semibold">{{ erroFormCatalog }}</p>
      </form>

      <template #footer>
        <Button variant="default" @click="mostrarModalCriarSint = false">Cancelar</Button>
        <Button variant="primary" :loading="salvandoCatalog" @click="salvarNovoSintoma">Salvar</Button>
      </template>
    </Modal>

    <!-- Tab 5: Pacientes (AGHU) -->
    <div v-show="abaAtiva === 'pacientes'" class="space-y-6">
      <Card>
        <template #header>
          <div class="pb-2">
            <h2 class="text-lg font-semibold text-gray-700">Pacientes Cadastrados no AGHU</h2>
            <p class="text-xs text-gray-400">Lista completa de pacientes obtida via simulação de conexão com o banco hospitalar.</p>
          </div>
        </template>

        <div v-if="loadingPacientes" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <p class="text-sm text-gray-500 mt-2">Carregando pacientes do AGHU...</p>
        </div>

        <div v-else-if="pacientes.length === 0" class="text-center py-12">
          <p class="text-sm text-gray-500">Nenhum paciente cadastrado no AGHU.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 mt-2">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cód. AGHU</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Prontuário (PREP)</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nome Completo</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">CPF</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Dt. Nasc.</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Gênero / Cor</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Filiação</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100 font-sans">
              <tr v-for="p in pacientes" :key="p.codigo" class="hover:bg-gray-50/50 transition">
                <td class="px-6 py-4 text-sm font-semibold text-gray-950 font-mono font-bold">#{{ p.codigo }}</td>
                <td class="px-6 py-4 text-sm font-semibold text-blue-600 font-mono">{{ p.prep }}</td>
                <td class="px-6 py-4 text-sm font-bold text-gray-950">{{ p.nome }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 font-mono">{{ p.cpf || 'Não informado' }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ p.dt_nascimento }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">
                  <span class="inline-flex px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 text-gray-700">
                    {{ p.sexo }} / {{ p.cor }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-400">
                  <div class="text-xs">Mãe: {{ p.nome_mae || 'Não informado' }}</div>
                  <div class="text-xs">Pai: {{ p.nome_pai || 'Não informado' }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- Tab 2: Estatísticas de Regulação -->
    <div v-show="abaAtiva === 'estatisticas'" class="space-y-6">
      <div v-if="loadingStats" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <p class="text-sm text-gray-500 mt-2">Processando dados e estatísticas...</p>
      </div>

      <div v-else-if="!stats" class="text-center py-12 bg-white rounded-xl border border-gray-200">
        <p class="text-sm text-gray-500">Erro ao carregar estatísticas do banco de dados.</p>
      </div>

      <div v-else class="space-y-6">
        <!-- Top bar with Title and Export Button -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div>
            <h2 class="text-lg font-bold text-gray-800">Painel Analytics</h2>
            <p class="text-xs text-gray-400 mt-0.5">Indicadores de desempenho e fila de regulação do InterHC.</p>
          </div>
          <Button variant="primary" :loading="exportandoExcel" @click="exportarExcel" class="flex items-center gap-2">
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Exportar para Excel
          </Button>
        </div>

        <!-- Highlights Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Total de Interconsultas</p>
              <h3 class="text-2xl font-bold text-gray-800 mt-1">{{ stats.total_interconsultas }}</h3>
              <p class="text-xs text-gray-400 mt-1">Solicitações ativas</p>
            </div>
            <div class="bg-blue-50/50 text-blue-600 p-3 rounded-lg">
              <InboxIcon class="h-6 w-6" />
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Tempo Médio de Marcação</p>
              <h3 class="text-2xl font-bold text-gray-800 mt-1">{{ stats.tempo_medio_atendimento_formatado }}</h3>
              <p class="text-xs text-gray-400 mt-1">Média para agendamento</p>
            </div>
            <div class="bg-indigo-50 text-indigo-600 p-3 rounded-lg">
              <ClockIcon class="h-6 w-6" />
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Especialidade Mais Solicitada</p>
              <h3 class="text-2xl font-bold text-gray-800 mt-1 truncate max-w-[160px]">{{ stats.top_specialty.name }}</h3>
              <p class="text-xs text-blue-600 font-semibold mt-1">{{ stats.top_specialty.count }} solicitações</p>
            </div>
            <div class="bg-blue-50 text-blue-600 p-3 rounded-lg">
              <ChartBarIcon class="h-6 w-6" />
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Total de Casos Indevidos</p>
              <h3 class="text-2xl font-bold text-red-600 mt-1">{{ totalIndevidas }}</h3>
              <p class="text-xs text-red-400 font-semibold mt-1">Baixa complexidade (Verde)</p>
            </div>
            <div class="bg-red-50 text-red-600 p-3 rounded-lg">
              <ExclamationTriangleIcon class="h-6 w-6" />
            </div>
          </div>
        </div>

        <!-- Detail Metrics Lists Row 1 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Specialties Distribution -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Demanda por Especialidade</h3>
              <p class="text-xs text-gray-400 mt-0.5">Ranking de solicitações por especialidade.</p>
            </template>
            
            <div class="space-y-4 mt-4" v-if="stats.specialties_distribution.length > 0">
              <div v-for="item in stats.specialties_distribution" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-gray-700">{{ item.name }}</span>
                  <span class="font-bold text-blue-600">{{ item.count }}</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div 
                    class="bg-blue-600 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxSpecialtyCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Nenhum dado registrado.</p>
          </Card>

          <!-- Pending Specialties -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Especialidades com Mais Pendências</h3>
              <p class="text-xs text-gray-400 mt-0.5">Ranking de solicitações pendentes por especialidade.</p>
            </template>
            
            <div class="space-y-4 mt-4" v-if="stats.especialidades_mais_pendencias.length > 0">
              <div v-for="item in stats.especialidades_mais_pendencias" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-gray-700">{{ item.name }}</span>
                  <span class="font-bold text-amber-600">{{ item.count }} pendentes</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div 
                    class="bg-amber-500 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxPendingCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Nenhuma solicitação pendente.</p>
          </Card>
        </div>

        <!-- Detail Metrics Lists Row 2 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Top Requesting Doctors -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-gray-800">Médicos Mais Solicitantes</h3>
              <p class="text-xs text-gray-400 mt-0.5">Volume total de solicitações enviadas.</p>
            </template>

            <div class="space-y-4 mt-4" v-if="stats.top_doctors.length > 0">
              <div v-for="item in stats.top_doctors" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-gray-700">{{ item.name }}</span>
                  <span class="font-bold text-gray-900">{{ item.count }}</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div 
                    class="bg-gray-600 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxDoctorCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Nenhum médico registrou pedidos.</p>
          </Card>

          <!-- Inappropriate Requests (VERDE) ranking -->
          <Card class="shadow-sm border border-gray-200">
            <template #header>
              <h3 class="text-md font-bold text-red-700 flex items-center gap-1">
                <ExclamationTriangleIcon class="h-5 w-5 text-red-500" />
                Casos Indevidos por Médico
              </h3>
              <p class="text-xs text-gray-400 mt-0.5">Médicos com maior taxa de solicitações VERDE.</p>
            </template>

            <div class="space-y-4 mt-4" v-if="stats.inappropriate_doctors.length > 0">
              <div v-for="item in stats.inappropriate_doctors" :key="item.name" class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span class="font-semibold text-red-700">{{ item.name }}</span>
                  <span class="font-bold text-red-600">{{ item.count }}</span>
                </div>
                <div class="w-full bg-red-50 rounded-full h-1.5">
                  <div 
                    class="bg-red-500 h-1.5 rounded-full" 
                    :style="{ width: (item.count / maxInappropriateCount) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400 text-center py-6">Excelente! Nenhuma solicitação indevida registrada.</p>
          </Card>
        </div>
      </div>
    </div>

    <!-- Modal Criar -->
    <Modal :show="mostrarModalCriar" @close="mostrarModalCriar = false">
      <template #header>Cadastrar Novo Usuário</template>
      
      <form @submit.prevent="salvarNovoUsuario" class="space-y-4">
        <div class="form-group">
          <label class="form-label">Nome de Usuário (login)</label>
          <input 
            type="text" 
            v-model="novoUser.username" 
            class="form-control" 
            required 
            placeholder="Ex: joao_medico"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">Senha</label>
          <input 
            type="password" 
            v-model="novoUser.password" 
            class="form-control" 
            required 
            placeholder="Mínimo 6 caracteres"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Nome de Exibição (Completo)</label>
          <input 
            type="text" 
            v-model="novoUser.display_name" 
            class="form-control" 
            required 
            placeholder="Ex: Dr. João da Silva"
          />
        </div>

        <div class="form-group">
          <label class="form-label">E-mail</label>
          <input 
            type="email" 
            v-model="novoUser.email" 
            class="form-control" 
            placeholder="Ex: joao@ufpe.br"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Perfil de Acesso</label>
          <select v-model="novoUser.role" class="form-control" required>
            <option value="medico">Médico Solicitante</option>
            <option value="regulador">Regulador (Central de Marcação)</option>
            <option value="admin">Administrador</option>
          </select>
        </div>

        <p v-if="erroForm" class="text-xs text-red-500 font-semibold">{{ erroForm }}</p>
      </form>

      <template #footer>
        <Button variant="default" @click="mostrarModalCriar = false">Cancelar</Button>
        <Button variant="primary" :loading="salvando" @click="salvarNovoUsuario">Salvar</Button>
      </template>
    </Modal>

    <!-- Modal Editar -->
    <Modal :show="mostrarModalEditar" @close="mostrarModalEditar = false">
      <template #header>Editar Usuário: @{{ userEditando?.username }}</template>
      
      <form @submit.prevent="salvarEdicaoUsuario" class="space-y-4">
        <div class="form-group">
          <label class="form-label">Nome de Exibição (Completo)</label>
          <input 
            type="text" 
            v-model="userEditandoForm.display_name" 
            class="form-control" 
            required 
            placeholder="Ex: Dr. João da Silva"
          />
        </div>

        <div class="form-group">
          <label class="form-label">E-mail</label>
          <input 
            type="email" 
            v-model="userEditandoForm.email" 
            class="form-control" 
            placeholder="Ex: joao@ufpe.br"
          />
        </div>

        <div class="form-group" v-if="userEditando?.username !== 'admin'">
          <label class="form-label">Perfil de Acesso</label>
          <select v-model="userEditandoForm.role" class="form-control" required>
            <option value="medico">Médico Solicitante</option>
            <option value="regulador">Regulador (Central de Marcação)</option>
            <option value="admin">Administrador</option>
          </select>
        </div>

        <p v-if="erroForm" class="text-xs text-red-500 font-semibold">{{ erroForm }}</p>
      </form>

      <template #footer>
        <Button variant="default" @click="mostrarModalEditar = false">Cancelar</Button>
        <Button variant="primary" :loading="salvando" @click="salvarEdicaoUsuario">Salvar Alterações</Button>
      </template>
    </Modal>
  </div>
  <div v-else class="text-center py-12">
    <Card class="max-w-md mx-auto">
      <h1 class="text-2xl font-bold text-red-600">Acesso Negado</h1>
      <p class="mt-4 text-gray-500">Você não tem privilégios suficientes para acessar a área administrativa.</p>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import { 
  UserGroupIcon, 
  UserPlusIcon, 
  PencilSquareIcon, 
  TrashIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  InboxIcon,
  QueueListIcon,
  ClipboardDocumentListIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const abaAtiva = ref('usuarios');
const users = ref<any[]>([]);
const stats = ref<any>(null);
const pacientes = ref<any[]>([]);

const loading = ref(false);
const loadingStats = ref(false);
const loadingPacientes = ref(false);
const salvando = ref(false);
const erroForm = ref('');

// Modais
const mostrarModalCriar = ref(false);
const mostrarModalEditar = ref(false);

// Forms
const novoUser = ref({
  username: '',
  password: '',
  display_name: '',
  email: '',
  role: 'medico'
});

const userEditando = ref<any>(null);
const userEditandoForm = ref({
  display_name: '',
  email: '',
  role: 'medico'
});

const carregarUsuarios = async () => {
  if (!authStore.isAdmin) return;
  loading.value = true;
  try {
    const { data } = await api.get('/api/admin/users');
    users.value = data;
  } catch (error: any) {
    console.error("Erro ao carregar usuários:", error);
  } finally {
    loading.value = false;
  }
};

const carregarEstatisticas = async () => {
  if (!authStore.isAdmin) return;
  loadingStats.value = true;
  try {
    const { data } = await api.get('/api/admin/statistics');
    stats.value = data;
  } catch (error: any) {
    console.error("Erro ao carregar estatísticas:", error);
  } finally {
    loadingStats.value = false;
  }
};

const exportandoExcel = ref(false);
const exportarExcel = async () => {
  exportandoExcel.value = true;
  try {
    const response = await api.get('/api/admin/statistics/export', {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'analytics_interhc.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    console.error("Erro ao exportar estatísticas:", error);
  } finally {
    exportandoExcel.value = false;
  }
};

const especialidades = ref<any[]>([]);
const sintomas = ref<any[]>([]);
const regras = ref<any[]>([]);
const loadingCatalog = ref(false);
const salvandoCatalog = ref(false);
const erroFormCatalog = ref('');

const mostrarModalCriarEsp = ref(false);
const mostrarModalCriarSint = ref(false);

const novaEsp = ref({ nome: '' });
const novoSint = ref({ nome: '', pontuacao: 1, especialidade_id: 1 });
const novaRegra = ref({ sintoma_id: 1, especialidade_id: 1, pontuacao: 5 });
const salvandoRegra = ref(false);

// Filtros para o Catálogo de Sintomas
const especialidadeFiltro = ref<number | 'todas'>('todas');
const buscaSintoma = ref('');

const contarSintomasDaEspecialidade = (espId: number) => {
  return regras.value.filter(r => r.especialidade_id === espId && !r.deleted_at).length;
};

const obterPontuacaoExibicao = (sint: any) => {
  if (especialidadeFiltro.value === 'todas') {
    return sint.pontuacao;
  }
  const rule = regras.value.find(r => r.sintoma_id === sint.id && r.especialidade_id === especialidadeFiltro.value && !r.deleted_at);
  return rule ? rule.pontuacao : sint.pontuacao;
};

const obterEspecialidadesSintoma = (sintId: number) => {
  const ids = regras.value.filter(r => r.sintoma_id === sintId && !r.deleted_at).map(r => r.especialidade_id);
  return especialidades.value.filter(e => ids.includes(e.id));
};

const sintomasFiltrados = computed(() => {
  let list = sintomas.value;
  
  if (especialidadeFiltro.value !== 'todas') {
    const espId = especialidadeFiltro.value;
    const sintomasComRegra = new Set(
      regras.value
        .filter(r => r.especialidade_id === espId && !r.deleted_at)
        .map(r => r.sintoma_id)
    );
    list = list.filter(s => sintomasComRegra.has(s.id));
  }
  
  if (buscaSintoma.value.trim()) {
    const term = buscaSintoma.value.toLowerCase().trim();
    list = list.filter(s => s.nome.toLowerCase().includes(term));
  }
  
  return list;
});

const carregarCatalogos = async () => {
  loadingCatalog.value = true;
  try {
    const resEsp = await api.get('/api/admin/especialidades');
    especialidades.value = resEsp.data;
    
    const resSint = await api.get('/api/admin/sintomas');
    sintomas.value = resSint.data;
    
    const resReg = await api.get('/api/admin/regras');
    regras.value = resReg.data;

    if (sintomas.value.length > 0) novaRegra.value.sintoma_id = sintomas.value[0].id;
    if (especialidades.value.length > 0) novaRegra.value.especialidade_id = especialidades.value[0].id;
  } catch (error) {
    console.error("Erro ao carregar catálogos:", error);
  } finally {
    loadingCatalog.value = false;
  }
};

const abrirModalCriarEsp = () => {
  novaEsp.value = { nome: '' };
  erroFormCatalog.value = '';
  mostrarModalCriarEsp.value = true;
};

const salvarNovaEspecialidade = async () => {
  erroFormCatalog.value = '';
  salvandoCatalog.value = true;
  try {
    await api.post('/api/admin/especialidades', novaEsp.value);
    mostrarModalCriarEsp.value = false;
    await carregarCatalogos();
  } catch (error: any) {
    erroFormCatalog.value = error.response?.data?.detail || "Erro ao salvar especialidade.";
  } finally {
    salvandoCatalog.value = false;
  }
};

const confirmarInativarEsp = async (esp: any) => {
  if (confirm(`Tem certeza que deseja remover a especialidade "${esp.nome}"?`)) {
    try {
      await api.delete(`/api/admin/especialidades/${esp.id}`);
      await carregarCatalogos();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao remover especialidade.");
    }
  }
};

const abrirModalCriarSint = () => {
  novoSint.value = { 
    nome: '', 
    pontuacao: 1, 
    especialidade_id: especialidades.value.length > 0 ? especialidades.value[0].id : 1 
  };
  erroFormCatalog.value = '';
  mostrarModalCriarSint.value = true;
};

const salvarNovoSintoma = async () => {
  erroFormCatalog.value = '';
  salvandoCatalog.value = true;
  try {
    await api.post('/api/admin/sintomas', novoSint.value);
    mostrarModalCriarSint.value = false;
    await carregarCatalogos();
  } catch (error: any) {
    erroFormCatalog.value = error.response?.data?.detail || "Erro ao salvar sintoma.";
  } finally {
    salvandoCatalog.value = false;
  }
};

const confirmarInativarSint = async (sint: any) => {
  if (confirm(`Tem certeza que deseja remover o sintoma "${sint.nome}"?`)) {
    try {
      await api.delete(`/api/admin/sintomas/${sint.id}`);
      await carregarCatalogos();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao remover sintoma.");
    }
  }
};

const salvarRegra = async () => {
  salvandoRegra.value = true;
  try {
    await api.post('/api/admin/regras', novaRegra.value);
    await carregarCatalogos();
    alert("Regra de pontuação salva com sucesso!");
  } catch (error: any) {
    alert(error.response?.data?.detail || "Erro ao salvar regra.");
  } finally {
    salvandoRegra.value = false;
  }
};

const confirmarInativarRegra = async (reg: any) => {
  if (confirm(`Deseja remover a regra customizada para este sintoma nesta especialidade?`)) {
    try {
      await api.delete(`/api/admin/regras/${reg.sintoma_id}/${reg.especialidade_id}`);
      await carregarCatalogos();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao remover regra.");
    }
  }
};

const obterNomeSintoma = (id: number) => {
  const s = sintomas.value.find(x => x.id === id);
  return s ? s.nome : `Sintoma ${id}`;
};

const obterNomeEspecialidade = (id: number) => {
  const e = especialidades.value.find(x => x.id === id);
  return e ? e.nome : `Especialidade ${id}`;
};

const scoreClass = (score: number) => {
  if (score >= 10) return 'bg-red-100 text-red-700';
  if (score >= 5) return 'bg-amber-100 text-amber-700';
  return 'bg-green-100 text-green-700';
};

const carregarPacientes = async () => {
  if (!authStore.isAdmin) return;
  loadingPacientes.value = true;
  try {
    const { data } = await api.get('/api/pacientes');
    pacientes.value = data;
  } catch (error: any) {
    console.error("Erro ao carregar pacientes:", error);
  } finally {
    loadingPacientes.value = false;
  }
};

const alterarAba = (aba: string) => {
  abaAtiva.value = aba;
  if (aba === 'usuarios') {
    carregarUsuarios();
  } else if (aba === 'estatisticas') {
    carregarEstatisticas();
  } else if (aba === 'especialidades') {
    carregarCatalogos();
  } else if (aba === 'sintomas') {
    carregarCatalogos();
  } else if (aba === 'pacientes') {
    carregarPacientes();
  }
};

onMounted(() => {
  carregarUsuarios();
});

// Computed Stats Properties

const totalIndevidas = computed(() => {
  if (!stats.value) return 0;
  return stats.value.inappropriate_doctors.reduce((acc: number, item: any) => acc + item.count, 0);
});

const maxSpecialtyCount = computed(() => {
  if (!stats.value || stats.value.specialties_distribution.length === 0) return 1;
  return Math.max(...stats.value.specialties_distribution.map((item: any) => item.count));
});

const maxDoctorCount = computed(() => {
  if (!stats.value || stats.value.top_doctors.length === 0) return 1;
  return Math.max(...stats.value.top_doctors.map((item: any) => item.count));
});

const maxInappropriateCount = computed(() => {
  if (!stats.value || stats.value.inappropriate_doctors.length === 0) return 1;
  return Math.max(...stats.value.inappropriate_doctors.map((item: any) => item.count));
});

const maxPendingCount = computed(() => {
  if (!stats.value || !stats.value.especialidades_mais_pendencias || stats.value.especialidades_mais_pendencias.length === 0) return 1;
  return Math.max(...stats.value.especialidades_mais_pendencias.map((item: any) => item.count));
});

const roleLabel = (role: string) => {
  if (role === 'admin') return 'Administrador';
  if (role === 'medico') return 'Médico';
  if (role === 'regulador') return 'Regulador';
  return role;
};

const roleClass = (role: string) => {
  if (role === 'admin') return 'bg-purple-100 text-purple-700';
  if (role === 'medico') return 'bg-green-100 text-green-700';
  if (role === 'regulador') return 'bg-blue-100 text-blue-700';
  return 'bg-gray-100 text-gray-700';
};

const abrirModalCriar = () => {
  novoUser.value = {
    username: '',
    password: '',
    display_name: '',
    email: '',
    role: 'medico'
  };
  erroForm.value = '';
  mostrarModalCriar.value = true;
};

const salvarNovoUsuario = async () => {
  erroForm.value = '';
  salvando.value = true;
  try {
    await api.post('/api/admin/users', novoUser.value);
    mostrarModalCriar.value = false;
    await carregarUsuarios();
  } catch (error: any) {
    erroForm.value = error.response?.data?.detail || "Erro ao salvar usuário. Verifique se o username já existe.";
  } finally {
    salvando.value = false;
  }
};

const abrirModalEditar = (u: any) => {
  userEditando.value = u;
  userEditandoForm.value = {
    display_name: u.display_name,
    email: u.email || '',
    role: u.role
  };
  erroForm.value = '';
  mostrarModalEditar.value = true;
};

const salvarEdicaoUsuario = async () => {
  erroForm.value = '';
  salvando.value = true;
  try {
    await api.put(`/api/admin/users/${userEditando.value.id}`, userEditandoForm.value);
    mostrarModalEditar.value = false;
    await carregarUsuarios();
  } catch (error: any) {
    erroForm.value = error.response?.data?.detail || "Erro ao salvar alterações.";
  } finally {
    salvando.value = false;
  }
};

const confirmarInativar = async (u: any) => {
  if (confirm(`Tem certeza que deseja inativar/desativar o usuário @${u.username}?`)) {
    try {
      await api.delete(`/api/admin/users/${u.id}`);
      await carregarUsuarios();
    } catch (error: any) {
      alert("Erro ao inativar usuário.");
    }
  }
};
</script>