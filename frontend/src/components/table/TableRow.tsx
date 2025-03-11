import {Account} from "@/types.ts";
import React, {CSSProperties, MouseEventHandler} from "react";
import PrivacyFilter from "@/components/PrivacyFilter.tsx";
import {formatDate} from "@/components/util.ts";

export default function TableRow({
  account,
  date,
  remoteName,
  purpose,
  children,
  onClick,
  className,
  style
}: {
  account?: Account,
  date: string,
  remoteName: string,
  purpose: string,
  children?: React.ReactNode,
  onClick?: MouseEventHandler<HTMLTableRowElement> | undefined;
  className?: string,
  style?: CSSProperties | undefined;
}) {
  
  return (
    <PrivacyFilter onClick={onClick} className={"containers tx-row-border " + className} style={{...style, borderLeftWidth: "4px", borderLeftColor: account?.color ?? "transparent"}}>
      <div className="left">
        <div className="date text-sm text-muted-foreground">{formatDate(date)}</div>
        <div className="remoteName font-medium">{remoteName}</div>
        <div className="purpose">{purpose}</div>
      </div>
      <div className="right">
        {children}
      </div>
    </PrivacyFilter>
  )
}
