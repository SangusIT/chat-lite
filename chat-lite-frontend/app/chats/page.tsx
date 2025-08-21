"use client"
import { getSession } from "./actions"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ColumnDef } from "@tanstack/react-table"

export type Chat = {
  name: string
}

export default function chats() {
  const router = useRouter();
  const [chats, setChats] = useState<[]>([])
  const sesH = getSession();
  console.log('sesH')
  console.log(sesH)

  useEffect(() => {
    console.log('loaded')
    getSession()
      .then((response) => {
        if (response) {
          if (response.detail?.token_invalid) {
            router.push('/login')
          } else {
            console.log(response)
            setChats(response)
          }
        }
      })
      .catch(err => console.log(err))
  }, [])

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2">
        <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight text-balance">Chats</h1>
        {chats.map((item: any, index) => (
          <div key={index} data-name={item.name}>
            <Separator />
          </div>
        ))}
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">

      </footer>
    </div>
  );
}
