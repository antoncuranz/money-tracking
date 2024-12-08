import {create, StateCreator} from 'zustand'
import {Account, Credit} from "@/types.ts";

type SelectionSlice = {
  currentAccount: Account | null;
  creditSelection: Credit | null;
  exchangeSelection: number | null;
  setCurrentAccount: (value: SelectionSlice["currentAccount"]) => void;
  setCreditSelection: (value: SelectionSlice["creditSelection"], accounts: Account[]) => void;
  setExchangeSelection: (value: SelectionSlice["exchangeSelection"]) => void;
};

const createSelectionSlice: StateCreator<
  SelectionSlice,
  [],
  [],
  SelectionSlice
> = (set) => ({
  currentAccount: null,
  creditSelection: null,
  exchangeSelection: null,
  setCurrentAccount: (currentAccount) => set(() => ({ currentAccount: currentAccount })),
  setCreditSelection: (value, accounts) => set((state) => ({
    creditSelection: value, currentAccount: accounts.find(acct => acct.id == value?.account_id) ?? state.currentAccount
  })),
  setExchangeSelection: (exchangeSelection) => set(() => ({ exchangeSelection: exchangeSelection })),
})

type TransactionAmountSlice = {
  changedTransactionAmounts: {[id: number]: number|null};
  clearTransactionAmounts: () => void,
  putTransactionAmount: (id: number, amount: number|null) => void,
};

const createTransactionAmountSlice: StateCreator<
  TransactionAmountSlice,
  [],
  [],
  TransactionAmountSlice
> = (set) => ({
  changedTransactionAmounts: {},
  clearTransactionAmounts: () => set(() => ({ changedTransactionAmounts: {} })),
  putTransactionAmount: (id, amount) => set((state) => ({ changedTransactionAmounts: { ...state.changedTransactionAmounts, [id]: amount } })),
})

export const useStore = create<SelectionSlice & TransactionAmountSlice>()((...a) => ({
  ...createSelectionSlice(...a),
  ...createTransactionAmountSlice(...a),
}))