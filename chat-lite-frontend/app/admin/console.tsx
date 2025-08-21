"use client"
import { verifyLocation } from "./actions"
import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ColumnDef } from "@tanstack/react-table"
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import moment from "moment";

export default function Console() {
    const [socketUrl, setSocketUrl] = useState('ws://localhost:8000/admin/ws');
    const [currentTime, setCurrentTime] = useState("")
    const [ollamStatus, setOllamaStatus] = useState("")

    const { sendMessage, lastMessage, readyState, sendJsonMessage, getWebSocket } = useWebSocket(socketUrl, {onOpen: () => console.log('opened'), shouldReconnect: (closeEvent) => true,});

    useEffect(() => {
        setInterval(() => sendMessage(""), 3000)
        
    }, []);

    useEffect(() => {
        if (lastMessage !== null) {
            const data = JSON.parse(lastMessage.data)
            const ollama_status = data.ollama_online ? "Online" : "Offline"
            setOllamaStatus(ollama_status)
        }
    }, [lastMessage]);

    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];


    return (
        <div className="font-sans grid grid-rows-[20px_1fr_20px] min-h-screen p-8 pb-20 gap-16 sm:p-20">
            <main className="flex flex-col gap-[32px] row-start-2">
                <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight text-balance">Admin Dashboard</h1>
                <Table className="w-md">
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[100px]">Websocket Status</TableHead>
                            <TableHead className="w-[100px]">Ollama Status</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        <TableRow>
                            <TableCell className="w-[100px]">{connectionStatus}</TableCell>
                            <TableCell className="w-[100px]">{ollamStatus}</TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </main>
            <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">

            </footer>
        </div>
    );
}