import 'server-only'
import { cookies } from 'next/headers' 
 
export async function createSession(access_token: any) {
  const expiresAt = new Date(Date.now() + 30 * 60 * 1000)
  const cookieStore = await cookies()
 
  cookieStore.set('session', access_token, {
    httpOnly: true,
    secure: true,
    expires: expiresAt,
    sameSite: 'lax',
    path: '/',
  })
}