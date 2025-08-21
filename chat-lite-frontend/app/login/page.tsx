"use client"
import { setSession } from "./actions"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from 'react'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useRouter, useSearchParams, redirect } from 'next/navigation'

export default function Register() {
  const router = useRouter()
  const [regError, setRegError] = useState("")
  const [userLogin, setUserLogin] = useState(true);

  useEffect(() => {

  }, [])

  const formSchema = z.union([
    z.object({
      username: z
        .string()
        .min(8, { message: "Username must be filled in" })
        .optional(),
      email: z
        .email()
        .min(1, { message: "Email must be filled in" }),
      password: z
        .string()
        .min(8, { message: "Password must be at least 8 characters long" })
        .regex(/[A-Z]/, { message: "Password must contain at least one uppercase letter" })
        .regex(/[a-z]/, { message: "Password must contain at least one lowercase letter" })
        .regex(/[0-9]/, { message: "Password must contain at least one number" })
        .regex(/[^a-zA-Z0-9]/, { message: "Password must contain at least one special character" })
    }),
    z.object({
      username: z
        .string()
        .min(8, { message: "Username must be filled in" }),
      email: z
        .email()
        .min(1, { message: "Email must be filled in" })
        .optional(),
      password: z
        .string()
        .min(8, { message: "Password must be at least 8 characters long" })
        .regex(/[A-Z]/, { message: "Password must contain at least one uppercase letter" })
        .regex(/[a-z]/, { message: "Password must contain at least one lowercase letter" })
        .regex(/[0-9]/, { message: "Password must contain at least one number" })
        .regex(/[^a-zA-Z0-9]/, { message: "Password must contain at least one special character" })
    })
  ])

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  })

  async function signIn(username: string, password: string) {
    const myHeaders = new Headers();
    myHeaders.append("accept", "application/json");
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");

    const urlencoded = new URLSearchParams();
    urlencoded.append("grant_type", "password");
    urlencoded.append("username", username);
    urlencoded.append("password", password);
    fetch("http://localhost:8000/users/token", { method: "POST", body: urlencoded, headers: myHeaders })
      .then((response) => response.json())
      .then((result) => {
        setSession(result)
          .then(res => {
            router.push('/')
          })
          .catch(err => {
            console.error(err)
          })
      })
      .catch((error) => console.error(error));
  }

  async function onSubmit(values: z.infer<typeof formSchema>) {
    signIn(values.username, values.password)
  }

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start w-1/3">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 w-full">
            {userLogin ?
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input type="username" placeholder="Username" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              :
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="Email" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            }
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="Password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormDescription>
              <a href="#" onClick={(e) => {
                e.preventDefault()
                form.clearErrors()
                setUserLogin(!userLogin)
              }}>Login with {userLogin ? "Email" : "Username"}</a>
            </FormDescription>
            <Button type="submit">Submit</Button>
          </form>
        </Form>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        {regError != "" ?
          <Alert variant="destructive">
            <AlertTitle>Problem with registration.</AlertTitle>
            <AlertDescription>
              {regError}
            </AlertDescription>
          </Alert>
          : ""}
      </footer>
    </div>
  );
}
