# Interfaces e Integrações

## 1. Protótipos
* A fazer

## 2. Hardware
* A fazer

## 3. Software
* Integração com AGHU. 

### [SCHEMA] Interface de Integração (TypeScript)
```typescript
interface IHospitalApi {
  getPatientData(id: string): Promise<PatientRecord>;
  syncProntuario(data: ProntuarioUpdate): Promise<SyncResponse>;
  checkLdapAuth(credentials: AuthInfo): Promise<AuthStatus>;
}
```
