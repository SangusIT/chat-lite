import Console from './console'
import { verifyLocation, getLLMs } from './actions'
import { redirect } from 'next/navigation'

export default async function Admin() {
  const verified = await verifyLocation()
  const llmDetails = await getLLMs()

  if (verified) {
    return <Console llm_info={llmDetails} />
  } else {
    redirect('/')
  }
}
