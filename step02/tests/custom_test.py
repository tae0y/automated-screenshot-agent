from src.custom import login, logout

def test_login_should_not_raise():
    try:
        login()
    except Exception as e:
        assert False, f"login() raised an exception: {e}"

def test_logout_should_not_raise():
    try:
        logout()
    except Exception as e:
        assert False, f"logout() raised an exception: {e}"
