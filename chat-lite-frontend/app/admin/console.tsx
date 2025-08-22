"use client"
import { getLLMs } from "./actions"
import { useEffect, useState, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { Separator } from "@/components/ui/separator"
import { Paperclip, Send } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import ComboBox from "@/components/ui/combobox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
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
import { Textarea } from "@/components/ui/textarea"

import moment from "moment";

export interface Pulled {
    id: string;
    name: string;
    last_modified: string;
    size: string
}

export interface Msg {
    id: string;
    role: string;
    content: string;
}



export default function Console(llm_info: any) {
    const [socketUrl, setSocketUrl] = useState('ws://localhost:8000/admin/ws')
    const [ollamStatus, setOllamaStatus] = useState("Offline")
    const [loginRequired, setLoginRequired] = useState("true")
    const [msg, setMsg] = useState("")
    const [msgList, setMsgList] = useState<Msg[]>([])
    const [llmList, setLlmList] = useState([])
    const [pulled, setPulled] = useState<Pulled[]>([])
    const [llm, setLlm] = useState("")

    const { sendMessage, lastMessage, readyState, sendJsonMessage, getWebSocket } = useWebSocket(socketUrl, { 
        onOpen: () => {
            // sendMessage("initiating stream")
            sendJsonMessage({"info": "system", "message": "initiating stream"})
        }, 
        onClose: () => setOllamaStatus("Offline"), 
        shouldReconnect: (closeEvent) => true, 
        onMessage: (event: WebSocketEventMap['message']) => {
            // sendMessage("continuing stream")
        },
    });

    useEffect(() => {
        const llmInfo = JSON.parse(llm_info.llm_info)
        setLlmList(llmInfo.available)
        setPulled(llmInfo["pulled"])
    }, [])

    useEffect(() => {
        console.log('login required')
        console.log(loginRequired)
        const new_settings = update_settings()
        console.log(new_settings)
    }, [loginRequired])

    useEffect(() => {
        console.log('llm')
        console.log(llm)
    }, [llm])

    useEffect(() => {
        if (lastMessage !== null) {
            console.log('received message')
            const data = JSON.parse(lastMessage.data)
            console.log(data)
            const ollama_status = data?.ollama_online ? "Online" : "Offline"
            const response = data?.response ? data.response : false
            if (response){
                const id = uuidv4();
                setMsgList([...msgList, {id: id, role: "system", content: response}])
            }
            setOllamaStatus(ollama_status)
        } else {
            setOllamaStatus("Offline")
        }
    }, [lastMessage]);

    const update_settings = useCallback(() => {
        console.log("update_settings await function from ./action to write to sqlite")
        return "updated"
    }, [loginRequired])

    const handleLlmChange = (value: string) => {
        setLlm(value)
    }

    async function send_prompt() {
        console.log("send_prompt")
        const id = uuidv4();
        setMsgList([...msgList, {id: id, role: "user", content: msg}])
        sendJsonMessage({"info": "input", "prompt": msg})
    }

    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];


    return (
        <div className="font-sans grid grid-rows-[20px_1fr_20px] min-h-screen p-8 pb-20 gap-16 sm:p-20">
            <header>
                <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight text-balance">Admin Dashboard</h1>
            </header>
            <main className="flex gap-[32px] row-start-2">
                <div className="flex-col w-1/3">
                    <div className="mb-2">
                        <p className="scroll-m-20 text-2xl tracking-tight text-balance">Status</p>
                        <Table className="w-md">
                            <TableHeader>
                                <TableRow className="hover:bg-transparent">
                                    <TableHead className="w-[100px]">Websocket Status</TableHead>
                                    <TableHead className="w-[100px]">Ollama Status</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                <TableRow className="hover:bg-transparent">
                                    <TableCell className="w-[100px]">{connectionStatus}</TableCell>
                                    <TableCell className="w-[100px]">{ollamStatus}</TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </div>
                    <div className="my-2">
                        <p className="scroll-m-20 text-2xl tracking-tight text-balance">Admin Settings</p>
                        <Table className="w-md">
                            <TableHeader>
                                <TableRow className="hover:bg-transparent">
                                    <TableHead className="w-[100px]">Login Required</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                <TableRow className="hover:bg-transparent">
                                    <TableCell className="w-[100px]">
                                        <Select defaultValue={loginRequired} onValueChange={(val) => setLoginRequired(val)}>
                                            <SelectTrigger className="w-[180px]">
                                                <SelectValue/>
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="true">True</SelectItem>
                                                <SelectItem value="false">False</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </div>
                    <div className="my-2">
                        <p className="scroll-m-20 text-2xl tracking-tight text-balance">LLM Settings</p>
                        <Table className="w-md">
                            <TableHeader>
                                <TableRow className="hover:bg-transparent">
                                        <TableHead className="w-[100px]">Select LLM</TableHead>
                                        <TableHead className="w-[100px]">Options</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                <TableRow className="hover:bg-transparent">
                                    <TableCell className="w-[100px]">
                                        <ComboBox onValueChange={handleLlmChange} items={llmList} list_type={"LLM"} />
                                    </TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </div>
                </div>

                <div id="chat-box" className="flex-col w-2/3">
                    <div id="chat-window" className="h-full bg-card text-card-foreground flex flex-col gap-6 p-6 rounded-xl border shadow-sm">
                        <div id="messages" className="h-3/4 border rounded">
                            {msgList.reverse().map(m => {
                                return (
                                    <div key={m.id}>{m.content}</div>
                                )
                            })}
                        </div>
                        <div id="input" className="h-1/4 border rounded">
                            <div className="flex h-full relative">
                                <Textarea onChange={(e) => setMsg(e.target.value)} className="resize-none" placeholder="Ask a question..." />
                                <div className="text-slate-400 absolute right-0 bottom-0 flex gap-2 m-1">
                                    <Paperclip></Paperclip>
                                    <Send onClick={send_prompt}></Send>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
            <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">

            </footer>
        </div>
    );
}