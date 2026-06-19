"use client"

import {useMemo, useRef, useState} from "react";
import Card from "@/components/card/Card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";
import {Account} from "@/types.ts";
import {FileUp, Upload} from "lucide-react";
import {cn} from "@/lib/utils.ts";

interface Props {
  accounts: Account[];
  selectedAccountId: string;
  onSelectedAccountIdChange: (value: string) => void;
  disabledAccountIds: Set<number>;
  onUpload: (accountId: number, file: File) => void;
}

const StatementMatchSidebar = ({
  accounts,
  selectedAccountId,
  onSelectedAccountIdChange,
  disabledAccountIds,
  onUpload,
}: Props) => {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const selectedAccount = useMemo(
    () => accounts.find(account => account.id.toString() === selectedAccountId) ?? null,
    [accounts, selectedAccountId]
  )

  const uploadDisabled = file == null || selectedAccount == null || disabledAccountIds.has(selectedAccount.id)

  function setPdfFile(nextFile: File | null) {
    if (nextFile == null) {
      setFile(null)
      return
    }

    if (nextFile.type === "application/pdf" || nextFile.name.toLowerCase().endsWith(".pdf"))
      setFile(nextFile)
  }

  function openPicker() {
    inputRef.current?.click()
  }

  function submit() {
    if (selectedAccount == null || file == null || disabledAccountIds.has(selectedAccount.id))
      return

    onUpload(selectedAccount.id, file)
    setFile(null)
  }

  function getAccountLabel(account: Account) {
    return account.name
  }

  return (
    <Card title="Upload Statement">
      <div className="p-4 space-y-4">
        <div className="space-y-2">
          <div className="text-sm font-medium">Account</div>
          <Select value={selectedAccountId} onValueChange={onSelectedAccountIdChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select an account"/>
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {accounts.map(account =>
                  <SelectItem key={account.id} value={account.id.toString()} disabled={disabledAccountIds.has(account.id)}>
                    {getAccountLabel(account)}
                  </SelectItem>
                )}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={event => setPdfFile(event.target.files?.[0] ?? null)}
        />

        <button
          type="button"
          className={cn(
            "w-full rounded-md border border-dashed border-input p-6 text-left transition-colors",
            dragActive && "border-primary bg-muted"
          )}
          onClick={openPicker}
          onDragOver={event => {
            event.preventDefault()
            setDragActive(true)
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={event => {
            event.preventDefault()
            setDragActive(false)
            setPdfFile(event.dataTransfer.files[0] ?? null)
          }}
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <FileUp className="h-8 w-8 text-muted-foreground"/>
            <div className="font-medium">Drop a PDF here</div>
            <div className="text-sm text-muted-foreground">or click to choose a statement file</div>
            {file != null &&
              <div className="max-w-full truncate text-sm text-foreground">{file.name}</div>
            }
          </div>
        </button>

        <Button className="w-full gap-2" onClick={submit} disabled={uploadDisabled}>
          <Upload className="h-4 w-4"/>
          Upload Statement
        </Button>
      </div>
    </Card>
  )
}

export default StatementMatchSidebar
