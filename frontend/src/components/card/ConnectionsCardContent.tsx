"use client"

import {PlaidConnection} from "@/types.ts";
import Card from "@/components/card/Card.tsx";
import PlaidLinkButton from "@/components/buttons/PlaidLinkButton.tsx";
import ConnectionTable from "@/components/table/ConnectionTable.tsx";
import {useState} from "react";

export default function ConnectionsCardContent({connections}: {
  connections: PlaidConnection[]
}) {
  const [selectedUpdateId, setSelectedUpdateId] = useState<number | null>(null)

  return (
    <Card title="Plaid Connections" headerSlot={
      <PlaidLinkButton
        key={selectedUpdateId ?? 'new'}
        updateId={selectedUpdateId ?? undefined}
        onDone={() => setSelectedUpdateId(null)}
      />
    }>
      <ConnectionTable
        connections={connections}
        selectedUpdateId={selectedUpdateId}
        onSelectUpdate={setSelectedUpdateId}
      />
    </Card>
  )
}
