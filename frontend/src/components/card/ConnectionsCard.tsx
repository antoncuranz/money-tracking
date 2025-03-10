import {fetchPlaidConnections} from "@/requests.ts";
import Card from "@/components/card/Card.tsx";
import PlaidLinkButton from "@/components/buttons/PlaidLinkButton.tsx";
import React from "react";
import ConnectionTable from "@/components/table/ConnectionTable.tsx";

export default async function ConnectionsCard() {
  const connections = await fetchPlaidConnections()

  return (
    <Card title="Plaid Connections" headerSlot={<PlaidLinkButton/>}>
        <ConnectionTable connections={connections}/>
    </Card>
  )
}