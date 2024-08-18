import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from app import main as app_main


def main():
    st.set_page_config(page_title="MGU Scraper", page_icon="./favicon.ico")

    with open("./config.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    name, authentication_status, username = authenticator.login(
        fields={
            "Form name": "Login",
            "Username": "Email",
            "Password": "Password",
            "Login": "Login",
        }
    )

    if authentication_status:
        st.write(f"Welcome **{name}**")
        authenticator.logout()
        app_main()
    elif authentication_status == False:
        st.error("Email/password is incorrect")
    elif authentication_status == None:
        st.warning("Please enter your email and password")


if __name__ == "__main__":
    main()
