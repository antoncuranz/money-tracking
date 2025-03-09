"use client"

import {Button} from "@/components/ui/button.tsx";
import {LinkIcon, LoaderCircle} from "lucide-react";
import React, {useCallback, useEffect, useState} from "react";
import {usePlaidLink} from "react-plaid-link";

const PlaidLinkButton = () => {
  const [inProgress, setInProgress] = useState(false)
  const [token, setToken] = useState<string|null>(null);

  const createLinkToken = useCallback(async () => {
    const response = await fetch("/api/import/plaid/create_link_token", {method: "POST"});
    const data = await response.json();
    setToken(data.link_token);
  }, []);
  
  useEffect(() => {
    if (token == null) {
      createLinkToken();
    }
  }, [token, createLinkToken]);

  const onSuccess = useCallback(async (publicToken: string) => {
    setInProgress(true);
    await fetch("/api/import/plaid/exchange_token?public_token=" + publicToken, {
      method: "POST",
      headers: {"Content-Type": "application/json"}
    });
    setInProgress(false)
    // router.refresh()
  }, []);
  
  const onExit = useCallback(() => {
    setInProgress(false)
  }, []);

  const { open, ready } = usePlaidLink({token, onSuccess, onExit});
  
  return (
    <Button size="sm" className="h-8 gap-1" onClick={() => {setInProgress(true); open()}} disabled={!ready || inProgress}>
      { inProgress ?
        <LoaderCircle className="h-3.5 w-3.5 animate-spin"/>
      :
        <LinkIcon className="h-3.5 w-3.5"/>
      }
      <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
      Plaid Link
      </span>
    </Button>
  )
}

export default PlaidLinkButton