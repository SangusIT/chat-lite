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
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start w-1/3">
        <h1 className="scroll-m-20 text-center text-4xl font-extrabold tracking-tight text-balance">Home</h1>
        {chats.map((item: any, index) => (
          <div key={index} data-name={item.name}>
            {/* <div className="grid items-center gap-4 px-4 py-5 md:grid-cols-4">
                <div className="order-2 flex items-center gap-2 md:order-none">
                  <span className="flex h-14 w-16 shrink-0 items-center justify-center rounded-md bg-muted">
                    {item.icon}
                  </span>
                  <div className="flex flex-col gap-1">
                    <h3 className="font-semibold">{item.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {item.category}
                    </p>
                  </div>
                </div>
                <p className="order-1 text-2xl font-semibold md:order-none md:col-span-2">
                  {item.description}
                </p>
                <Button variant="outline" asChild>
                  <a
                    className="order-3 ml-auto w-fit gap-2 md:order-none"
                    href={item.link}
                  >
                    <span>View project</span>
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </Button>
              </div> */}
            <Separator />
          </div>
        ))}
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">

      </footer>
    </div>
  );
}
