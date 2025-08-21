'use server'

export async function verifyLocation() {
    const authorized = await fetch("http://localhost:8000/admin/dashboard", {
        method: "GET",
        redirect: "follow"
    })
    .then((response) => {
        if (!response.ok)
            return false
        return response.json()
    })
    .then((result) => result)
    .catch((error) => console.error(error));
    return authorized
}