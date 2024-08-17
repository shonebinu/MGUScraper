import argparse
import streamlit_authenticator as stauth


def main():
    parser = argparse.ArgumentParser(
        description="Hash passwords using Streamlit Authenticator."
    )
    parser.add_argument("passwords", nargs="+", help="List of passwords to hash")

    args = parser.parse_args()
    plain_passwords = args.passwords

    hashed_passwords = stauth.Hasher(plain_passwords).generate()

    print(hashed_passwords)


if __name__ == "__main__":
    main()
