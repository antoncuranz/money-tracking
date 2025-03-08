export type Account = {
  id: number;
  actual_id: string;
  import_id?: string;
  name: string;
  institution: string;
  due_day?: number;
  autopay_offset?: number;
  icon?: string;
  color?: string;
  target_spend?: number;
};

export type BankAccount = {
  id: number;
  import_id?: string;
  name: string;
  institution: string;
  icon?: string;
  balance: number;
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
