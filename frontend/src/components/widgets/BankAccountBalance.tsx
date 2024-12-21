import {formatAmount} from "@/components/util.ts";
import {BankAccount} from "@/types.ts";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";

interface Props {
  bankAccount: BankAccount
}

const BankAccountBalance = ({bankAccount}: Props) => {
  
  return (
    <div>
      <img className="w-8 mr-2 mt-3 inline-block align-top flex-init" src={bankAccount.icon} alt=""/>
      <div className="inline-block flex-auto">
        <p className="font-medium">{bankAccount.name}</p>
        <p className="text-sm text-muted-foreground">{bankAccount.institution}</p>
        <PrivacyFilter className="mt-2">
          <span className="font-medium">{formatAmount(bankAccount.balance)}</span>
        </PrivacyFilter>
      </div>
    </div>
  )
}

export default BankAccountBalance