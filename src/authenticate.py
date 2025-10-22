import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from app import main as app_main


def main():
    st.set_page_config(page_title="MGU Scraper", page_icon="./favicon.png")

    with open("./config.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f"Welcome **{st.session_state['name']}**")
        app_main()
    elif st.session_state["authentication_status"] is False:
        st.error("Email/password is incorrect")
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your email and password")


if __name__ == "__main__":
    main()
