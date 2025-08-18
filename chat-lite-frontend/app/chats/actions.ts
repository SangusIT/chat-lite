'use server'
import { cookies } from 'next/headers'

export async function getSession() {
  const access_token = (await cookies()).get('session')?.value
  const myHeaders = new Headers();
    myHeaders.append("accept", "application/json");
    myHeaders.append("Authorization", `Bearer ${access_token}`);

    const chats = await fetch("http://localhost:8000/chats/", {
    method: "GET",
    headers: myHeaders,
    redirect: "follow"
    })
    .then((response) => response.json())
    .then((result) => {
        return result
    })
    .catch((error) => console.error(error));
  return chats
}

export async function deleteSession() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
}