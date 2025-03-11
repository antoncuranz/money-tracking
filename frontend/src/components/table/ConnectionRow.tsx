import {LoaderCircle, Telescope, Trash2} from "lucide-react";
import {Button} from "@/components/ui/button.tsx";
import {PlaidConnection} from "@/types.ts";
import React, {useState} from "react";
import {titlecase} from "@/components/util.ts";
import {useUser} from "@/components/provider/UserProvider.tsx";

export default function ConnectionRow({
  connection, deleteConnection, discoverAccounts
}: {
  connection: PlaidConnection,
  deleteConnection: () => void,
  discoverAccounts: () => void,
}) {
  const [discoverInProgress, setDiscoverInProgress] = useState(false)
  const [deletionInProgress, setDeletionInProgress] = useState(false)
  
  const {username} = useUser()

  async function privateDiscoverAccounts() {
    setDiscoverInProgress(true)
    await discoverAccounts()
    setDiscoverInProgress(false)
  }
  
  async function privateDeleteConnection() {
    setDeletionInProgress(true)
    await deleteConnection()
    setDeletionInProgress(false)
  }

  return (
    <div className="containers tx-row-border">
      <div className="left-nowrap">
        <div className="font-medium ml-1">
          {connection.user.name != username &&
            <>{titlecase(connection.user.name)}'s </>
          }
          {connection.name ?? connection.plaid_item_id}
        </div>
        <div>{connection.plaid_accounts.length} Accounts</div>
      </div>
      <div className="right">
        <div>
          <Button variant="outline" size="icon" onClick={privateDiscoverAccounts} disabled={discoverInProgress || deletionInProgress}>
            {discoverInProgress ?
              <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
            :
              <Telescope className="h-4 w-4" />
            }
          </Button>
          <Button variant="outline" size="icon" className="ml-2" onClick={privateDeleteConnection} disabled={discoverInProgress || deletionInProgress}>
            {deletionInProgress ?
              <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
            :
              <Trash2 className="h-4 w-4" />
            }
          </Button>
        </div>
      </div>
    </div>
  )
}