import {fetchPlaidConnections} from "@/requests.ts";
import React from "react";
import ConnectionsCardContent from "@/components/card/ConnectionsCardContent.tsx";

export default async function ConnectionsCard() {
  const connections = await fetchPlaidConnections()

  return (
    <ConnectionsCardContent connections={connections}/>
  )
}
