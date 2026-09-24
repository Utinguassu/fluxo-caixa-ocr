# 📜 Documentação de Requisitos e Regras de Negócio

## Visão Geral (Versão 1 - MVP)

### Requisitos Funcionais
* **RN01:** O sistema deve permitir a importação de PRINTs via navegador mobile para lançamentos de débito.
  * **RN01.01:** O usuário deve sinalizar se o print é de fatura de cartão ou pagamento avulso (Pix/Conta).
* **RN02:** O sistema deve ler a imagem (OCR) e identificar o Tipo, Valor, Data e Estabelecimento. O desconto deve ocorrer automaticamente.
* **RN03:** O Dashboard inicial deve exibir o Saldo Inicial cadastrado, o Total de Débitos e o Saldo Atualizado em tempo real.
* **RN04:** O extrato detalhado (Timeline) deve ordenar do lançamento mais recente para o mais antigo, mostrando os valores deduzidos em vermelho com o sinal negativo (-).
* **RN05:** É obrigatório o cadastro de um Saldo Inicial antes de qualquer lançamento.
  * **RN05.01:** O Saldo Inicial pode ser atualizado. O sistema deve guardar o histórico de saldos cadastrados, mas utilizar sempre o mais recente para os cálculos atuais.
* **RN06:** O sistema deve possuir autenticação (Login) via e-mail e senha de 6 dígitos.
* **RN07:** O sistema deve garantir o isolamento de dados, exibindo apenas as movimentações do usuário logado.
* **RN08:** Deve existir uma tela administrativa para cadastro de novos usuários.

### Requisitos Não Funcionais
* A V1 deve rodar e ser acessível exclusivamente na rede interna via navegador iOS (iPhone).
* A arquitetura deve permitir conexão de ferramentas de administração de banco de dados (ex: DBeaver) para consultas SQL diretas.

---
## Visão de Futuro (Versão 2)
* Exportação de relatórios da Timeline para Excel (filtrado por período).
* Autenticação em Dois Fatores (2FA) via e-mail.
* Migração da aplicação para Cloud Pública com acesso via internet externa.
