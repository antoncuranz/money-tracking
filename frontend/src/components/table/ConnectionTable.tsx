"use client"

import {PlaidConnection} from "@/types.ts";
import ConnectionRow from "@/components/table/ConnectionRow.tsx";
import {useToast} from "@/components/ui/use-toast.ts";
import {useRouter} from "next/navigation";

export default function ConnectionTable({connections}: {
  connections: PlaidConnection[],
}) {
  const { toast } = useToast();
  const router = useRouter();
  
  async function deleteConnection(connectionId: number) {
    const url = "/api/import/plaid/connections/" + connectionId
    const response = await fetch(url, {method: "DELETE"})

    if (response.ok)
      router.refresh()
    else toast({
      title: "Error deleting Connection",
      description: response.statusText
    })
  }
  
  async function discoverAccounts(connectionId: number) {
    const url = "/api/import/plaid/connections/" + connectionId + "/discover"
    const response = await fetch(url, {method: "POST"})

    if (response.ok)
      router.refresh()
    else toast({
      title: "Error discovering accounts",
      description: response.statusText
    })
  }

  return (
    <div className="w-full relative">
      {connections.map(connection =>
        <ConnectionRow key={connection.id} connection={connection}
                       deleteConnection={() => deleteConnection(connection.id)}
                       discoverAccounts={() => discoverAccounts(connection.id)}
        />
      )}
    </div>
  )
}
