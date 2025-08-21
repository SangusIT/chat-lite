import { getSession } from "./actions"
import { redirect } from 'next/navigation'
import Dashboard from "./dashboard"

export default async function Home() {
  const session = await getSession();
  if (session?.detail?.token_invalid) {
    redirect('/login')
  } else {
    return <Dashboard />
  }
}
