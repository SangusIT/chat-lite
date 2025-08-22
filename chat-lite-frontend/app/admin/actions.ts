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

export async function getLLMs() {
    const response = await fetch('http://localhost:8000/ollama/all_info');
    if (response.ok && response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let result = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            result += decoder.decode(value, { stream: true });
        }
        return result
    }
}