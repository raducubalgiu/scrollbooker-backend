import httpx
import os

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")

async def send_verification_email(to_email: str, verify_link: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": f"ScrollBooker <{FROM_EMAIL}>",
                "to": [to_email],
                "subject": "Verifica-ti adresa de email",
                "html": f"""
                <h2>Bun venit pe ScrollBooker.</h2>
                <p>Da click mai jos pentru a-ti valida adresa de email</p>
                <a href="{verify_link}">Confirma emailul</a>
                <p>Daca nu ai creat acest cont, ignora acest email.</p>    
                """
            }
        )
        response.raise_for_status()