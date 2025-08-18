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

export default function Home() {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  const [inputMessage, setInputMessage] = useState("");

  

  useEffect(() => {
    console.log('loaded')
    getSession()
      .then((response) => {
        if (response) {
          if (response.detail?.token_invalid) {
            router.push('/login')
          } else {
            console.log(response)
            // try {
            //   const ws = new WebSocket("wss://localhost:8000/ws");

            //   ws.onopen = () => {
            //     console.log("WebSocket connection established");
            //     // setSocket(ws);
            //   };

            //   // ws.onmessage = (event) => {
            //   //   setMessages((prevMessages) => [...prevMessages, event.data]);
            //   // };

            //   ws.onclose = () => {
            //     console.log("WebSocket connection closed");
            //     setSocket(null); // Clear socket on close
            //   };

            //   ws.onerror = (error) => {
            //     console.log("WebSocket error: ", error);
            //   };

            //   return () => {
            //     ws.close(); // Clean up on component unmount
            //   }; 
            // } catch (error) {
            //   console.log(error)
            // }
            // const {
            //   sendMessage,
            //   sendJsonMessage,
            //   lastMessage,
            //   lastJsonMessage,
            //   readyState,
            //   getWebSocket,
            // } = useWebSocket(socketUrl, {
            //   onOpen: () => console.log('opened'),
            //   //Will attempt to reconnect on all close events, such as server shutting down
            //   shouldReconnect: (closeEvent) => true,
            // });
            
          }
        }
      })
      .catch(err => console.log(err))
  }, [])

  // const sendMessage = () => {
  //       if (socket && inputMessage.trim() !== "") {
  //         socket.send(inputMessage);
  //         setInputMessage("");
  //       }
  //     };

  // const handleConnect = useCallback(() => {
  //   console.log('calling ws')
  //   useWebSocket(socketUrl, {
  //     onOpen: () => console.log('opened'),
  //     //Will attempt to reconnect on all close events, such as server shutting down
  //     shouldReconnect: (closeEvent) => true,
  //   })
  // }, [])

  // const connectionStatus = {
  //   [ReadyState.CONNECTING]: 'Connecting',
  //   [ReadyState.OPEN]: 'Open',
  //   [ReadyState.CLOSING]: 'Closing',
  //   [ReadyState.CLOSED]: 'Closed',
  //   [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  // }[readyState];

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start w-1/3">
        <h1 className="scroll-m-20 text-center text-4xl font-extrabold tracking-tight text-balance">Home</h1>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">

      </footer>
    </div>
  );
}
