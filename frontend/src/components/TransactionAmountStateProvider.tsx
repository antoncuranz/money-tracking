'use client';

import React, {createContext, useContext, useState} from 'react';

type TransactionAmountContextType = {
  changedTransactionAmounts: {[id: number]: number|null};
  setChangedTransactionAmounts: (value: {[id: number]: number|null}) => void;
};

const TransactionAmountContextDefaultValues: TransactionAmountContextType = {
  changedTransactionAmounts: {},
  setChangedTransactionAmounts: () => {}
};

const TransactionAmountStateContext = createContext<TransactionAmountContextType>(TransactionAmountContextDefaultValues);

export const TransactionAmountStateProvider = ({
  children
}: {
  children: React.ReactNode
}) => {
  const [changedTransactionAmounts, setChangedTransactionAmounts] = useState<{[id: number]: number|null}>({})

  return (
    <TransactionAmountStateContext.Provider value={{ changedTransactionAmounts, setChangedTransactionAmounts }}>
      {children}
    </TransactionAmountStateContext.Provider>
  );
};

export const useTransactionAmountState = () => {
  return useContext(TransactionAmountStateContext);
};