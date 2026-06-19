"use client"

import SaveAmountsButton from "@/components/buttons/SaveAmountsButton.tsx";
import {useStore} from "@/store.ts";

const TxSaveButton = () => {
  const {changedTransactionAmounts, clearTransactionAmounts} = useStore()

  return <SaveAmountsButton amounts={changedTransactionAmounts} onSuccess={clearTransactionAmounts}/>
}

export default TxSaveButton