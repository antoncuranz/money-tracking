'use client';

import React, { createContext, useContext, useState } from 'react';
import {Account, Credit} from "@/types.ts";

type SelectionContextType = {
  currentAccount: Account | null;
  setCurrentAccount: (value: Account | null) => void;
  creditSelection: Credit | null;
  setCreditSelection: (value: Credit | null, accounts: Account[]) => void;
};

const SelectionContextDefaultValues: SelectionContextType = {
  currentAccount: null,
  setCurrentAccount: () => {},
  creditSelection: null,
  setCreditSelection: () => {},
};

const SelectionStateContext = createContext<SelectionContextType>(SelectionContextDefaultValues);

export const SelectionStateProvider = ({
  children
}: {
  children: React.ReactNode
}) => {
  const [currentAccount, setCurrentAccount] = useState<Account|null>(null)
  const [creditSelection, setCreditSelectionInternal] = useState<Credit|null>(null)

  function setCreditSelection(value: Credit | null, accounts: Account[]) {
    setCreditSelectionInternal(value)

    if (!value)
      return;

    const acct = accounts.find(acct => acct.id == value.account_id)
    if (acct)
      setCurrentAccount(acct)
  }

  return (
    <SelectionStateContext.Provider value={{ currentAccount, setCurrentAccount, creditSelection, setCreditSelection }}>
      {children}
    </SelectionStateContext.Provider>
  );
};

export const useSelectionState = () => {
  return useContext(SelectionStateContext);
};