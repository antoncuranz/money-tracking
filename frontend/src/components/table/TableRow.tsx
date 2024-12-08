import {Account} from "@/types.ts";
import React, {CSSProperties, MouseEventHandler} from "react";

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
    <div onClick={onClick} className={"containers tx-row-border " + className} style={{...style, borderLeftWidth: "4px", borderLeftColor: account?.color ?? "transparent"}}>
      <div className="left">
        <div className="date text-sm text-muted-foreground">{date}</div>
        <div className="remoteName font-medium">{remoteName}</div>
        <div className="purpose">{purpose}</div>
      </div>
      <div className="right">
        {children}
      </div>
    </div>
  )
}
