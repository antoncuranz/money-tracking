"use client"

import {Button} from "@/components/ui/button.tsx";
import {Hammer, LinkIcon, LoaderCircle} from "lucide-react";
import React, {useCallback, useEffect, useState} from "react";
import {usePlaidLink} from "react-plaid-link";
import {useRouter} from "next/navigation";

const PlaidLinkButton = ({updateId, onDone}: {
  updateId?: number,
  onDone?: () => void
}) => {
  const [inProgress, setInProgress] = useState(false)
  const [token, setToken] = useState<string|null>(null);
  
  const router = useRouter();

  const createLinkToken = useCallback(async () => {
    const url = "/api/import/plaid/create_link_token" + (updateId ? `?update_id=${updateId}` : "");
    const response = await fetch(url, {method: "POST"});
    const data = await response.json();
    setToken(data.link_token);
  }, [updateId]);
  
  useEffect(() => {
    if (token == null) {
      createLinkToken();
    }
  }, [token, createLinkToken]);

  const onSuccess = useCallback(async (publicToken: string) => {
    setInProgress(true);
    if (!updateId) {
      await fetch("/api/import/plaid/exchange_token?public_token=" + publicToken, {
        method: "POST",
        headers: {"Content-Type": "application/json"}
      });
    }
    setInProgress(false)
    onDone?.()
    router.refresh()
  }, [updateId, onDone, router]);
  
  const onExit = useCallback(() => {
    setInProgress(false)
  }, []);

  const { open, ready } = usePlaidLink({token, onSuccess, onExit});
  
  const isUpdate = !!updateId;

  return (
    <Button size="sm" className="h-8 gap-1 mt-0 self-end" onClick={() => {setInProgress(true); open()}} disabled={!ready || inProgress}>
      { inProgress ?
        <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
      :
        isUpdate ? <Hammer className="h-3.5 w-3.5"/> : <LinkIcon className="h-3.5 w-3.5"/>
      }
      <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
      {isUpdate ? "Repair" : "Plaid Link"}
      </span>
    </Button>
  )
}

export default PlaidLinkButton
