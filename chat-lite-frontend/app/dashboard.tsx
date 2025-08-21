"use client"
import { getSession } from "./actions"
import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ColumnDef } from "@tanstack/react-table"

export type Chat = {
  name: string
}

export default function Dashboard() {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  const [inputMessage, setInputMessage] = useState("");
  
  // const sesH = getSession();
  // console.log('sesH')
  // console.log(sesH)

  

  useEffect(() => {
    console.log('loaded')
    // getSession()
    //   .then((response) => {
    //     if (response) {
    //       if (response.detail?.token_invalid) {
    //         router.push('/login')
    //       } else {
    //         console.log(response)
            
    //       }
    //     }
    //   })
    //   .catch(err => console.log(err))
  }, [])

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2">
        <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight text-balance">Home</h1>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">

      </footer>
    </div>
  );
}
