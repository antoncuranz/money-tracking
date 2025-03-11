export type User = {
  id: number;
  name: string;
  super_user: boolean;
};

export type Account = {
  id: number;
  user: User;
  bank_account_id: number | null;
  actual_id: string;
  plaid_account_id: number | null;
  name: string;
  institution: string;
  due_day: number | null;
  autopay_offset: number | null;
  icon: string | null;
  color: string | null;
  target_spend: number | null;
};

export type BankAccount = {
  id: number;
  user: User;
  name: string;
  institution: string;
  icon: string | null;
  balance: number;
  plaid_account_id: number | null;
};

export type Credit = {
  id: number;
  account_id: number;
  import_id: string;
  date: string;
  counterparty: string;
  description: string;
  category: string;
  amount_usd: number;
  transactions: CreditTransaction[];
};

export type CreditTransaction = {
  amount: number;
  credit_id: number;
  transaction_id: number;
};

export type Transaction = {
  id: number;
  account_id: number;
  import_id: string;
  actual_id: number | null;
  date: string;
  counterparty: string;
  description: string;
  category: string;
  amount_usd: number;
  amount_eur: number | null;
  guessed_amount_eur: number | null;
  status: number;
  payment: number | null;
  fees_and_risk_eur: number | null;
  credits: CreditTransaction[];
  ignore: boolean | null;
};

export type Exchange = {
  id: number;
  actual_id: number | null;
  date: string;
  amount_usd: number;
  exchange_rate: number;
  amount_eur: number | null;
  paid_eur: number;
  fees_eur: number | null;
  payments: ExchangePayment[];
};

export type ExchangePayment = {
  amount: number;
  exchange_id: number;
  payment_id: number;
};

export type Payment = {
  id: number;
  account_id: number;
  import_id: string;
  actual_id: number | null;
  date: string;
  counterparty: string;
  description: string;
  category: string;
  amount_usd: number;
  amount_eur: number;
  status: number;
  exchanges: ExchangePayment[];
};

export type Balances = {
  total: number;
  posted: number;
  pending: number;
  credits: number;
  exchanged: number;
  virtual_account: number;
};

export type AccountBalances = { [id: string] : AccountBalance };

export type AccountBalance = {
  posted: number;
  pending: number;
  total_spent: number;
  total_credits: number;
}

export type FeeSummary = {
  fees_and_risk_eur: number;
};

export type AccountDates = {
  color: string;
  due: string;
  statement: string;
};

export type PlaidAccount = {
  id: number;
  name: string;
  plaid_account_id: string;
  connection_id: number;
};

export type PlaidConnection = {
  id: number;
  user: User;
  name: string | null;
  plaid_item_id: string;
  plaid_accounts: PlaidAccount[];
};
