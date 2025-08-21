import Console from './console'
import { verifyLocation } from './actions'
import { redirect } from 'next/navigation'

export default async function Admin() {
  const verified = await verifyLocation()

  if (verified) {
    return <Console />
  } else {
    redirect('/')
  }
}
