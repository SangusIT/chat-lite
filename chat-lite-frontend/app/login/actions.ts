'use server'
import { createSession } from '@/lib/session'

export async function setSession(result: any) {
  await createSession(result['access_token'])
}