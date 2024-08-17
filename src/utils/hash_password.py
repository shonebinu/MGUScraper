import streamlit_authenticator as stauth

plain_passwords = ["abc", "strong_password"]
hashed_passwords = stauth.Hasher(plain_passwords).generate()

print(hashed_passwords)
