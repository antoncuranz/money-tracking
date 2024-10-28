type Account = {
  id: number;
  actual_id: string;
  teller_id?: string;
  teller_access_token?: string;
  teller_enrollment_id?: string;
  name: string;
  institution: string;
};

type Credit = {
  id: number;
  account_id: number;
  teller_id: string;
  date: string;
  counterparty: string;
  description: string;
  category: string;
  amount_usd: number;
  credittransaction_set: CreditTransaction[];
};

type CreditTransaction = {
  amount: number;
  credit: Credit;
  transaction: Transaction;
};

type Transaction = {
  id: number;
  account_id: number;
  teller_id: string;
  actual_id: number | null;
  date: string;
  counterparty: string;
  description: string;
  category: string;
  amount_usd: number;
  amount_eur: number | null;
  status: number;
  payment: number | null;
  fees_and_risk_eur: number | null;
  credittransaction_set: CreditTransaction[];
  ignore: boolean | null;
};

type Exchange = {
  id: number;
  actual_id: number | null;
  date: string;
  amount_usd: number;
  exchange_rate: number;
  amount_eur: number | null;
  paid_eur: number;
  fees_eur: number | null;
  exchangepayment_set: ExchangePayment[];
};

type ExchangePayment = {
  amount: number;
  exchange: Exchange;
  payment: Payment;
};

type Payment = {
  id: number;
  account_id: number;
  teller_id: string;
  actual_id: number | null;
  date: string;
  counterparty: string;
  description: string;
  category: string;
  amount_usd: number;
  amount_eur: number;
  processed: boolean;
  exchangepayment_set: ExchangePayment[];
};

type Balances = {
  total: number;
  posted: number;
  pending: number;
  credits: number;
  exchanged: number;
  virtual_account: number;
};

type FeeSummary = {
  fees_and_risk_eur: number;
};