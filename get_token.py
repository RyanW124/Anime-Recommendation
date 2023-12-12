import secrets, requests

def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]

code_verifier = code_challenge = get_new_code_verifier()
client_id = input("Client ID: ")

# print(code_verifier)
url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={client_id}&code_challenge={code_verifier}'
print(url)

payload = {
    'client_id': client_id,
    'client_secret': input("Client secret: "),
    'code': input("Auth code (click on the url above): "),  # ask the user to input the auth code they got and insert it here
    'code_verifier': code_verifier,
    'grant_type': "authorization_code",
}
with requests.Session() as session:
    response = session.post('https://myanimelist.net/v1/oauth2/token', payload).json()
with open("tokens.txt", "w") as f:
    f.write(response["access_token"]+"\n"+response["refresh_token"])